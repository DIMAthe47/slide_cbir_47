import sys
from datetime import datetime
from functools import lru_cache

from PyQt5 import QtWidgets

import os
from PyQt5.QtCore import QRectF, Qt, QSize
from PyQt5.QtGui import QColor, QPixmapCache
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QMessageBox, QAbstractItemView

from cbir_core.computer import model_utils, computer_utils
from cbir_core.computer.model_utils import find_image_path, find_downsample
from config_constants import start_query_slide_path, start_db_filepathes_to_models, start_selection_rect, \
    main_window_size, result_items_icon_max_size_or_ratio, cache_size_in_kb, \
    base_items_icon_max_size_or_ratio
from descriptor_tile_models import DescriptorTileModels
from elapsed_timer import elapsed_timer
import numpy as np

from designer.cbir_main_window import Ui_MainWindow

import json_utils
from model_generators import *
import openslide

from slide_list_view_47.model.role_funcs import filepath_to_slideviewparams, imagepath_decoration_func, \
    decoration_size_func_factory
from slide_list_view_47.model.slide_list_model import SlideListModel
from slide_list_view_47.widgets.actions.on_get_selected_items_action import OnGetSelectedItemsDataAction
from slide_list_view_47.widgets.actions.on_load_items_action import OnLoadItemsAction
from slide_list_view_47.widgets.slide_viewer_delegate import SlideViewerDelegate
from slide_viewer_47.common.slide_view_params import SlideViewParams
from slide_viewer_47.widgets.slide_viewer import SlideViewer
from tiling_utils import get_n_columns_n_rows_for_tile_size, gen_slice_rect_n


def excepthook(excType, excValue, tracebackobj):
    print(excType, excValue, tracebackobj)


sys.excepthook = excepthook


def build_item_text(tiles_descriptors_model):
    img_path = find_image_path(tiles_descriptors_model)
    rect_tiles_model = model_utils.find_rect_tiles_model(tiles_descriptors_model)
    rect_size = rect_tiles_model["computer_func_params"]["rect_size"]
    tile_size = rect_tiles_model["computer_func_params"]["tile_size"]
    img_name = os.path.basename(img_path)
    media_object_text = "img_name: {}\nimg_size: {}\ntile_size: {}".format(img_name, rect_size, tile_size)
    return media_object_text


def filepath_to_tiles_descritpors_model(filepath):
    tiles_descritpors_models = json_utils.read(filepath)
    return DescriptorTileModels(tiles_descritpors_models)


def descriptor_tile_model_to_slide_view_params(item: DescriptorTileModels):
    return item.slide_view_params


def descriptor_tile_model_to_str(item: DescriptorTileModels):
    tiles_descriptors_model = item.models[0]
    return build_item_text(tiles_descriptors_model)


def descriptor_tile_model_decoration_func(tiles_descritpors_models: dict, icon_size: QSize):
    img_path = find_image_path(tiles_descritpors_models[0])
    return imagepath_decoration_func(img_path, icon_size)


def slideviewparams_setter(items, index, value):
    item: DescriptorTileModels = items[index.row()]
    item.slide_view_params = value


def tiles_descriptors_model_to_str(tiles_descriptors_model):
    rect_tiles_model = model_utils.find_rect_tiles_model(tiles_descriptors_model)
    rect_tiles_size = rect_tiles_model["computer_func_params"]["tile_size"]
    downsample = find_downsample(tiles_descriptors_model)
    descriptor_type = tiles_descriptors_model["name"]
    str_ = "descriptor_type: {}, rect: ({},{}), downsample: {}".format(descriptor_type,
                                                                       *rect_tiles_size, downsample)
    return str_


def build_result_item(distances, tiles_descriptor_model):
    # print(distances)
    # normalized_distances = distances/ np.max(distances)
    normalized_distances = (distances - np.min(distances)) / (np.max(distances) - np.min(distances))
    # alphas = [128 - 128 * dist for dist in normalized_distances]
    # alphas = [128 * 128 ** (-dist) for dist in normalized_distances]
    alphas = 128 ** (1 - normalized_distances)
    colors = [(0, 255, 0, int(alpha)) for alpha in alphas]
    rect_tiles_model = model_utils.find_rect_tiles_model(tiles_descriptor_model)
    rect_tiles = list(computer_utils.compute_model(rect_tiles_model))
    img_path = find_image_path(tiles_descriptor_model)
    slide_view_params = SlideViewParams(img_path, grid_rects_0_level=rect_tiles, grid_colors_0_level=colors,
                                        grid_visible=True)
    item = DescriptorTileModels([tiles_descriptor_model])
    item.slide_view_params = slide_view_params
    return item


