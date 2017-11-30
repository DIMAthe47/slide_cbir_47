import random, sys

from PIL import Image
from PyQt5 import QtGui
import numpy as np
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, QPointF, QRectF, QEvent
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QRubberBand, QLabel, QApplication, QMessageBox, QWidget, QScrollArea, QVBoxLayout, \
    QSizePolicy, QHBoxLayout, QSlider, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsSceneWheelEvent, \
    QGraphicsEllipseItem, QGraphicsItemGroup
import openslide
from PIL.ImageQt import ImageQt
import time

from GraphicsTIle import GraphicsTile
from SelectedRect import SelectedRect


class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start


def pilimage_to_array(pilimage):
    pilimage.show()

    with Timer() as t:
        im_arr = np.fromstring(pilimage.tobytes(), dtype=np.uint8)
        im_arr = im_arr.reshape((pilimage.size[1], pilimage.size[0], len(pilimage.getbands())))
    img = Image.fromarray(im_arr)
    img.show()
    print("fromstring : {}".format(t.interval))
    return im_arr


def matrix_to_pixmap(image_matrix):
    with Timer() as t:
        if image_matrix.shape[2] == 4:
            img_format = QtGui.QImage.Format_RGBA8888
        else:
            img_format = QtGui.QImage.Format_RGB8888
        print("img_format: {}".format(img_format))
        qimg = QtGui.QImage(image_matrix, image_matrix.shape[1], image_matrix.shape[0], img_format)
    print("QtGui.QImage(image_matrix,  : {}".format(t.interval))
    with Timer() as t:
        qpm = QtGui.QPixmap.fromImage(qimg)
    print("QtGui.QPixmap.fromImage(qimg) : {}".format(t.interval))
    return qpm


