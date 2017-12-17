import sys
from PyQt5 import QtGui, QtWidgets

from PIL import Image
from PyQt5.QtCore import QSize, pyqtSlot, Qt, QRectF
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QAction, QInputDialog, QMessageBox, QAbstractItemView
from media_object import OnLoadMediaObjectsAction, MediaObject, OnGetDataSelectedMediaObjectsAction, \
    PixmapWithMaskedTiles
from slide_viewer_menu import SlideViewerMenu
import numpy as np

from cbir_main_window import Ui_MainWindow

sys.path.append(r"/home/dimathe47/PycharmProjects/cbir")
import model_utils
import json_utils
from model_generators import *
import computer_utils
import openslide

start_selection_rect = QRectF(0, 0, 500, 500)


def qrectf_to_rect(qrectf: QRectF):
    return (int(qrectf.x()), int(qrectf.y()), int(qrectf.width()), int(qrectf.height()))


def find_image_path(model):
    img_path = model_utils.find_tile_model(model)["computer_func_params"]["image_model"]["string"]
    return img_path


def find_downsample(model):
    img_path = model_utils.find_tile_model(model)["computer_func_params"]["downsample"]
    return img_path


def filepath_to_media_object(filepath):
    tiles_descritpors_models = json_utils.read(filepath)
    img_path = find_image_path(tiles_descritpors_models[0])
    pilimg = openslide.OpenSlide(img_path).get_thumbnail((100, 100))
    media_object = MediaObject(filepath, pilimg, tiles_descritpors_models)
    return media_object


# important. Note that in perspective query can come from outside the system - in this case we will have no access to slide or slide_path
def slidepath_to_tiles_descriptors_model(img_path, tile_rect, downsample,
                                         tiles_descriptor_model):
    # TODO mess with tile_rect. It is (x,y,w,h) or (x,y,x+w,y+h)!?
    slide = openslide.OpenSlide(img_path)
    downsample = 1
    level = slide.get_best_level_for_downsample(downsample)
    tile = slide.read_region(tile_rect[0:2], level, tile_rect[2:4])
    # tile.show(title="query_tile")
    query_tile_model = {
        "type": "list",
        "name": "query_tile",
        "list": [
            tile
        ]
    }

    tiles_descriptor_model_copy = dict(tiles_descriptor_model)
    pilimage_to_matrix_model, parent_model = model_utils.find_pilimage_to_matrix_model(tiles_descriptor_model_copy)
    pilimage_to_matrix_model_copy = dict(pilimage_to_matrix_model)
    parent_model["input_model"] = pilimage_to_matrix_model_copy
    pilimage_to_matrix_model_copy["input_model"] = query_tile_model
    tiles_descriptor_model_copy["output_model"] = {
        "type": "inmemory"
    }
    query_tiles_descriptors_model = tiles_descriptor_model_copy
    return query_tiles_descriptors_model


class TilesDistancesIndicatorPixmap(PixmapWithMaskedTiles):
    def __init__(self, img, tile_rects, distances) -> None:
        self.distances = distances
        self.normalized_distances = distances / np.max(distances)
        qcolors = [QColor(0, 255, 0, normalized_distance * 128) for normalized_distance in
                   self.normalized_distances]
        super().__init__(img, tile_rects, qcolors)


class CbirMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CbirMainWindow, self).__init__()
        self.setWindowTitle("CBIR GUI")
        self.setMinimumSize(1000, 700)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.query_menu.set_slide_viewer(self.ui.right_widget)

        db_action_load = OnLoadMediaObjectsAction(self.ui.menubar, "load")
        db_action_load.set_list_view(self.ui.left_widget.list_view)
        db_action_load.set_media_object_extractor(filepath_to_media_object)
        self.ui.db_menu.addAction(db_action_load)

        action_search = OnGetDataSelectedMediaObjectsAction(self.ui.menubar, "search")
        action_search.set_list_view(self.ui.left_widget.list_view)
        action_search.set_data_consumer(self.on_search_action)
        self.ui.menu_action.addAction(action_search)

        self.ui.left_widget.width()

        # default init
        media_objects = [filepath_to_media_object(source) for source in
                         ["/home/dimathe47/PycharmProjects/slide_cbir_47/array.json"]]
        self.ui.left_widget.list_view.update_media_objects(media_objects)
        self.ui.left_widget.list_view.selectAll()

        slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'
        # slide_path = '/home/dimathe47/Downloads/CMU-1-Small-Region.svs'
        self.ui.right_widget.load_slide(slide_path)
        self.ui.right_widget.selected_qrectf_level_downsample = 1
        self.ui.right_widget.selected_qrectf_0_level = start_selection_rect
        self.ui.right_widget.update_selected_rect_view()

        self.ui.left_widget.list_view.setViewMode(QtWidgets.QListView.ListMode)
        self.ui.bottom_widget.list_view.setViewMode(QtWidgets.QListView.ListMode)
        self.ui.bottom_widget.list_view.setSelectionMode(QAbstractItemView.NoSelection)

    def init_view_after_show(self):
        self.ui.bottom_widget.list_view.update_media_objects_per_viewport(1)

    @pyqtSlot()
    def onShowQuery(self):
        pilimg = self.ui.right_widget.get_selected_rect_pilimg()
        if pilimg:
            # pilimg.save("selected_rect.png")
            pilimg.show()

    def on_search_action(self, media_objects):
        print(media_objects)
        n_nearest = 10
        selected_tiles_descriptors_models = media_objects
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
        selected_tiles_descriptors_models = selected_tiles_descriptors_models[0]

        if not selected_tiles_descriptors_models:
            buttonReply = QMessageBox.question(self, 'Error', "No models selected",
                                               QMessageBox.Ok)
            return

        selected_query_qrectf = self.get_selected_query_qrectf()
        if not selected_query_qrectf:
            buttonReply = QMessageBox.question(self, 'Error', "No query rect selected",
                                               QMessageBox.Ok)
            return

        chosen_tiles_descriptors_model = self.choose_tiles_descriptors_model(selected_tiles_descriptors_models)
        if not chosen_tiles_descriptors_model:
            buttonReply = QMessageBox.question(self, 'Error', "No descriptor model selected",
                                               QMessageBox.Ok)
            return

        selected_query_rect = qrectf_to_rect(selected_query_qrectf)
        # selected_query_top_left = (selected_query_qrectf.topLeft().x(), selected_query_qrectf.topLeft().y())
        # selected_query_bottom_right = (selected_query_qrectf.bottomRight().x(), selected_query_qrectf.bottomRight().y())

        query_tile_descriptor_model = slidepath_to_tiles_descriptors_model(self.get_query_slide_path(),
                                                                           selected_query_rect,
                                                                           self.get_selected_query_level_downsample(),
                                                                           chosen_tiles_descriptors_model)
        print(query_tile_descriptor_model)
        descriptor = computer_utils.compute_model(query_tile_descriptor_model)
        print(list(descriptor))
        # distance_model = generate_distance_matrix_model(query_tile_descriptor_model, chosen_tiles_descriptors_model,
        #                                                 "l2", "computed/dst.hdf5")
        # db_descriptors = computer_utils.compute_model(chosen_tiles_descriptors_model, force=False)

        distance_model = generate_distance_matrix_model(query_tile_descriptor_model, chosen_tiles_descriptors_model)

        distances = computer_utils.compute_model(distance_model, force=True)
        distances = np.array(distances).squeeze()
        # distances = computer_utils.read_input_model(distance_model["output_model"])[0]
        print(distances)

        normalized_distances = distances / np.max(distances)
        alphas = [128 - 128 * dist for dist in normalized_distances]
        qcolors = [QColor(0, 255, 0, int(alpha)) for alpha in alphas]
        rect_tiles_model = model_utils.find_rect_tiles_model(chosen_tiles_descriptors_model)
        rect_tiles = list(computer_utils.compute_model(rect_tiles_model))
        # tile_model =  model_utils.find_tile_model(chosen_tiles_descriptors_model)
        img_path = find_image_path(chosen_tiles_descriptors_model)
        slide = openslide.OpenSlide(img_path)
        thumbnail_size = self.ui.bottom_widget.list_view.icon_size
        thumbnail = slide.get_thumbnail(thumbnail_size)
        thumbnail_size = thumbnail.size
        downsample = find_downsample(chosen_tiles_descriptors_model)
        slide_size_0 = slide.level_dimensions[slide.get_best_level_for_downsample(downsample)]
        slide_size = (slide_size_0[0] / downsample, slide_size_0[1] / downsample)
        thumbnail_scale = (slide_size[0] / thumbnail_size[0], slide_size[1] / thumbnail_size[1])

        # for slide_rect in rect_tiles:
        #     rect_as_arr=np.array(slide_rect)
        #     rect_as_arr[]/=
        thumbnail_rects = [(slide_rect[0] / thumbnail_scale[0], slide_rect[1] / thumbnail_scale[1],
                            slide_rect[2] / thumbnail_scale[0], slide_rect[3] / thumbnail_scale[1]) for
                           slide_rect in
                           rect_tiles]

        media_object = MediaObject(img_path, PixmapWithMaskedTiles(thumbnail, thumbnail_rects, qcolors),
                                   chosen_tiles_descriptors_model)
        self.ui.bottom_widget.list_view.update_media_objects([media_object])

        # nearest_indices_model = generate_nearest_indices_model(distance_model, -1, "computed/nearest_indices.hdf5")
        # nearest_indices = computer_utils.compute_model(nearest_indices_model)[0]
        # print(nearest_indices)

    def get_query_slide_path(self):
        return self.ui.right_widget.slide_path

    def get_selected_query_qrectf(self):
        return self.ui.right_widget.selected_qrectf_0_level

    def get_selected_query_level_downsample(self):
        return self.ui.right_widget.selected_qrectf_level_downsample

    def choose_tiles_descriptors_model(self, tiles_descriptors_models):
        choice_items = []
        for tiles_descriptors_model in tiles_descriptors_models:
            str_ = self.tiles_descriptors_model_to_string(tiles_descriptors_model)
            choice_items.append(str_)

        chosen_number, okPressed = self.get_chosen_number(choice_items)
        if not okPressed:
            return
        chosen_tiles_descriptors_model = tiles_descriptors_models[chosen_number]
        print(chosen_tiles_descriptors_model)
        return chosen_tiles_descriptors_model

    def tiles_descriptors_model_to_string(self, tiles_descriptors_model):
        rect_tiles_model = model_utils.find_rect_tiles_model(tiles_descriptors_model)
        rect_tiles_size = rect_tiles_model["computer_func_params"]["tile_size"]
        tile_model = model_utils.find_tile_model(tiles_descriptors_model)
        downsample = tile_model["computer_func_params"]["downsample"]
        descriptor_type = tiles_descriptors_model["name"]
        str_ = "descriptor_type: {}, rect: ({},{}), downsample: {}".format(descriptor_type,
                                                                           *rect_tiles_size, downsample)
        return str_

    def get_chosen_number(self, choice_items: list):
        item, okPressed = QInputDialog.getItem(self, "Select tile and descriptor params", "", choice_items, 0, False)
        if okPressed and item:
            print(item)
        return choice_items.index(item), okPressed


def main():
    app = QApplication(sys.argv)
    win = CbirMainWindow()
    win.show()
    win.init_view_after_show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
