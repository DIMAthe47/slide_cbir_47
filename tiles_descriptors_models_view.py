import sys

from PIL import Image
from PyQt5 import QtGui

from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout, \
    QTableView, QListView
from PyQt5.QtCore import Qt, pyqtSlot, QAbstractListModel, QModelIndex, QVariant


class ImageTextListModel(QAbstractListModel):
    # dataChangedSignal = pyqtSignal(int, int)

    def __init__(self, pilimg_text_list):
        QAbstractListModel.__init__(self)
        self.pilimg_text_list = pilimg_text_list
        # self.scale_pilimg = 0.5

    def rowCount(self, parent=QModelIndex()):
        return len(self.pilimg_text_list)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return QVariant(self.pilimg_text_list[index.row()]["text"])
        elif role == Qt.EditRole:
            return QVariant(self.pilimg_text_list[index.row()]["text"])
        elif role == Qt.ToolTipRole:
            return QVariant(self.pilimg_text_list[index.row()]["text"])
        elif role == Qt.DecorationRole:
            pilimg = self.pilimg_text_list[index.row()]["pilimg"]
            qim = ImageQt(pilimg)
            pixmap = QtGui.QPixmap.fromImage(qim)
            # w = pilimg.size[0] * self.scale_pilimg
            # h = pilimg.size[1] * self.scale_pilimg
            w=100
            h=100
            pixmap = pixmap.scaled(w, h)
            return QVariant(pixmap)
            # return QVariant(pixmap)
        else:
            return QVariant()

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled


class SimpleListView(QListView):
    def __init__(self, parent=None):
        QListView.__init__(self, parent)
        self.setAlternatingRowColors(True)


def main():
    app = QApplication(sys.argv)

    win = QWidget()
    win.setWindowTitle('Image List')
    win.setMinimumSize(500, 600)
    layout = QVBoxLayout()
    win.setLayout(layout)

    list_view = SimpleListView()

    img_dir = '/home/dimathe47/data/geo_tiny/Segm_RemoteSensing1/cropped'
    import os
    img_names = os.listdir(img_dir)

    pilimg_text_list = [{"idx": i, "pilimg": Image.open(os.path.join(img_dir, img_name)), "text": img_name} for
                        i, img_name in
                        enumerate(img_names)]
    image_list_model = ImageTextListModel(pilimg_text_list)
    list_view.setModel(image_list_model)
    layout.addWidget(list_view)

    win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