class SlideViewer3(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.view = QGraphicsView()
        # self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        print(self.setMouseTracking(True))

        self.setLayout(layout)

        self.level_label = QLabel()
        layout.addWidget(self.level_label)

        # self.view.installEventFilter(self)
        # self.installEventFilter(self)
        self.view.viewport().installEventFilter(self)

        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.mouse_press_view = QPoint()
        self.rects = []

    def setSlide(self, slide_path):
        self.slide = openslide.OpenSlide(slide_path)
        self.reset_slide_params()
        self.tiles_pyramid_models = []
        self.generate_tiles_for_level(0, (500, 500), False)
        self.generate_tiles_for_level(1, (500, 500), False)
        self.generate_tiles_for_level(2, (500, 500), True)
        self.last_mouse_pos_scene = QPointF(0, 0)
        self.mouse_view_diff_scene = QPointF(0, 0)
        self.update_scale(1)
        self.view.fitInView(self.scene.sceneRect())
        print(self.view.mapToScene(self.view.rect()).boundingRect())

    def eventFilter(self, qobj: 'QObject', event: 'QEvent'):
        # print(event)
        if isinstance(event, QGraphicsSceneWheelEvent):
            print("QGraphicsSceneWheelEvent", "eventFilter", qobj, event)
            return True
        elif isinstance(event, QWheelEvent):
            # print("QWheelEvent", "eventFilter", qobj, event)
            self.last_mouse_pos_scene = self.view.mapToScene(event.pos())
            self.last_rect_scene = self.view.mapToScene(self.view.viewport().pos())

            self.mouse_view_diff_scene = self.view.mapToScene(event.pos()) - self.view.mapToScene(
                self.view.viewport().rect().center())
            # print("eventFilter", event.pos(), "->", self.last_mouse_pos_scene)
            print("eventFilter last_rect_scene", self.view.viewport().pos(), "->", self.last_rect_scene)
            print("diff", self.mouse_view_diff_scene)
            # чтобы колёсико отвечало только за зум, а не за скроллинг
            self.process_view_port_wheel_event(event)
            return True
        elif isinstance(event, QMouseEvent):
            if event.button() == Qt.LeftButton:
                if event.type() == QEvent.MouseButtonPress:
                    self.mouse_press_view = QPoint(event.pos())
                    self.rubber_band.setGeometry(QRect(self.mouse_press_view, QSize()))
                    self.rubber_band.show()
                    return True
                if event.type() == QEvent.MouseButtonRelease:
                    self.rubber_band.hide()
                    self.add_rect()
                    return True
            elif event.type() == QEvent.MouseMove:
                if not self.mouse_press_view.isNull():
                    self.rubber_band.setGeometry(QRect(self.mouse_press_view, event.pos()).normalized())
                    return True

        return False

    def add_rect(self):
        pos = self.rubber_band.pos() - self.view.pos()
        pos_scene = self.view.mapToScene(pos)
        rect = self.rubber_band.rect()
        rect_scene = self.view.mapToScene(rect).boundingRect()
        downsample = self.get_current_downsample()
        pos_0 = pos_scene * downsample
        rect_width_0 = rect_scene.width() * downsample
        rect_height_0 = rect_scene.height() * downsample
        for tiles_pyramid_model in self.tiles_pyramid_models:
            downsample = self.get_downsample(tiles_pyramid_model["level"])
            rect_real_sized = QRect(pos_0.x() / downsample, pos_0.y() / downsample, rect_width_0 / downsample,
                                    rect_height_0 / downsample)
            item = SelectedRect(rect_real_sized, 1)
            tiles_pyramid_model["tiles_graphics_group"].removeFromGroup(tiles_pyramid_model["selected_graphics_rect"])
            tiles_pyramid_model["tiles_graphics_group"].addToGroup(item)
            tiles_pyramid_model["selected_graphics_rect"] = item
        self.view.invalidateScene()
        self.update()
        self.view.viewport().update()

    def sceneEvent(self, event):
        print("scene event", event)

    def reset_slide_params(self):
        start_downsample_factor = 16
        self.zoom_factor = 1 / start_downsample_factor
        self.last_mouse_pos = QPoint(0, 0)

    def update_scale(self, zoom):
        self.zoom_factor *= zoom
        downsample = 1 / self.zoom_factor
        best_level = self.slide.get_best_level_for_downsample(downsample)
        # print("best_level", best_level)

        level_downsample = self.slide.level_downsamples[best_level]
        new_zoom_factor = 1 / level_downsample
        # self.zoom_factor = new_zoom_factor
        new_scale = self.zoom_factor / new_zoom_factor
        # print("new_scale", new_scale)
        new_mouse_pos_scene = self.last_mouse_pos_scene * self.get_level_relative_scale(best_level)
        # self.scene.addRect(new_mouse_pos_scene.x(), new_mouse_pos_scene.y(), 20, 20)
        # self.scene.addRect(0, 0, 100, 100)
        # self.scene.addText("Origin")

        self.view.resetTransform()
        # dxy = new_mouse_pos_scene - self.last_mouse_pos_scene
        # self.view.horizontalScrollBar().setValue(self.view.horizontalScrollBar().value() + dxy.x())
        # self.view.verticalScrollBar().setValue(self.view.verticalScrollBar().value() + dxy.y())

        self.scene.setSceneRect(self.get_scene_rect_for_level(best_level))

        print(new_scale)
        self.view.scale(new_scale, new_scale)

        new_center_on = new_mouse_pos_scene
        # new_center_on = new_mouse_pos_scene - self.mouse_view_diff_scene
        print("new_center_on", new_center_on)
        self.view.centerOn(new_center_on)

        # self.view.translate(3000,1000)

        new_mouse_pos_global = self.view.mapToGlobal(self.view.mapFromScene(new_mouse_pos_scene))
        # self.view.cursor().setPos(new_mouse_pos_global)

        self.prev_best_level = best_level
        self.set_visible_level(best_level)

        # self.scene.invalidate()
        self.level_label.setText("level: {} ({}, {})".format(best_level, *self.get_level_size(best_level)))

    def process_view_port_wheel_event(self, event: QWheelEvent):
        zoom_in = 1.25
        zoom_out = 1 / zoom_in

        # self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.view.setResizeAnchor(QGraphicsView.NoAnchor)

        zoom_ = None
        if event.angleDelta().y() > 0:
            zoom_ = zoom_in
        elif event.angleDelta().y() < 0:
            zoom_ = zoom_out

        if (zoom_):
            self.mouse_wheel_pos_scene = self.view.mapToScene(event.pos())
            # print("wheelEvent", event.pos(), "->", self.mouse_wheel_pos_scene)
            self.update_scale(zoom_)

        event.accept()

    # def mousePressEvent(self, event: QtGui.QMouseEvent):
    #     pos = self.view.mapToScene(event.pos() - self.view.pos())
    #     self.scene.addRect(pos.x(), pos.y(), 50, 50)
    #     print(pos)


    def pilimage_to_pixmap(self, pilimage):
        # pilimage.show()
        qim = ImageQt(pilimage)
        pix = QtGui.QPixmap.fromImage(qim)
        return pix

    def get_view_size(self):
        size = self.view.size()
        return (size.width(), size.height())

    def set_visible_level(self, level):
        for tile_pyramid_model in self.tiles_pyramid_models:
            if tile_pyramid_model["level"] == level:
                tile_pyramid_model["tiles_graphics_group"].setVisible(True)
            else:
                tile_pyramid_model["tiles_graphics_group"].setVisible(False)

    def get_visible_level(self):
        for tile_pyramid_model in self.tiles_pyramid_models:
            if tile_pyramid_model["tiles_graphics_group"].isVisible():
                return tile_pyramid_model["level"]

    def get_level_relative_scale(self, new_level):
        level = self.get_visible_level()
        level_relative_scale = self.get_downsample(level) / self.get_downsample(new_level)
        return level_relative_scale

    def get_downsample(self, level):
        return self.slide.level_downsamples[level]

    def get_level_size(self, level):
        return self.slide.level_dimensions[level]

    def get_current_downsample(self):
        return self.get_downsample(self.get_visible_level())

    def get_scene_rect_for_level(self, level):
        size_ = self.get_level_size(level)
        rect = QRectF(-size_[0] / 2, -size_[1] / 2, size_[0], size_[1])
        return rect

    def generate_tiles_for_level(self, level, tile_size, visible):
        tiles_rects = []
        x = 0
        y = 0
        tiles_grid_size = self.slide.level_dimensions[level]
        x_size = tiles_grid_size[0]
        y_size = tiles_grid_size[1]
        x_step = tile_size[0]
        y_step = tile_size[1]
        while y < y_size:
            while x < x_size:
                w = x_step
                if x + w >= x_size:
                    w = x_size - x
                h = y_step
                if y + h >= y_size:
                    h = y_size - y
                tiles_rects.append((x, y, w, h))
                x += x_step
            x = 0
            y += y_step

        print("tiles_rects", tiles_rects)
        print("tiles_grid_size", tiles_grid_size)
        # graphics_tiles_rects = []
        tiles_graphics_group = QGraphicsItemGroup()
        tiles_graphics = []
        downsample = self.slide.level_downsamples[level]
        for tile_rect in tiles_rects:
            # item=self.scene.addRect(tile_rect[0], tile_rect[1], tile_rect[2], tile_rect[3])
            item = GraphicsTile(tile_rect, self.slide, level, self.slide.level_downsamples[level])
            item.setPos(-tiles_grid_size[0] / 2, -tiles_grid_size[1] / 2)
            # item.setPos((tile_rect[0] - tiles_grid_size[0] / 2) * downsample,
            #             (tile_rect[1] - tiles_grid_size[1] / 2) * downsample)
            # item.setPos(tile_rect[0], tile_rect[1])
            # graphics_tiles_rects.append(item)
            tiles_graphics_group.addToGroup(item)
            # tiles_graphics.append(item)
        tiles_graphics_group.setVisible(visible)
        self.scene.addItem(tiles_graphics_group)
        tile_pyramid_model = {
            "level": level,
            "tiles_grid_size": tiles_grid_size,
            "tile_size": tile_size,
            "tiles_rects": tiles_rects,
            "tiles_graphics": tiles_graphics,
            "tiles_graphics_group": tiles_graphics_group,
            "selected_graphics_rect": None
        }
        self.tiles_pyramid_models.append(tile_pyramid_model)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    win = QWidget()
    win.setWindowTitle('Image List')
    win.setMinimumSize(500, 600)
    layout = QVBoxLayout()
    win.setLayout(layout)

    # dirpath = '/home/dimathe47/data/geo_tiny/Segm_RemoteSensing1/cropped/poligon_minsk_1_yandex_z18_train_0_0.jpg'
    # dirpath = '/home/dimathe47/data/geo_tiny/S/egm_RemoteSensing1/poligon_minsk_1_yandex_z18_train.jpg'
    # slide_path = '/home/dimathe47/Downloads/CMU-1-Small-Region.svs'
    # slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'
    slide_path = r'C:\Users\dmitriy\Downloads\JP2K-33003-1.svs'
    slideViewer = SlideViewer3()
    layout.addWidget(slideViewer)

    win.show()

    slideViewer.setSlide(slide_path)

    sys.exit(app.exec_())
