import sys
from PyQt5 import QtGui, QtWidgets

from PIL import Image
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QAction
from cbir_main_window import Ui_MainWindow
from tiles_descriptors_models_view import SimpleListView, ImageTextListModel


class CbirMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CbirMainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("CBIR GUI")
        self.setMinimumSize(1000, 700)

        searchAction = QAction("search", self)
        searchAction.triggered.connect(self.close)
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&Actions')
        fileMenu.addAction(searchAction)

        img_dir = '/home/dimathe47/data/geo_tiny/Segm_RemoteSensing1/cropped'
        import os
        img_names = os.listdir(img_dir)
        pilimg_text_list = [{"idx": i, "pilimg": Image.open(os.path.join(img_dir, img_name)), "text": img_name} for
                            i, img_name in
                            enumerate(img_names)]
        image_list_model = ImageTextListModel(pilimg_text_list)

        self.ui.left_widget.setModel(image_list_model)
        self.ui.left_widget.setViewMode(QtWidgets.QListView.IconMode)
        self.ui.left_widget.setGridSize(QSize(150, 150))

        self.ui.bottom_widget.setModel(image_list_model)
        self.ui.bottom_widget.setViewMode(QtWidgets.QListView.IconMode)
        self.ui.bottom_widget.setGridSize(QSize(150, 150))

        slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'
        self.ui.right_widget.setSlide(slide_path)




def main():
    app = QApplication(sys.argv)

    win = CbirMainWindow()
    win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
