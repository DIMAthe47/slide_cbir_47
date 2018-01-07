import sys

from PyQt5 import QtWidgets, QtCore

import os
from PyQt5.QtCore import pyqtSlot, QRectF
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QMessageBox, QAbstractItemView

from cbir_core.computer import model_utils, computer_utils
from media_object import MediaObject
from tiled_pixmap import TiledPixmap
from media_object_action import OnLoadMediaObjectsAction, OnGetSelectedMediaObjectsDataAction
import numpy as np

from CreateModelsDialog import CreateModelsDialog
from designer.cbir_main_window import Ui_MainWindow

import json_utils
from model_generators import *
import openslide

from tiling_utils import get_n_columns_n_rows_for_tile_size, gen_slice_rect_n

start_selection_rect = QRectF(0, 0, 500, 500)
# start_slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'
start_slide_path = r'C:\Users\DIMA\Downloads\JP2K-33003-1.svs'


# start_filepathes_to_models = ["/home/dimathe47/PycharmProjects/slide_cbir_47/models/array0.json",
#                               "/home/dimathe47/PycharmProjects/slide_cbir_47/models/array1.json"]

# start_slide_path = '/home/dimathe47/Downloads/CMU-1-Small-Region.svs'


def qrectf_to_rect(qrectf: QRectF):
    return (int(qrectf.x()), int(qrectf.y()), int(qrectf.width()), int(qrectf.height()))


def find_image_path(model):
    img_path = model_utils.find_image_model(model)["string"]
    return img_path


def find_downsample(model):
    openslide_tiler_model = model_utils.find_openslide_tiler_model(model)
    downsample = openslide_tiler_model["computer_func_params"]["downsample"]
    return downsample


def build_media_object_text(tiles_descriptors_model):
    img_path = find_image_path(tiles_descriptors_model)
    rect_tiles_model = model_utils.find_rect_tiles_model(tiles_descriptors_model)
    rect_size = rect_tiles_model["computer_func_params"]["rect_size"]
    tile_size = rect_tiles_model["computer_func_params"]["tile_size"]
    img_name = os.path.basename(img_path)
    media_object_text = "img_name: {}, image_size: {}, tile_size: {}".format(img_name, rect_size, tile_size)
    return media_object_text


def filepath_to_media_object(filepath, thumbnail_size=(500, 500)):
    tiles_descritpors_models = json_utils.read(filepath)
    img_path = find_image_path(tiles_descritpors_models[0])
    media_object_text = build_media_object_text(tiles_descritpors_models[0])
    pilimg = openslide.OpenSlide(img_path).get_thumbnail(thumbnail_size)
    media_object = MediaObject(media_object_text, pilimg, tiles_descritpors_models)
    return media_object


def tiles_descriptors_model_to_str(tiles_descriptors_model):
    rect_tiles_model = model_utils.find_rect_tiles_model(tiles_descriptors_model)
    rect_tiles_size = rect_tiles_model["computer_func_params"]["tile_size"]
    downsample =find_downsample(tiles_descriptors_model)
    descriptor_type = tiles_descriptors_model["name"]
    str_ = "descriptor_type: {}, rect: ({},{}), downsample: {}".format(descriptor_type,
                                                                       *rect_tiles_size, downsample)
    return str_


def build_media_object_with_intensities_tiles(distances, tiles_descriptor_model, icon_size):
    print(distances)
    normalized_distances = distances / np.max(distances)
    alphas = [128 - 128 * dist for dist in normalized_distances]
    qcolors = [QColor(0, 255, 0, int(alpha)) for alpha in alphas]
    rect_tiles_model = model_utils.find_rect_tiles_model(tiles_descriptor_model)
    rect_tiles = list(computer_utils.compute_model(rect_tiles_model))
    # tile_model =  model_utils.find_tile_rects_model(chosen_tiles_descriptors_model)
    img_path = find_image_path(tiles_descriptor_model)
    slide = openslide.OpenSlide(img_path)
    thumbnail_size = icon_size
    thumbnail = slide.get_thumbnail(thumbnail_size)
    thumbnail_size = thumbnail.size
    downsample = find_downsample(tiles_descriptor_model)
    slide_size_0 = slide.level_dimensions[slide.get_best_level_for_downsample(downsample)]
    slide_size = (slide_size_0[0] / downsample, slide_size_0[1] / downsample)
    thumbnail_scale = (slide_size[0] / thumbnail_size[0], slide_size[1] / thumbnail_size[1])
    slide_tile_size = (rect_tiles[0][2], rect_tiles[0][3])
    columns, rows = get_n_columns_n_rows_for_tile_size(slide_size_0, slide_tile_size)
    thumbnail_rects = gen_slice_rect_n(thumbnail_size, columns, rows)

    media_object_text = build_media_object_text(tiles_descriptor_model)
    media_object = MediaObject(media_object_text, TiledPixmap(thumbnail, thumbnail_rects, qcolors),
                               tiles_descriptor_model)
    return media_object


