import random, sys

from PIL import Image
from PyQt5 import QtGui
import numpy as np
from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QRubberBand, QLabel, QApplication, QMessageBox, QWidget, QScrollArea, QVBoxLayout, \
    QSizePolicy, QHBoxLayout, QSlider, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsSceneWheelEvent, \
    QGraphicsEllipseItem
import openslide
from PIL.ImageQt import ImageQt
import time


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


class SlideViewer2(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()

        self.view = QGraphicsView()
        self.view.setRenderHint(QPainter.Antialiasing)
        # self.item = QGraphicsEllipseItem(-20, -10, 40, 20)
        # self.item.setZValue(5)


        self.view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.scene = QGraphicsScene()
        # self.scene.addItem(self.item)
        # self.scene.addRect(self.scene.sceneRect())
        self.view.setScene(self.scene)
        layout = QHBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.view.eventFilter = self.sceneEventFilter
        # self.view.eventFilter = self.sceneEventFilter

    def sceneEventFilter(self, graphicsitem, event):
        if isinstance(event, QGraphicsSceneWheelEvent):
            print("QGraphicsSceneWheelEvent", event.pos())
            pass
        if isinstance(event, QWheelEvent):
            # print(event.pos())
            # чтобы колёсико отвечало только за зум, а не за скроллинг
            self.last_mouse_pos = event.pos()
            # print("sceneEventFilter", event.pos())
            return True
        return False

    def pilimage_to_pixmap(self, pilimage):
        # pilimage.show()
        qim = ImageQt(pilimage)
        pix = QtGui.QPixmap.fromImage(qim)
        return pix

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = QPoint(event.pos())
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()

    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            rect = self.rubberBand.geometry().getRect()
            QMessageBox.information(self, "Image Viewer",
                                    "RubberBand geometry: %s." % str(rect))
            # self.rubberBand.hide()

    def setSlide(self, slide_path):
        self.slide = openslide.OpenSlide(slide_path)
        self.reset_slide_params()
        self.rereadTileIfNeed(1)
        self.zoom_factors = list(range(len(self.slide.level_dimensions)))
        # image = QImage(img_path)
        # if image.isNull():
        #     QMessageBox.information(self, "Image Viewer",
        #                             "Cannot load %s." % img_path)
        #     return
        # self.imageLabel.setPixmap(QPixmap.fromImage(image))
        # self.imageLabel.adjustSize()

    def rereadTileIfNeed(self, zoom_):
        # best_level = 2 - self.zoom_factor
        # best_level = self.slide.get_best_level_for_downsample(self.zoom_factor)
        scene_size = self.scene.sceneRect().size()
        print("zoom_factor", self.zoom_factor)
        print("scene_size", scene_size)
        best_level = self.slide.get_best_level_for_downsample(self.downsample_factor)
        if best_level != self.last_level:
            print("best_level", best_level)
            level_size = self.slide.level_dimensions[best_level]

            with Timer() as t:
                # if best_level<100:
                if best_level == 2:
                    # self.tile_matrix = self.slide.get_thumbnail(self.get_view_size())
                    # self.tile_matrix = self.slide.get_thumbnail((640, 480))
                    self.tile_matrix = self.slide.get_thumbnail((500, 500))
                else:
                    mouse_pos = self.view.mapToScene(self.last_mouse_pos)
                    lx = mouse_pos.x()
                    ly = mouse_pos.y()
                    rect_start_x = self.last_mouse_pos.x() - self.zoom_factor * self.view.size().width() / 2
                    rect_start_y = self.last_mouse_pos.y() - self.zoom_factor * self.view.size().height() / 2
                    print("rect_start_x", rect_start_x)
                    print("rect_start_y", rect_start_y)
                    rect = QRect(rect_start_x, rect_start_y,
                                 self.zoom_factor * self.view.size().width(),
                                 self.zoom_factor * self.view.size().height())
                    rect_scene = self.view.mapToScene(rect)
                    print("resc_scene", rect_scene.boundingRect())
                    sx = int(scene_size.width() / self.zoom_factor)
                    sy = int(scene_size.height() / self.zoom_factor)
                    # width_ratio = rect_scene.boundingRect().width() / self.graphics_pixmap.boundingRect().width()
                    # height_ratio = rect_scene.boundingRect().height() / self.graphics_pixmap.boundingRect().height()
                    width_ratio = self.slide.level_dimensions[best_level][
                                      0] / self.graphics_pixmap.boundingRect().width()
                    height_ratio = self.slide.level_dimensions[best_level][
                                       1] / self.graphics_pixmap.boundingRect().height()
                    # new_rect_scene_width = int(width_ratio * self.slide.level_dimensions[best_level][0])
                    # new_rect_scene_height = int(height_ratio * self.slide.level_dimensions[best_level][1])
                    new_rect_scene_width = int(width_ratio * self.view.size().width())
                    new_rect_scene_height = int(height_ratio * self.view.size().height())
                    print("width_ratio", width_ratio)
                    print("height_ratio", height_ratio)
                    print("new_rect_scene_width", new_rect_scene_width)
                    print("new_rect_scene_height", new_rect_scene_height)
                    # new_width=width_ratio.
                    # sw = scene_size.width()
                    # sh = scene_size.height()
                    # ix = int(level_size[0] * (lx) / (sw))
                    # iy = int(level_size[1] * (ly) / (sh))
                    # ix = int(level_size[0] * lx / (2 * scene_size.width()))
                    # iy = int(level_size[1] * ly / (2 * scene_size.height()))
                    # ix = int(level_size[0] * sx / (2 * self.get_view_size()[0]))
                    # iy = int(level_size[1] * sy / (2 * self.get_view_size()[1]))
                    # sx2 = int(level_size[0] / self.zoom_factor)
                    # sy2 = int(level_size[1] / self.zoom_factor)

                    sx2 = new_rect_scene_width
                    sy2 = new_rect_scene_height
                    # sx2 = 5000
                    # sy2 = 5000
                    ix, iy = 0, 0

                    print("lx", lx, "ly", ly)
                    # print("ix", ix, "iy", iy)
                    # print("sx", sx, "sy", sy)
                    # print("sw", sw, "sh", sh)
                    # print("sx2", sx2, "sy2", sy2)
                    # self.tile_matrix = self.slide.read_region((ix, iy), best_level, self.get_view_size())
                    # self.tile_matrix = self.slide.read_region((ix, iy), best_level,
                    #                                           self.slide.level_dimensions[best_level])
                    self.tile_matrix = self.slide.read_region((ix, iy), best_level,
                                                              (sx2, sy2))
                self.view.resetTransform()
            # print("self.slide.***(self.tile_location, best_level, self.tile_size) : {}".format(t.interval))
            # self.pixmap = matrix_to_pixmap(pilimage_to_array(self.tile_matrix))
            self.pixmap = self.pilimage_to_pixmap(self.tile_matrix)
            # self.pixmap = self.pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio)
            self.scene.clear()
            self.graphics_pixmap = self.scene.addPixmap(self.pixmap)
            self.graphics_pixmap.sceneEvent = self.sceneEvent

            self.scene.addRect(self.scene.sceneRect())
            self.view.fitInView(self.graphics_pixmap)
            self.scene.setSceneRect(self.graphics_pixmap.boundingRect())
            self.scene.invalidate()
            self.last_level = best_level
        else:
            self.zoom_factor *= zoom_
            self.downsample_factor /= zoom_
            # self.view.scale(zoom_, zoom_)

    def sceneEvent(self, event):
        print("scene event", event)

    def reset_slide_params(self):
        self.last_level = -1
        self.zoom_factor = 1
        self.downsample_factor = 15
        self.last_mouse_pos = QPoint(0, 0)
        # self.zoom_factor = 0
        # self.tile_size = self.slide.level_dimensions[0]
        self.tile_location = (0, 0)

    def get_view_size(self):
        size = self.view.size()
        return (size.width(), size.height())

    def wheelEvent(self, event):
        # print(event.pos())
        # print(self.view.mapFromScene(event.pos()))
        # print("mapToScene", self.view.mapToScene(event.pos()))
        # print(self.graphics_pixmap.mapToScene(event.pos()))
        # print(self.graphics_pixmap.mapFromScene(event.pos()))
        # print(self.graphics_pixmap.mapToParent(event.pos()))
        # print(self.graphics_pixmap.mapFromParent(event.pos()))
        # print("self.scene.sceneRect", self.scene.sceneRect())
        # print("self.view.sceneRect().getCoords", self.view.sceneRect().getCoords())
        # print("self.graphics_pixmap.mapToScene()", self.graphics_pixmap.mapToScene(self.graphics_pixmap.pos()).x())
        # print("last moust pos", self.view.mapToScene(self.last_mouse_pos))

        # print(self.graphics_pixmap.mapFromItem(event.pos()))
        # print(self.graphics_pixmap.mapFromItem(event.pos()))
        # print(self.scene.sceneRect())
        # print(self.view.pos())
        # self.updateTile()
        zoom_in = 1.25
        zoom_out = 1 / 1.25

        # print("wheel event", event.angleDelta().y())
        if event.angleDelta().y() > 0:
            zoom_ = zoom_in
        # if self.zoom_factor < self.zoom_factors[len(self.zoom_factors) - 1]:
        #     self.zoom_factor += 1
        #     self.updateTile()
        elif event.angleDelta().y() < 0:
            zoom_ = zoom_out
        # if self.zoom_factor > self.zoom_factors[0]:
        #     self.zoom_factor -= 1
        #     self.updateTile()

        # self.view.scale(zoom_, zoom_)



        # self.graphics_pixmap.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        # self.graphics_pixmap.setScale(self.zoom_factor)
        self.rereadTileIfNeed(zoom_)
        # print(event.screenPos())
        # print(event.scenePos())
        event.accept()


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
    slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'
    slideViewer = SlideViewer2()
    layout.addWidget(slideViewer)

    win.show()

slideViewer.setSlide(slide_path)

sys.exit(app.exec_())
