import random, sys
import json
from PIL import Image
from PyQt5 import QtGui
import numpy as np
from PyQt5.QtCore import QPoint, QRect, QSize, Qt, QPointF, QRectF, QEvent, QVariant
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QRubberBand, QLabel, QApplication, QMessageBox, QWidget, QScrollArea, QVBoxLayout, \
    QSizePolicy, QHBoxLayout, QSlider, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsSceneWheelEvent, \
    QGraphicsEllipseItem, QGraphicsItemGroup, QGridLayout, QGroupBox, QMainWindow, QAction, QGraphicsItem, \
    QAbstractScrollArea
import openslide
from PIL.ImageQt import ImageQt
import time

from GraphicsTIle import GraphicsTile
from SelectedRect import SelectedRect


def rect_to_str(rect):
    if isinstance(rect, QPolygonF):
        rect = rect.boundingRect()
    return "({},{},{},{})".format(rect.x(), rect.y(), rect.width(), rect.height())


def point_to_str(point: QPoint):
    return "({},{})".format(point.x(), point.y())


class Timer:
    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start


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

        # self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
        # self.view.setTransformationAnchor(QGraphicsView.AnchorViewCenter)


        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        # print(self.setMouseTracking(True))

        self.setLayout(layout)

        self.level_label = QLabel()
        self.selected_rect_label = QLabel()
        self.mouse_pos_scene_label = QLabel()
        self.mouse_pos_view_label = QLabel()
        self.view_rect_view_label = QLabel()
        self.view_rect_scene_label = QLabel()
        layout.addWidget(self.level_label)
        layout.addWidget(self.selected_rect_label)
        layout.addWidget(self.mouse_pos_scene_label)
        layout.addWidget(self.mouse_pos_view_label)
        layout.addWidget(self.view_rect_view_label)
        layout.addWidget(self.view_rect_scene_label)
        # self.horizontalGroupBox = QGroupBox("Selected rect")
        # grid_layout = QGridLayout()
        # layout.addWidget(self.horizontalGroupBox)
        # layout.addWidget(self.selected_rect_label)

        # grid_layout.addWidget(QLabel("rect pos:"), 0, 0)

        # self.pos_x_line_edit = QTextLine()
        # self.pos_y_line_edit = QTextLine()
        # grid_layout.addWidget(self.pos_x_line_edit, 0, 1)
        # grid_layout.addWidget(self.pos_y_line_edit, 0, 2)
        # grid_layout.addWidget(QLabel("rect size:"), 1, 0)

        # self.horizontalGroupBox.setLayout(grid_layout)

        # self.view.installEventFilter(self)
        # self.installEventFilter(self)
        self.view.viewport().installEventFilter(self)

        # def viewEventFilter():
        #     e = object()
        #     e.eventFilter = self.viewEventFilter
        #     return e

        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.mouse_press_view = QPoint()
        self.rects = []
        # self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def get_selected_rect_pilimg(self):
        if self.selected_rect_downsample:
            best_level = self.slide.get_best_level_for_downsample(self.selected_rect_downsample)
            best_level_downsample = self.get_downsample(best_level)
            w = int(self.selected_rect_size[0] / best_level_downsample)
            h = int(self.selected_rect_size[1] / best_level_downsample)
            x_0 = int(self.selected_rect_pos_0.x() + self.get_level_size(0)[0] / 2)
            y_0 = int(self.selected_rect_pos_0.y() + self.get_level_size(0)[1] / 2)
            selected_rect_pilimg = self.slide.read_region((x_0, y_0), best_level, (w, h))
            return selected_rect_pilimg
            # self.selected_rect_size = (rect_width_0, rect_height_0)
            #  = downsample

    def get_selected_rect(self):
        if self.selected_rect_downsample:
            best_level = self.slide.get_best_level_for_downsample(self.selected_rect_downsample)
            best_level_downsample = self.get_downsample(best_level)
            w = int(self.selected_rect_size[0] / best_level_downsample)
            h = int(self.selected_rect_size[1] / best_level_downsample)
            x_0 = int(self.selected_rect_pos_0.x() + self.get_level_size(0)[0] / 2)
            y_0 = int(self.selected_rect_pos_0.y() + self.get_level_size(0)[1] / 2)
            selected_rect_pilimg = self.slide.read_region((x_0, y_0), best_level, (w, h))
            return (x_0, y_0, w, h, best_level_downsample)

    def setSlide(self, slide_path):
        self.slide_path = slide_path
        self.slide = openslide.OpenSlide(slide_path)
        self.tiles_pyramid_models = []
        self.generate_tiles_for_level(0, (500, 500), False)
        self.generate_tiles_for_level(1, (500, 500), False)
        self.generate_tiles_for_level(2, (500, 500), True)
        self.last_mouse_pos_scene = QPointF(0, 0)
        self.mouse_view_diff_scene = QPointF(0, 0)
        self.last_mouse_pos = QPoint(0, 0)
        # self.start_downsample_factor = 32
        # self.zoom_factor = 1 / self.start_downsample_factor
        self.logical_zoom = 1
        self.level_relative_zoom = 1
        # view_size = self.view.size()
        # min_level_size = self.get_level_size(2)
        # self.zoom_factor = min((view_size.width() / min_level_size[0], view_size.height() / min_level_size[1]))
        # self.view.scale(0.2, 0.2)
        self.update_scale(QPoint(0, 0), 1)

        self.selected_rect_downsample = 1
        self.selected_rect_pos_0 = QPoint(0, 0)
        self.selected_rect_size = self.get_level_size(0)
        # self.view.fitInView(self.scene.sceneRect())
        print(self.view.mapToScene(self.view.rect()).boundingRect())

    def viewEventFilter(self, qobj: 'QObject', event: 'QEvent'):
        print(event)

    def updateLabels(self, event):
        self.mouse_pos_view_label.setText("mouse_pos_view" + point_to_str(event.pos()))
        self.mouse_pos_scene_label.setText("mouse_pos_scene" + point_to_str(self.view.mapToScene(event.pos())))
        self.view_rect_view_label.setText("view_rect_view" + rect_to_str(self.view.rect()))
        self.view_rect_scene_label.setText("view_rect_scene" + rect_to_str(self.view.mapToScene(self.view.rect())))

    def eventFilter(self, qobj: 'QObject', event: 'QEvent'):
        if isinstance(event, QGraphicsSceneWheelEvent):
            print("QGraphicsSceneWheelEvent", "eventFilter", qobj, event)
            return True
        elif isinstance(event, QWheelEvent):
            # print("QWheelEvent", "eventFilter", qobj, event)
            self.last_mouse_pos_scene = self.view.mapToScene(event.pos())
            self.last_rect_scene = self.view.mapToScene(self.view.viewport().pos())

            # print("eventFilter", event.pos(), "->", self.last_mouse_pos_scene)
            # print("eventFilter last_rect_scene", self.view.viewport().pos(), "->", self.last_rect_scene)
            # чтобы колёсико отвечало только за зум, а не за скроллинг
            self.process_view_port_wheel_event(event)
            self.updateLabels(event)
            return True
        elif isinstance(event, QMouseEvent):
            if event.button() == Qt.RightButton:
                if event.type() == QEvent.MouseButtonRelease:
                    # self.view.translate(500, 500)
                    print(self.view.mapToScene(self.view.rect().center()) - self.view.mapToScene(event.pos()))
                    self.updateLabels(event)
                    return True
            elif event.button() == Qt.LeftButton:
                if event.type() == QEvent.MouseButtonPress:
                    self.mouse_press_view = QPoint(event.pos())
                    self.rubber_band.setGeometry(QRect(self.mouse_press_view, QSize()))
                    self.rubber_band.show()
                    return True
                if event.type() == QEvent.MouseButtonRelease:
                    self.rubber_band.hide()
                    self.add_rect()
                    # self.view.translate(-500, -500)
                    self.updateLabels(event)
                    return True
            elif event.type() == QEvent.MouseMove:
                self.updateLabels(event)
                if not self.mouse_press_view.isNull():
                    self.rubber_band.setGeometry(QRect(self.mouse_press_view, event.pos()).normalized())

                return False

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
        self.selected_rect_pos_0 = pos_0
        self.selected_rect_size = (rect_width_0, rect_height_0)
        self.selected_rect_downsample = downsample
        for tiles_pyramid_model in self.tiles_pyramid_models:
            downsample = self.get_downsample(tiles_pyramid_model["level"])
            rect_real_sized = QRect(pos_0.x() / downsample, pos_0.y() / downsample, rect_width_0 / downsample,
                                    rect_height_0 / downsample)
            item = SelectedRect(rect_real_sized, 1)
            tiles_pyramid_model["tiles_graphics_group"].removeFromGroup(tiles_pyramid_model["selected_graphics_rect"])
            tiles_pyramid_model["tiles_graphics_group"].addToGroup(item)
            tiles_pyramid_model["selected_graphics_rect"] = item

        best_level = self.slide.get_best_level_for_downsample(self.selected_rect_downsample)
        best_level_downsample = self.get_downsample(best_level)
        w = int(self.selected_rect_size[0] / best_level_downsample)
        h = int(self.selected_rect_size[1] / best_level_downsample)
        self.selected_rect_label.setText(
            "selected_rect. pos: ({},{}), size: ({},{})".format(self.selected_rect_pos_0.x(),
                                                                self.selected_rect_pos_0.y(), w, h))
        self.view.invalidateScene()
        self.update()
        self.view.viewport().update()

    def sceneEvent(self, event):
        print("scene event", event)

    def get_current_level_downsample(self):
        best_level = self.slide.get_best_level_for_downsample(1 / self.logical_zoom)
        level_downsample = self.slide.level_downsamples[best_level]
        return level_downsample

    def set_scene_rect_for_current_level(self):
        best_level = self.slide.get_best_level_for_downsample(1 / self.logical_zoom)
        self.scene.setSceneRect(self.get_scene_rect_for_level(best_level))

    def set_visible_for_current_level(self):
        best_level = self.slide.get_best_level_for_downsample(1 / self.logical_zoom)
        level_downsample = self.slide.level_downsamples[best_level]
        self.set_visible_level(best_level)
        level_size = self.get_level_size(best_level)
        self.level_label.setText(
            "level: {} ({}, {}), level_downsample: {}".format(best_level, level_size[0], level_size[1],
                                                              level_downsample))

    def update_scale(self, mouse_pos: QPoint, zoom):
        old_level_downsample = self.get_current_level_downsample()
        self.logical_zoom *= zoom
        new_level_downsample = self.get_current_level_downsample()
        old_view_pos_scene = self.view.mapToScene(self.view.pos())
        old_mouse_pos_scene = self.view.mapToScene(mouse_pos) - old_view_pos_scene
        mouse_pos_scene = self.view.mapToScene(mouse_pos)
        view_pos_scene = self.view.mapToScene(self.view.rect().topLeft())

        if old_level_downsample == new_level_downsample:
            self.set_scene_rect_for_current_level()

        new_scale = zoom
        self.view.scale(new_scale, new_scale)
        self.level_relative_zoom *= new_scale

        new_view_pos_scene = self.view.mapToScene(self.view.pos())
        new_mouse_pos_scene = self.view.mapToScene(mouse_pos)
        new_mouse_pos_scene = self.view.mapToScene(mouse_pos) - new_view_pos_scene
        mouse_pos_delta = new_mouse_pos_scene - old_mouse_pos_scene
        view_delta = new_view_pos_scene - old_view_pos_scene
        pos_delta = mouse_pos_delta + view_delta
        # print("pos_delta", pos_delta.x())
        self.view.translate(pos_delta.x(), pos_delta.y())
        if old_level_downsample != new_level_downsample:
            new_view_pos_scene = self.view.mapToScene(self.view.rect().topLeft())
            level_scale_delta = 1 / (new_level_downsample / old_level_downsample)
            # a1 = (mouse_pos_scene - view_pos_scene) / level_scale_delta
            # shift_scene = mouse_pos_scene - a1
            shift_scene = new_view_pos_scene
            shift_scene *= level_scale_delta
            self.resetTransform()
            self.set_scene_rect_for_current_level()
            new_scale = self.level_relative_zoom * (new_level_downsample) / old_level_downsample
            self.view.scale(new_scale, new_scale)
            self.view.translate(-shift_scene.x(), -shift_scene.y())
            print("mouse_pos_scene", mouse_pos_scene)
            print("view_pos_scene", view_pos_scene)
            self.scene.addRect(
                QRectF(self.view.mapToScene(mouse_pos), self.view.mapToScene(mouse_pos) + QPointF(50, 50)))
            # self.zoom_for_level = 1 / 32

            self.level_relative_zoom = new_scale
            # self.logical_ = new_scale

        self.old_level_downsample = new_level_downsample
        self.set_visible_for_current_level()

    def resetTransform(self):
        print("view_pos before resetTransform:", self.view_pos_scene_str())
        print("dx before resetTransform:", self.view.transform().dx())
        print("horizontalScrollBar before resetTransform:", self.view.horizontalScrollBar().value())
        print("horizontalScrollBar singleStep before resetTransform:", self.view.horizontalScrollBar().singleStep())
        self.view.resetTransform()
        self.view.horizontalScrollBar().setValue(0)
        self.view.verticalScrollBar().setValue(0)
        print("view_pos after resetTransform:", self.view_pos_scene_str())
        print("dx after resetTransform:", self.view.transform().dx())
        print("horizontalScrollBar after resetTransform:", self.view.horizontalScrollBar().value())

    def view_pos_scene_str(self):
        return point_to_str(self.view.mapToScene(self.view.pos()))

    def view_pos_view_str(self):
        return point_to_str(self.view.pos())

    def process_view_port_wheel_event(self, event: QWheelEvent):
        zoom_in = 1.15
        zoom_out = 1 / zoom_in
        zoom_ = zoom_in if event.angleDelta().y() > 0 else zoom_out
        # print("wheelEvent", event.pos(), "->", self.mouse_wheel_pos_scene)
        self.update_scale(event.pos(), zoom_)
        self.updateLabels(event)
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
        # rect = QRectF(-size_[0] / 2, -size_[1] / 2, size_[0], size_[1])
        rect = QRectF(0, 0, size_[0], size_[1])
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
        downsample = self.slide.level_downsamples[level]
        for tile_rect in tiles_rects:
            # item=self.scene.addRect(tile_rect[0], tile_rect[1], tile_rect[2], tile_rect[3])
            downsample = self.slide.level_downsamples[level]
            item = GraphicsTile(tile_rect, self.slide, level, downsample)
            # item.setPos(-tiles_grid_size[0] / 2, -tiles_grid_size[1] / 2)
            # item.setScale(1 / self.slide.level_downsamples[level])
            # item.setScale(1 / downsample)
            tiles_graphics_group.addToGroup(item)
            # tiles_graphics_group.setScale(1 / downsample)
            # tiles_graphics_group.setScale(2)
        tiles_graphics_group.setVisible(visible)
        self.scene.addItem(tiles_graphics_group)
        tile_pyramid_model = {
            "level": level,
            "tiles_grid_size": tiles_grid_size,
            "tile_size": tile_size,
            "tiles_rects": tiles_rects,
            "tiles_graphics_group": tiles_graphics_group,
            "selected_graphics_rect": None
        }
        self.tiles_pyramid_models.append(tile_pyramid_model)


