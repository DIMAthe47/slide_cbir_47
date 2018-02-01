from datetime import datetime
from typing import Iterable

import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QAbstractItemView, QMessageBox, QInputDialog

from slide_cbir_47.slide_cbir_47_config import main_window_size, start_db_filepathes_to_slide_tiles_descriptors_models, \
    base_items_icon_max_size_or_ratio, \
    start_query_slide_path, start_selection_rect, result_items_icon_max_size_or_ratio
from cbir_core.computer import computer_utils
from slide_cbir_47.model.slide_tiles_descriptors_models_view_item import SlideTilesDescriptorsModelsViewItem
from slide_cbir_47.designer.cbir_main_window import Ui_MainWindow
from model_generators import generate_distance_matrix_model
from slide_list_view_47.model.role_funcs import item_to_pixmap_through_slideviewparams_factory, \
    decoration_size_func_factory
from slide_list_view_47.model.slide_list_model import SlideListModel
from slide_list_view_47.widgets.actions.list_view_menu import ListViewMenu
from slide_list_view_47.widgets.actions.on_get_selected_items_action import OnGetSelectedItemsDataAction
from slide_list_view_47.widgets.actions.on_load_items_action import OnLoadItemsAction
from slide_cbir_47.model.slide_tiles_descriptors_models_view_item_funcs import \
    slide_tiles_descriptors_models_view_item_to_slide_view_params, slide_tiles_descriptors_models_view_item_to_str, \
    tiles_descriptors_model_to_str, filepath_to_slide_tiles_descriptors_models_view_item, \
    build_result_slide_tiles_descriptors_models_view_item, build_query_tiles_descriptors_model
from slide_viewer_47.common.qt.my_action import MyAction
from slide_viewer_47.common.slide_view_params import SlideViewParams
from slide_viewer_47.widgets.menu.on_load_slide_action import OnLoadSlideAction
from slide_viewer_47.widgets.menu.slide_viewer_view_menu import SlideViewerViewMenu
from slide_viewer_47.widgets.slide_viewer import SlideViewer


class CbirMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.resize(*main_window_size)
        self.ui.setupUi(self)
        self.setWindowTitle("slide_cbir_47")

    def after_show(self):
        self.setup_base_items_widget()
        self.setup_query_viewer()
        self.setup_result_items_widget()
        self.setup_db_menu()
        self.setup_results_menu()
        self.setup_query_menu()
        self.setup_action_menu()
        self.db_list_view_menu.item_mode_menu.delegate_mode_action.trigger()
        self.results_list_view_menu.item_mode_menu.delegate_mode_action.trigger()

    def setup_query_menu(self):
        on_load_slide_action = OnLoadSlideAction("&load", self.ui.query_menu, self.query_viewer)
        slide_viewer_view_menu = SlideViewerViewMenu("&view", self.ui.query_menu, self.query_viewer)

    def setup_db_menu(self):
        db_action_load = OnLoadItemsAction("load", self.ui.db_menu, self.base_items_widget.list_model,
                                           filepath_to_slide_tiles_descriptors_models_view_item)
        self.db_list_view_menu = ListViewMenu("list_view", self.ui.db_menu, self.base_items_widget)
        self.db_list_view_menu.item_mode_menu.update_funcs(
            item_to_pixmap_through_slideviewparams_factory(
                slide_tiles_descriptors_models_view_item_to_slide_view_params),
            slide_tiles_descriptors_models_view_item_to_str,
            slide_tiles_descriptors_models_view_item_to_slide_view_params)

    def setup_results_menu(self):
        self.results_list_view_menu = ListViewMenu("list_view", self.ui.results_menu, self.result_items_widget)
        self.results_list_view_menu.item_mode_menu.update_funcs(
            item_to_pixmap_through_slideviewparams_factory(
                slide_tiles_descriptors_models_view_item_to_slide_view_params),
            slide_tiles_descriptors_models_view_item_to_str,
            slide_tiles_descriptors_models_view_item_to_slide_view_params)

    def setup_action_menu(self):
        select_all_db_models_action = MyAction("select all db_models", self.ui.menu_action, self.on_select_all_images)
        search_action = OnGetSelectedItemsDataAction("search in selected db_models", self.ui.menu_action,
                                                     self.base_items_widget.list_view,
                                                     self.on_search_action)

    def setup_base_items_widget(self):
        self.base_items_widget = self.ui.left_widget
        self.base_items_widget.list_view.setViewMode(QtWidgets.QListView.ListMode)
        if start_db_filepathes_to_slide_tiles_descriptors_models:
            items = [filepath_to_slide_tiles_descriptors_models_view_item(source) for source in
                     start_db_filepathes_to_slide_tiles_descriptors_models]
            self.base_items_widget.list_model.update_items(items)

        self.base_items_widget.list_model.update_role_func(SlideListModel.DecorationSizeOrRatioRole,
                                                           decoration_size_func_factory(
                                                               self.base_items_widget.list_view,
                                                               *base_items_icon_max_size_or_ratio))

    def setup_query_viewer(self):
        self.query_viewer: SlideViewer = self.ui.right_widget
        if start_query_slide_path:
            slide_view_params: SlideViewParams = SlideViewParams(start_query_slide_path)
            slide_view_params.selected_rect_0_level = start_selection_rect
            self.query_viewer.load(slide_view_params)

    def setup_result_items_widget(self):
        self.result_items_widget = self.ui.bottom_widget
        self.result_items_widget.list_view.setViewMode(QtWidgets.QListView.IconMode)
        self.result_items_widget.list_view.setSelectionMode(QAbstractItemView.NoSelection)
        self.result_items_widget.list_model.update_role_func(SlideListModel.DecorationSizeOrRatioRole,
                                                             decoration_size_func_factory(
                                                                 self.result_items_widget.list_view,
                                                                 *result_items_icon_max_size_or_ratio))

    def on_select_all_images(self):
        self.base_items_widget.list_view.selectAll()

    def on_search_action(self, selected_slide_tiles_descriptors_models_view_items: Iterable[
        SlideTilesDescriptorsModelsViewItem]):
        if not self.query_viewer.slide_view_params.selected_rect_0_level:
            QMessageBox.question(self, 'Error', "No query rect selected", QMessageBox.Ok)
            return

        slide_tiles_descriptors_models = []
        for selected_slide_tiles_descriptors_models_view_item in selected_slide_tiles_descriptors_models_view_items:
            for slide_tiles_descriptors_model in selected_slide_tiles_descriptors_models_view_item.slide_tiles_descriptors_models:
                slide_tiles_descriptors_models.append(slide_tiles_descriptors_model)

        if not slide_tiles_descriptors_models:
            QMessageBox.question(self, 'Error', "No db_models selected", QMessageBox.Ok)
            return

        n_selected_images = len(selected_slide_tiles_descriptors_models_view_items)
        chosen_tiles_descriptors_models = self.choose_tiles_descriptors_model(slide_tiles_descriptors_models,
                                                                              n_selected_images)
        if not chosen_tiles_descriptors_models:
            QMessageBox.question(self, 'Error', "No tiles_descriptors_model selected", QMessageBox.Ok)
            return

        self.statusBar().showMessage("Searching...")
        self.result_items_widget.list_model.update_items([])

        selected_rect_0_level_int = [int(x) for x in self.query_viewer.slide_view_params.selected_rect_0_level]
        query_tile_descriptor_model = build_query_tiles_descriptors_model(
            self.query_viewer.slide_view_params.slide_path, selected_rect_0_level_int,
            chosen_tiles_descriptors_models[0])
        print("query_tile_descriptor_model", query_tile_descriptor_model)

        result_items = []
        query_descriptor = computer_utils.compute_model(query_tile_descriptor_model, force=True)
        query_descriptor = list(query_descriptor)[0]
        query_descriptor_model = {
            "type": "list",
            "list": [query_descriptor]
        }
        for chosen_tiles_descriptors_model in chosen_tiles_descriptors_models:
            start_datetime = datetime.now()
            distance_model = generate_distance_matrix_model(query_descriptor_model, chosen_tiles_descriptors_model)
            distances = computer_utils.compute_model(distance_model, force=True)
            distances = list(distances)
            distances = np.array(distances).squeeze()
            result_item = build_result_slide_tiles_descriptors_models_view_item(distances,
                                                                                chosen_tiles_descriptors_model)
            result_items.append(result_item)
        self.statusBar().showMessage("Searching done. Visualization might take several seconds")
        self.result_items_widget.list_model.update_items(result_items)

        # nearest_indices_model = generate_nearest_indices_model(distance_model, -1, "computed/nearest_indices.hdf5")
        # nearest_indices = computer_utils.compute_model(nearest_indices_model)[0]
        # print(nearest_indices)

    def choose_tiles_descriptors_model(self, tiles_descriptors_models, n_selected_images):
        str__model = {}
        for tiles_descriptors_model in tiles_descriptors_models:
            str_ = tiles_descriptors_model_to_str(tiles_descriptors_model)
            models = str__model.get(str_, [])
            models.append(tiles_descriptors_model)
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