# important. Note that in perspective query can come from outside the system - in this case we will have no access to slide or slide_path
def build_query_tile_descriptor_model(img_path, tile_rect, downsample,
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


class CbirMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(CbirMainWindow, self).__init__()
        self.setWindowTitle("CBIR GUI")
        self.setMinimumSize(1000, 700)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_base_media_objects_widget()
        self.setup_query_viewer()
        self.setup_result_media_objects_widget()
        self.setup_db_menu()
        self.setup_query_menu()
        self.setup_action_menu()

    def setup_query_menu(self):
        self.ui.query_menu.set_slide_viewer(self.query_viewer)

    def setup_db_menu(self):
        db_action_load = OnLoadMediaObjectsAction(self.ui.menubar, "load")
        db_action_load.set_list_model(self.base_media_objects_widget.list_model)
        db_action_load.set_media_object_extractor(filepath_to_media_object)
        self.ui.db_menu.addAction(db_action_load)

        db_action_create = self.ui.db_menu.addAction("create")
        db_action_create.triggered.connect(self.on_create_models)

    def setup_action_menu(self):
        action_search = OnGetSelectedMediaObjectsDataAction(self.ui.menubar, "search")
        action_search.set_list_view(self.base_media_objects_widget.list_view)
        action_search.set_data_consumer(self.on_search_action)
        self.ui.menu_action.addAction(action_search)

    def setup_base_media_objects_widget(self):
        self.base_media_objects_widget = self.ui.left_widget
        self.base_media_objects_widget.list_view.setViewMode(QtWidgets.QListView.ListMode)
        # media_objects = [filepath_to_media_object(source) for source in start_filepathes_to_models]
        # self.base_media_objects_widget.list_model.update_media_objects(media_objects)
        # self.base_media_objects_widget.list_view.selectAll()

    def setup_query_viewer(self):
        self.query_viewer = self.ui.right_widget
        self.query_viewer.load_slide(start_slide_path)
        self.query_viewer.selected_qrectf_level_downsample = 1
        self.query_viewer.selected_qrectf_0_level = start_selection_rect
        self.query_viewer.update_selected_rect_view()

    def setup_result_media_objects_widget(self):
        self.result_media_objects_widget = self.ui.bottom_widget
        self.result_media_objects_widget.list_view.setViewMode(QtWidgets.QListView.ListMode)
        self.result_media_objects_widget.list_view.setSelectionMode(QAbstractItemView.NoSelection)
        self.result_media_objects_widget.list_view.update_icon_max_size_or_ratio((200, 0.5))

    def on_search_action(self, media_objects_data):
        selected_query_qrectf = self.query_viewer.selected_qrectf_0_level
        if not selected_query_qrectf:
            QMessageBox.question(self, 'Error', "No query rect selected", QMessageBox.Ok)
            return

        print(media_objects_data)
        selected_tiles_descriptors_models_arr = media_objects_data
        tiles_descriptors_models = [tiles_descriptor_model for tiles_descriptors_models in
                                    selected_tiles_descriptors_models_arr for tiles_descriptor_model in
                                    tiles_descriptors_models]

        if not tiles_descriptors_models or len(tiles_descriptors_models) == 0:
            QMessageBox.question(self, 'Error', "No models selected", QMessageBox.Ok)
            return

        n_selected_images = len(selected_tiles_descriptors_models_arr)
        chosen_tiles_descriptors_models = self.choose_tile_descriptors_model(tiles_descriptors_models,
                                                                             n_selected_images)
        if not chosen_tiles_descriptors_models:
            QMessageBox.question(self, 'Error', "No descriptor model selected", QMessageBox.Ok)
            return

        selected_query_rect = qrectf_to_rect(selected_query_qrectf)
        query_tile_descriptor_model = build_query_tile_descriptor_model(self.query_viewer.slide_path,
                                                                        selected_query_rect,
                                                                        self.query_viewer.selected_qrectf_level_downsample,
                                                                        chosen_tiles_descriptors_models[0])
        print(query_tile_descriptor_model)
        media_objects = []
        for chosen_tiles_descriptors_model in chosen_tiles_descriptors_models:
            distance_model = generate_distance_matrix_model(query_tile_descriptor_model, chosen_tiles_descriptors_model)
            distances = computer_utils.compute_model(distance_model, force=True)
            distances = np.array(distances).squeeze()
            media_object = build_media_object_with_intensities_tiles(distances, chosen_tiles_descriptors_model,
                                                                     self.result_media_objects_widget.list_view.icon_size)
            media_objects.append(media_object)
        self.result_media_objects_widget.list_model.update_media_objects(media_objects)

        # nearest_indices_model = generate_nearest_indices_model(distance_model, -1, "computed/nearest_indices.hdf5")
        # nearest_indices = computer_utils.compute_model(nearest_indices_model)[0]
        # print(nearest_indices)

    def choose_tile_descriptors_model(self, tiles_descriptors_models, n_selected_images):
        str__model = {}
        for tiles_descriptor_model in tiles_descriptors_models:
            str_ = tiles_descriptors_model_to_str(tiles_descriptor_model)
            models = str__model.get(str_, [])
            models.append(tiles_descriptor_model)
            str__model[str_] = models

        available_models_for_selected_images_strs = [str_ for str_ in str__model if
                                                     len(str__model[str_]) == n_selected_images]
        chosen_str = self.get_chosen_str(available_models_for_selected_images_strs)
        chosen_tiles_descriptors_models = str__model[chosen_str]
        return chosen_tiles_descriptors_models

    def get_chosen_str(self, choice_items):
        chosen_item, okPressed = QInputDialog.getItem(self, "Select tile and descriptor params", "", choice_items, 0,
                                                      False)
        if not okPressed:
            return
        print(chosen_item)
        return chosen_item

    def on_create_models(self):
        CreateModelsDialog(self).show()
        print("on_create_models")


def main():
    app = QApplication(sys.argv)
    win = CbirMainWindow()
    win.show()
    # win.init_view_after_show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
