import typing

from PIL.ImageQt import ImageQt
from PyQt5 import QtGui
from PyQt5.QtCore import QRectF, QRect, Qt

from PyQt5.QtWidgets import QGraphicsItem, QWidget
import openslide


class SelectedRect(QGraphicsItem):
    def __init__(self, qrect: QRect, downsample):
        super().__init__()
        self.qrect = QRect(qrect.x(), qrect.y(), qrect.width() * downsample, qrect.height() * downsample)
        self.downsample = downsample
        self.setAcceptedMouseButtons(Qt.NoButton)

    def boundingRect(self):
        return QRectF(self.qrect)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionGraphicsItem',
              widget: typing.Optional[QWidget] = ...):
        painter.drawRect(self.qrect)
