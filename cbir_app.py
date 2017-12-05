import sys
from PyQt5 import QtGui, QtWidgets

from PIL import Image
from PyQt5.QtCore import QSize, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QAction, QInputDialog, QMessageBox
from cbir_main_window import Ui_MainWindow
from tiles_descriptors_models_view import SimpleListView, ImageTextListModel

sys.path.append(r"/home/dimathe47/PycharmProjects/cbir")
import model_utils
import json_utils
from model_generators import *
import computer_utils


def generate_tile_descriptor_model(img_path, tile_rect, downsample, tiles_descriptor_model):
    # tiling_model = {
    #     "type": "list",
    #     "name":"query_tile",
    #     "list": [
    #         pilimg
    #     ]
    # }
    rects_model = {
        "type": "list",
        "name": "query_tile",
        "list": [
            tile_rect
        ]
    }
    tiling_model = generate_tiling_model2(rects_model, img_path, downsample)
    img_matrix_model = generate_pilimage_to_matrix_model(generate_rgbapilimage_to_rgbpilimage_model(tiling_model))
    tiles_descriptor_model_copy = dict(tiles_descriptor_model)
    tiles_descriptor_model_copy["input_model"] = img_matrix_model
    tiles_descriptor_model_copy["output_model"] = {
        "type": "inmemory"
    }
    return tiles_descriptor_model_copy


class CbirMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CbirMainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setAcceptDrops(True)

        self.setWindowTitle("CBIR GUI")
        self.setMinimumSize(1000, 700)

        showQueryTileAction = QAction("show query tile", self)
        showQueryTileAction.triggered.connect(self.onShowQuery)

        searchAction = QAction("search", self)
        searchAction.triggered.connect(self.onSearchAction)

        mainMenu = self.menuBar()
        actionMenu = mainMenu.addMenu('&Actions')
        actionMenu.addAction(searchAction)
        actionMenu.addAction(showQueryTileAction)

        # img_dir = '/home/dimathe47/data/geo_tiny/Segm_RemoteSensing1/cropped'
        # import os
        # img_names = os.listdir(img_dir)
        # pilimg_text_list = [{"idx": i, "pilimg": Image.open(os.path.join(img_dir, img_name)), "text": img_name} for
        #                     i, img_name in
        #                     enumerate(img_names)]
        # image_list_model = ImageTextListModel(pilimg_text_list)

        # self.ui.left_widget.list_view.setModel(image_list_model)
        self.ui.left_widget.list_view.setViewMode(QtWidgets.QListView.IconMode)
        self.ui.left_widget.list_view.setGridSize(QSize(150, 150))
        filepathes = ["/home/dimathe47/PycharmProjects/show_slide_2/array.json"]
        self.ui.left_widget.updateItemsModel(filepathes)

        # self.ui.bottom_widget.setModel(image_list_model)
        # self.ui.bottom_widget.list_view.setViewMode(QtWidgets.QListView.IconMode)
        # self.ui.bottom_widget.list_view.setGridSize(QSize(150, 150))

        slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'
        self.ui.right_widget.load_slide(slide_path)

    @pyqtSlot()
    def onShowQuery(self):
        pilimg = self.ui.right_widget.get_selected_rect_pilimg()
        if pilimg:
            # pilimg.save("selected_rect.png")
            pilimg.show()

    @pyqtSlot()
    def onSearchAction(self):
        n_nearest = 10
        selected_items = []
        for index in self.ui.left_widget.list_view.selectionModel().selectedIndexes():
            selected_item_text = self.ui.left_widget.list_view.model().data(index, Qt.DisplayRole)
            for item in self.ui.left_widget.list_view.model().pilimg_text_list:
                if item["text"] == selected_item_text:
                    selected_items.append(item)

        print(selected_items)

        """
        only one db image for now
        TODO: take into account many db images
        descriptor_name__items = {}
        for item in selected_items:
            for descriptor_model in item["tiles_descriptors_models"]:
                items_with_desc_name = descriptor_name__items.get(descriptor_model["name"], [])
                items_with_desc_name.append(item)
                descriptor_name__items[descriptor_model["name"]] = items_with_desc_name

        available_descriptor_models = []
        for descriptor_name in descriptor_name__items:
            # need intersection here
            items_set=descriptor_name__items[descriptor_name]
            if len(items_set)==len(selected_items):
                available_descriptor_models.append(*items_set)

        print(available_descriptor_models)
        """

        if not selected_items:
            buttonReply = QMessageBox.question(self, 'Error', "No images/models are selected",
                                               QMessageBox.Ok)
            return

        tiles_descriptors_models_choose_items = []
        selected_item = selected_items[0]
        choose_item__tiles_descriptors_model = {}
        for tiles_descriptors_model in selected_item["tiles_descriptors_models"]:
            tile_rects_model = model_utils.find_tiles_rects_model(tiles_descriptors_model)
            tile_rects_shape = tile_rects_model["computer_func_params"]["tile_shape"]
            downsample = tile_rects_model["computer_func_params"]["downsample"]
            descriptor_type = tiles_descriptors_model["name"]
            choose_item = "descriptor_type: {}, rect: ({},{}), downsample: {}".format(descriptor_type,
                                                                                      tile_rects_shape[0],
                                                                                      tile_rects_shape[1], downsample)
            tiles_descriptors_models_choose_items.append(choose_item)
            choose_item__tiles_descriptors_model[choose_item] = tiles_descriptors_model

        print(tiles_descriptors_models_choose_items)

        choosen_item = self.getChoice(tiles_descriptors_models_choose_items)
        choosen_tiles_descriptors_model = choose_item__tiles_descriptors_model[choosen_item]

        pilimg = self.ui.right_widget.get_selected_rect_pilimg()
        if not pilimg:
            buttonReply = QMessageBox.question(self, 'Error', "No query tile selected",
                                               QMessageBox.Ok)
            return

        tile_rect_d=self.ui.right_widget.get_selected_rect()
        slide_path=self.ui.right_widget.slide_path

        query_tile_descriptor_model = generate_tile_descriptor_model(slide_path, tile_rect_d[0:4],tile_rect_d[4], choosen_tiles_descriptors_model)
        print(query_tile_descriptor_model)
        descriptor = computer_utils.compute_model(query_tile_descriptor_model)
        print(descriptor)
        dst_model = generate_distance_matrix_model(query_tile_descriptor_model, choosen_tiles_descriptors_model, "l2",
                                                   "dst.hdf5")
        nearest_indices_model = generate_nearest_indices_model(dst_model, -1, "nearest_indices.hdf5")
        nearest_indices=computer_utils.compute_model(nearest_indices_model)[0]



        # if not query_images_filepathes:

    #     return

    # self.search_results = fake_search_results = [[query_image_filepath] * n_nearest for query_image_filepath in query_image_filepathes]
    # self.search_results = self.retrieve_search_results(query_images_filepathes, n_nearest)


    # self.updateSearchResultsView(self.search_results[0])

    def getChoice(self, choice_items):
        item, okPressed = QInputDialog.getItem(self, "Select tile and descriptor params", "", choice_items, 0, False)
        if okPressed and item:
            print(item)
            return item


def main():
    app = QApplication(sys.argv)

    win = CbirMainWindow()
    win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
