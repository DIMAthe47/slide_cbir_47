import random, sys

from PIL import Image
from PyQt5 import QtGui
import numpy as np
from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QRubberBand, QLabel, QApplication, QMessageBox, QWidget, QScrollArea, QVBoxLayout, \
    QSizePolicy, QHBoxLayout, QSlider
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
    # pilimage.show()

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


class SlideViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()

        self.imageLabel = QLabel()
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.imageLabel)

        self.scrollArea.setWidgetResizable(True)
        layout = QHBoxLayout()
        layout.addWidget(self.scrollArea)
        self.slider = QSlider(Qt.Vertical)
        self.slider.setMinimum(0)
        self.slider.setMaximum(2)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(self.slider_changed)
        layout.addWidget(self.slider)

        self.setLayout(layout)
        # self.imageLabel.resize(*self.get_view_max_size())
        # self.imageLabel.resize(100,200)

    def pilimage_to_pixmap(self, pilimage):
        qim = ImageQt(pilimage)
        pix = QtGui.QPixmap.fromImage(qim)
        return pix

    def slider_changed(self, newvalue):
        print('slot method called.', newvalue)
        self.zoom_factor = newvalue
        self.updateTile()

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
        self.updateTile()
        self.zoom_factors = list(range(len(self.slide.level_dimensions)))
        # image = QImage(img_path)
        # if image.isNull():
        #     QMessageBox.information(self, "Image Viewer",
        #                             "Cannot load %s." % img_path)
        #     return
        # self.imageLabel.setPixmap(QPixmap.fromImage(image))
        # self.imageLabel.adjustSize()

    def updateTile(self):
        best_level = 2 - self.zoom_factor
        # best_level = self.slide.get_best_level_for_downsample(self.zoom_factor)
        print("best_level", best_level)
        with Timer() as t:
            if best_level == 2:
                self.tile_matrix = self.slide.get_thumbnail((640, 480))
                # self.tile_matrix = self.slide.get_thumbnail(self.get_view_max_size())
            else:
                self.tile_matrix = self.slide.read_region(self.tile_location, best_level,
                                                          (640, 480))
        print("self.slide.***(self.tile_location, best_level, self.tile_size) : {}".format(t.interval))
        # self.pixmap = matrix_to_pixmap(pilimage_to_array(self.tile_matrix))
        self.pixmap = self.pilimage_to_pixmap(self.tile_matrix)
        self.pixmap = self.pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio)
        self.imageLabel.setPixmap(self.pixmap)
        # self.imageLabel.adjustSize()

    def reset_slide_params(self):
        self.zoom_factor = 0
        self.tile_size = self.slide.level_dimensions[0]
        self.tile_location = (0, 0)

    def get_view_max_size(self):
        size = self.scrollArea.rect().size()
        # print(str(size))
        # print(str(self.rect().size()))
        # print(str(self.imageLabel.rect().size()))
        size = (size.width(), size.height())
        print(size)
        return size

    def wheelEvent(self, event):
        print("wheel event", event.angleDelta().y())
        if event.angleDelta().y() > 0:
            if self.zoom_factor < self.zoom_factors[len(self.zoom_factors) - 1]:
                self.zoom_factor += 1
                self.updateTile()
        elif event.angleDelta().y() < 0:
            if self.zoom_factor > self.zoom_factors[0]:
                self.zoom_factor -= 1
                self.updateTile()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    win = QWidget()
    win.setWindowTitle('Image List')
    # win.setMinimumSize(500, 400)
    layout = QVBoxLayout()
    win.setLayout(layout)

    # dirpath = '/home/dimathe47/data/geo_tiny/Segm_RemoteSensing1/cropped/poligon_minsk_1_yandex_z18_train_0_0.jpg'
    # dirpath = '/home/dimathe47/data/geo_tiny/S/egm_RemoteSensing1/poligon_minsk_1_yandex_z18_train.jpg'
    # slide_path = '/home/dimathe47/Downloads/CMU-1-Small-Region.svs'
    slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'
    slideViewer = SlideViewer()
    layout.addWidget(slideViewer)
    slideViewer.setSlide(slide_path)

    win.show()

    sys.exit(app.exec_())
