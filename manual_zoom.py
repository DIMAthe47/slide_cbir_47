import sys
from PyQt5 import QtGui

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPixmap, QWheelEvent
from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QVBoxLayout, QLabel, QApplication, QMainWindow

from app3 import point_to_str, rect_to_str


class ZoomViewer(QWidget):
    def __init__(self):
        super(ZoomViewer, self).__init__()
        self.view = QGraphicsView()
        self.view.setTransformationAnchor(QGraphicsView.NoAnchor)

        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.level_label = QLabel()
        self.selected_rect_label = QLabel()
        self.mouse_pos_scene_label = QLabel()
        self.mouse_pos_view_label = QLabel()
        self.old_pos_label = QLabel()
        self.new_pos_label = QLabel()
        self.mouse_pos_delta_label = QLabel()
        self.view_rect_view_label = QLabel()
        self.view_rect_scene_label = QLabel()
        layout.addWidget(self.level_label)
        layout.addWidget(self.selected_rect_label)
        layout.addWidget(self.mouse_pos_scene_label)
        layout.addWidget(self.mouse_pos_view_label)
        layout.addWidget(self.old_pos_label)
        layout.addWidget(self.new_pos_label)
        layout.addWidget(self.mouse_pos_delta_label)
        layout.addWidget(self.view_rect_view_label)
        layout.addWidget(self.view_rect_scene_label)
        self.mouse_press_view = QPoint()
        self.view.viewport().installEventFilter(self)

    def updateLabels(self, event):
        self.mouse_pos_view_label.setText("mouse_pos_view" + point_to_str(event.pos()))
        self.mouse_pos_scene_label.setText("mouse_pos_scene" + point_to_str(self.view.mapToScene(event.pos())))
        self.view_rect_view_label.setText("view_rect_view" + rect_to_str(self.view.rect()))
        self.view_rect_scene_label.setText("view_rect_scene" + rect_to_str(self.view.mapToScene(self.view.rect())))

    def setImage(self, image_path):
        pixmap = QPixmap(image_path)
        self.scene.addPixmap(pixmap)

    def mousePressEvent(self, a0: QtGui.QMouseEvent):
        self.view.translate(1000, 1000)

    def wheelEvent(self, event):
        """
        Zoom in or out of the view.
        """
        zoomInFactor = 2
        zoomOutFactor = 1 / zoomInFactor

        # Save the scene pos
        oldPos = self.view.mapToScene(event.pos())

        # Zoom
        if event.angleDelta().y() > 0:
            zoomFactor = zoomInFactor
        else:
            zoomFactor = zoomOutFactor
        self.view.scale(zoomFactor, zoomFactor)

        # Get the new position
        newPos = self.view.mapToScene(event.pos())
        self.new_pos_label.setText("new_pos_label: " + point_to_str(newPos))
        self.old_pos_label.setText("old_pos_label: " + point_to_str(oldPos))

        # Move scene to old position
        delta = newPos - oldPos
        self.view.translate(delta.x(), delta.y())
        self.mouse_pos_delta_label.setText("mouse_pos_delta_label: " + point_to_str(delta))

    def eventFilter(self, a0: 'QObject', event: 'QEvent'):
        # return False
        print(event)
        if hasattr(event, "pos"):
            self.updateLabels(event)

        if isinstance(event, QWheelEvent):
            self.wheelEvent(event)
            self.updateLabels(event)
            return True
        return False


class ZoomMainWindow(QMainWindow):
    def __init__(self):
        super(ZoomMainWindow, self).__init__()
        slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'
        self.zoomViewer = ZoomViewer()
        self.setCentralWidget(self.zoomViewer)
        # self.installEventFilter(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ZoomMainWindow()
    image_path = '/home/dimathe47/data/geo_tiny/Segm_RemoteSensing1/poligon_minsk_1_yandex_z18_train.jpg'
    win.zoomViewer.setImage(image_path)
    win.show()
    sys.exit(app.exec_())