class SlieViewerMainWindow(QMainWindow):
    def __init__(self):
        super(SlieViewerMainWindow, self).__init__()
        self.setWindowTitle('Slide viewer')
        self.setMinimumSize(1000, 1000)
        # self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
        # self.view.setTransformationAnchor(QGraphicsView.AnchorViewCenter)

        noAnchorAction = QAction("NoAnchor", self)
        noAnchorAction.setCheckable(True)
        anchorViewCenterAction = QAction("AnchorViewCenter", self)
        anchorViewCenterAction.setCheckable(True)
        anchorUnderMouseAction = QAction("AnchorUnderMouse", self)
        anchorUnderMouseAction.setCheckable(True)

        noAnchorAction.triggered.connect(self.anchorActionFactory(QGraphicsView.NoAnchor, "NoAnchor"))
        anchorViewCenterAction.triggered.connect(
            self.anchorActionFactory(QGraphicsView.AnchorViewCenter, "AnchorViewCenter"))
        anchorUnderMouseAction.triggered.connect(
            self.anchorActionFactory(QGraphicsView.AnchorUnderMouse, "AnchorUnderMouse"))

        self.anchorActions = [noAnchorAction, anchorViewCenterAction, anchorUnderMouseAction]
        # searchAction.triggered.connect(self.onSearchAction)
        mainMenu = self.menuBar()
        acnchorModesMenu = mainMenu.addMenu('&anchor mode')
        acnchorModesMenu.addActions(self.anchorActions)

        restartAction = QAction("restart", self)
        restartAction.triggered.connect(self.restartHack)
        mainMenu.addAction(restartAction)

        # actionMenu.addAction(searchAction)
        # actionMenu.addAction(showQueryTileAction)
        self.slideViewer = SlideViewer3()
        self.setCentralWidget(self.slideViewer)

        noAnchorAction.trigger()

    def anchorActionFactory(self, anchorMode, anchorModeText):
        def onAction():
            self.slideViewer.view.setTransformationAnchor(anchorMode)
            for anchorModeAction in self.anchorActions:
                if anchorModeAction.text() == anchorModeText:
                    anchorModeAction.setChecked(True)
                else:
                    anchorModeAction.setChecked(False)

        return onAction

    def restartHack(self):
        slide_path = self.slideViewer.slide_path
        self.slideViewer = SlideViewer3()
        self.setCentralWidget(self.slideViewer)
        self.slideViewer.setSlide(slide_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SlieViewerMainWindow()
    # slide_path = '/home/dimathe47/Downloads/CMU-1-Small-Region.svs'
    slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'
    win.show()
    win.slideViewer.setSlide(slide_path)
    sys.exit(app.exec_())
