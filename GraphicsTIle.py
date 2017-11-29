import typing

from PIL.ImageQt import ImageQt
from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, QRect

from PyQt5.QtWidgets import QGraphicsItem, QWidget
import openslide


class GraphicsTile(QGraphicsItem):
    def __init__(self, x_y_w_h, slide: openslide.OpenSlide, level, downsample):
        super().__init__()
        self.x_y_w_h = x_y_w_h
        self.rect = QRect(x_y_w_h[0], x_y_w_h[1], x_y_w_h[2] * downsample, x_y_w_h[3] * downsample)
        # self.rect = QRect(0, 0, x_y_w_h[2] * downsample, x_y_w_h[3] * downsample)
        self.rect = QRect(x_y_w_h[0], x_y_w_h[1], x_y_w_h[2], x_y_w_h[3])
        self.slide = slide
        self.level = level
        self.downsample = downsample

    def pilimage_to_pixmap(self, pilimage):
        # pilimage.show()
        qim = ImageQt(pilimage)
        pix = QtGui.QPixmap.fromImage(qim)
        return pix

    def boundingRect(self):
        return QRectF(self.rect)

    def setDownsaple(self, downsample):
        self.downsample = downsample
        self.rect.setWidth(self.x_y_w_h[2] * downsample)
        self.rect.setHeight(self.x_y_w_h[3] * downsample)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...):
        # print("paint")
        # painter.drawRect(self.rect)
        # painter.drawRect(0,0,100,100)
        x = int(self.x_y_w_h[0] * self.downsample)
        y = int(self.x_y_w_h[1] * self.downsample)
        # x=0
        # y=0
        tile_pilimage = self.slide.read_region((x, y),
                                               self.level, (self.x_y_w_h[2], self.x_y_w_h[3]))
        self.pixmap = self.pilimage_to_pixmap(tile_pilimage)

        painter.drawPixmap(self.rect, self.pixmap)
