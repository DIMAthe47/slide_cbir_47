import sys

from PIL import Image
from PyQt5 import QtGui

from PIL.ImageQt import ImageQt
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout, \
    QTableView, QListView, QFileDialog, QPushButton, QAbstractItemView
from PyQt5.QtCore import Qt, pyqtSlot, QAbstractListModel, QModelIndex, QVariant

sys.path.append(r"/home/dimathe47/PycharmProjects/cbir")
import model_utils
import json_utils

import openslide


def build_items_for_tiles_descritpors_models(filepathes):
    items = []
    for filepath in filepathes:
        tiles_descritpors_models = json_utils.read(filepath)
        img_path = model_utils.find_image_path(tiles_descritpors_models[0])
        pilimg = openslide.OpenSlide(img_path).get_thumbnail((100, 100))
        item = {"pilimg": pilimg, "text": img_path,
                "tiles_descriptors_models": tiles_descritpors_models}
        items.append(item)
    return items


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
            w = 100
            h = 100
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
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)


class TilesDescriptorWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        self.setWindowTitle('Image List')
        self.setMinimumSize(500, 600)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.list_view = SimpleListView()

        # img_dir = '/home/dimathe47/data/geo_tiny/Segm_RemoteSensing1/cropped'
        # import os
        # img_names = os.listdir(img_dir)
        #
        # pilimg_text_list = [{"idx": i, "pilimg": Image.open(os.path.join(img_dir, img_name)), "text": img_name} for
        #                     i, img_name in
        #                     enumerate(img_names)]
        # image_list_model = ImageTextListModel(pilimg_text_list)
        # self.list_view.setModel(image_list_model)
        layout.addWidget(self.list_view)

        fileDialogButton = QPushButton("Load")
        fileDialogButton.clicked.connect(self.onFileDialogAction)
        layout.addWidget(fileDialogButton)
        # layout.addItem()

    @pyqtSlot()
    def onFileDialogAction(self):
        filepathes, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "")

        # selected_dir = r'C:\Users\User\GoogleDisk\Pictures\Mountains'
        # selected_dir = r'D:\datasets\brodatz\data.brodatz\size_213x213'
        self.updateItemsModel(filepathes)
        # self.updateSearchResultsView([])

    def dragEnterEvent(self, e):
        # print("drag", e.mimeData().hasText())
        if e.mimeData().hasText():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        uri_list_text = e.mimeData().text()
        uris = uri_list_text.split('\n')
        filepathes = []
        for uri_ in uris:
            try:
                filepath = uri_.split('file:///')[1]
                filepathes.append(filepath)
            except e:
                print(e)
        # print("drop", len(e.mimeData().text()), e.mimeData().text())
        self.updateItemsModel(filepathes)
        # self.updateSearchResultsView([])

    def updateItemsModel(self, filepathes):
        items_ = build_items_for_tiles_descritpors_models(filepathes)
        db_model = ImageTextListModel(items_)
        self.list_view.setModel(db_model)

        # def updateSearchResultsView(self, img_pathes):
        #     self.result_images_model = SimpleListModel(img_pathes)
        #     self.search_results_list_view.setModel(self.result_images_model)


def main():
    app = QApplication(sys.argv)

    win = TilesDescriptorWindow()

    win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