# important. Note that in perspective query can come from outside the system - in this case we will have no access to slide or slide_path
def build_query_tile_descriptor_model(img_path, tile_rect, level,
                                      tiles_descriptor_model):
    # TODO mess with tile_rect. It is (x,y,w,h) or (x,y,x+w,y+h)!?
    slide = openslide.OpenSlide(img_path)
    # downsample = 1
    # level = slide.get_best_level_for_downsample(downsample)
    level = 0
    tile = slide.read_region(tile_rect[0:2], level, tile_rect[2:4])
    # tile.show(title="query_tile")
    query_tile_model = {
        "type": "list",
        "name": "query_tile",
        "list": [
            tile
        ]
    }

    from copy import deepcopy
    tiles_descriptor_model_copy = deepcopy(tiles_descriptor_model)
    openslide_tiler_model, parent_model = model_utils.find_openslide_tiler_model(tiles_descriptor_model_copy)
    parent_model["input_model"] = query_tile_model
    tiles_descriptor_model_copy["output_model"] = {
        "type": "inmemory"
    }
    query_tiles_descriptors_model = tiles_descriptor_model_copy
    return query_tiles_descriptors_model


class CbirMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("CBIR GUI")
        self.ui = Ui_MainWindow()
        self.resize(*main_window_size)
        self.ui.setupUi(self)

    def after_show(self):
        self.setup_base_items_widget()
        self.setup_query_viewer()
        self.setup_result_items_widget()
        self.setup_db_menu()
        self.setup_query_menu()
        self.setup_action_menu()

    def setup_query_menu(self):
        self.ui.query_menu.set_slide_viewer(self.query_viewer)

    def setup_db_menu(self):
        db_action_load = OnLoadItemsAction("load", self.ui.menubar)
        db_action_load.media_object_builder = descriptor_tile_model_to_slide_view_params
        db_action_load.set_list_model(self.base_items_widget.list_model)
        self.ui.db_menu.addAction(db_action_load)

    def setup_action_menu(self):
        action_search = OnGetSelectedItemsDataAction(self.ui.menubar, "search")
        action_search.set_list_view(self.base_items_widget.list_view)
        action_search.set_data_consumer(self.on_search_action)
        self.ui.menu_action.addAction(action_search)
        self.ui.action_select_all_images.triggered.connect(self.on_select_all_images)

    def setup_base_items_widget(self):
        self.base_items_widget = self.ui.left_widget
        self.base_items_widget.list_view.setViewMode(QtWidgets.QListView.ListMode)
        items = [filepath_to_tiles_descritpors_model(source) for source in
                 start_db_filepathes_to_models]
        self.base_items_widget.list_model.update_items(items)

        # self.base_items_widget.list_model.update_role_func(SlideListModel.SlideViewParamsRole, None)
        # self.base_items_widget.list_model.update_role_func(Qt.DecorationRole,
        #                                                    descriptor_tile_model_decoration_func)
        self.base_items_widget.list_model.update_role_func(Qt.DisplayRole, descriptor_tile_model_to_str)
        # self.base_items_widget.list_model.update_role_func(SlideListModel.SlideViewParamsRole,
        #                                                    descriptor_tile_model_to_slide_view_params)
        self.base_items_widget.list_model.slide_view_params_getter=descriptor_tile_model_to_slide_view_params

        self.base_items_widget.list_model.update_role_func(SlideListModel.DecorationSizeOrRatioRole,
                                                           decoration_size_func_factory(
                                                               self.base_items_widget.list_view, 0.5, 0.5))
        self.base_items_widget.list_model.slide_view_params_setter = slideviewparams_setter
        self.base_items_widget.list_view.setItemDelegate(SlideViewerDelegate())

    def setup_query_viewer(self):
        self.query_viewer: SlideViewer = self.ui.right_widget
        slide_view_params: SlideViewParams = SlideViewParams(start_query_slide_path)
        slide_view_params.selected_rect_0_level = start_selection_rect
        self.query_viewer.load(slide_view_params)

    def setup_result_items_widget(self):
        self.result_items_widget = self.ui.bottom_widget
        self.result_items_widget.list_view.setViewMode(QtWidgets.QListView.IconMode)
        self.result_items_widget.list_view.setSelectionMode(QAbstractItemView.NoSelection)

        self.result_items_widget.list_model.update_role_func(Qt.DisplayRole, descriptor_tile_model_to_str)
        # self.result_items_widget.list_model.update_role_func(SlideListModel.SlideViewParamsRole,
        #                                                      descriptor_tile_model_to_slide_view_params)
        self.result_items_widget.list_model.slide_view_params_getter=descriptor_tile_model_to_slide_view_params
        self.result_items_widget.list_model.update_role_func(SlideListModel.DecorationSizeOrRatioRole,
                                                           decoration_size_func_factory(
                                                               self.result_items_widget.list_view, 0.2, 0.5))
        self.result_items_widget.list_model.slide_view_params_setter = slideviewparams_setter
        self.result_items_widget.list_view.setItemDelegate(SlideViewerDelegate())

    def on_select_all_images(self):
        self.base_items_widget.list_view.selectAll()

    def on_search_action(self, items):

        if not self.query_viewer.slide_view_params.selected_rect_0_level:
            QMessageBox.question(self, 'Error', "No query rect selected", QMessageBox.Ok)
            return
        # selected_query_qrectf_0_level = QRectF(*self.query_viewer.slide_view_params.selected_rect_0_level)
        # print(items)
        selected_tiles_descriptors_models_arr = items
        tiles_descriptors_models = [tiles_descriptor_model for tiles_descriptors_models in
                                    selected_tiles_descriptors_models_arr for tiles_descriptor_model in
                                    tiles_descriptors_models.models]

        if not tiles_descriptors_models or len(tiles_descriptors_models) == 0:
            QMessageBox.question(self, 'Error', "No models selected", QMessageBox.Ok)
            return

        n_selected_images = len(selected_tiles_descriptors_models_arr)
        chosen_tiles_descriptors_models = self.choose_tile_descriptors_model(tiles_descriptors_models,
                                                                             n_selected_images)
        if not chosen_tiles_descriptors_models:
            QMessageBox.question(self, 'Error', "No descriptor model selected", QMessageBox.Ok)
            return

        self.statusBar().showMessage("Searching...")
        self.result_items_widget.list_model.update_items([])
        # return
        # self.result_items_widget.update()

        # selected_query_rect = qrectf_to_rect(selected_query_qrectf)
        selected_rect_0_level_int = [int(x) for x in self.query_viewer.slide_view_params.selected_rect_0_level]
        query_tile_descriptor_model = build_query_tile_descriptor_model(self.query_viewer.slide_view_params.slide_path,
                                                                        selected_rect_0_level_int,
                                                                        self.query_viewer.slide_view_params.level,
                                                                        chosen_tiles_descriptors_models[0])
        print(query_tile_descriptor_model)
        result_items = []
        query_descriptor = computer_utils.compute_model(query_tile_descriptor_model, force=True)
        query_descriptor = list(query_descriptor)[0]
        query_descriptor_model = {
            "type": "list",
            "list": [query_descriptor]
        }
        for chosen_tiles_descriptors_model in chosen_tiles_descriptors_models:
            start_datetime = datetime.now()
            # distance_model = generate_distance_matrix_model(query_tile_descriptor_model, chosen_tiles_descriptors_model)
            distance_model = generate_distance_matrix_model(query_descriptor_model, chosen_tiles_descriptors_model)
            distances = computer_utils.compute_model(distance_model, force=True)
            distances = list(distances)
            distances = np.array(distances).squeeze()
            result_item = build_result_item(distances, chosen_tiles_descriptors_model)
            result_items.append(result_item)
        self.statusBar().showMessage("Searching done")
        self.result_items_widget.list_model.update_items(result_items)

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
        if not chosen_str:
            return None
        chosen_tiles_descriptors_models = str__model[chosen_str]
        return chosen_tiles_descriptors_models

    def get_chosen_str(self, choice_items):
        chosen_item, okPressed = QInputDialog.getItem(self, "Select tile and descriptor params", "", choice_items, 0,
                                                      False)
        if not okPressed:
            return None
        print(chosen_item)
        return chosen_item


def main():
    app = QApplication(sys.argv)
    QPixmapCache.setCacheLimit(cache_size_in_kb)
    QPixmapCache.clear()
    win = CbirMainWindow()
    win.show()
    win.after_show()
    # win.init_view_after_show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
