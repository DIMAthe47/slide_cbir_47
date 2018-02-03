import os

import numpy as np
import openslide

import json_utils
from cbir_core.computer import model_utils, computer_utils
from cbir_core.computer.model_utils import find_image_path, find_downsample
from slide_cbir_47.model.slide_tiles_descriptors_models_view_item import SlideTilesDescriptorsModelsViewItem
from slide_viewer_47.common.slide_view_params import SlideViewParams


def build_item_text(tiles_descriptors_model: dict):
    img_path = find_image_path(tiles_descriptors_model)
    rect_tiles_model = model_utils.find_rect_tiles_model(tiles_descriptors_model)
    rect_size = rect_tiles_model["computer_func_params"]["rect_size"]
    tile_size = rect_tiles_model["computer_func_params"]["tile_size"]
    img_name = os.path.basename(img_path)
    media_object_text = "img_name: {}\nimg_size: {}\ntile_size: {}".format(img_name, rect_size, tile_size)
    return media_object_text


def slide_tiles_descriptors_models_view_item_to_slide_view_params(item: SlideTilesDescriptorsModelsViewItem):
    return item.slide_view_params


def slide_tiles_descriptors_models_view_item_to_str(item: SlideTilesDescriptorsModelsViewItem):
    tiles_descriptors_model = item.slide_tiles_descriptors_models[0]
    return build_item_text(tiles_descriptors_model)


def tiles_descriptors_model_to_str(tiles_descriptors_model: dict):
    rect_tiles_model = model_utils.find_rect_tiles_model(tiles_descriptors_model)
    rect_tiles_size = rect_tiles_model["computer_func_params"]["tile_size"]
    downsample = find_downsample(tiles_descriptors_model)
    descriptor_type = tiles_descriptors_model["name"]
    str_ = "descriptor_type: {}, rect: ({},{}), downsample: {}".format(descriptor_type,
                                                                       *rect_tiles_size, downsample)
    return str_


def filepath_to_slide_tiles_descriptors_models_view_item(filepath):
    slide_tiles_descriptors_models_container = json_utils.read(filepath)
    slide_tiles_descriptors_models = slide_tiles_descriptors_models_container["slide_tiles_descriptors_models"]
    slide_view_params = SlideViewParams(slide_tiles_descriptors_models_container["slide_path"])
    return SlideTilesDescriptorsModelsViewItem(slide_tiles_descriptors_models, slide_view_params)


def build_result_slide_tiles_descriptors_models_view_item(distances: np.ndarray, tiles_descriptors_model: dict):
    # normalized_distances = distances/ np.max(distances)
    normalized_distances = (distances - np.min(distances)) / (np.max(distances) - np.min(distances))
    # alphas = [128 - 128 * dist for dist in normalized_distances]
    # alphas = [128 * 128 ** (-dist) for dist in normalized_distances]
    alphas = 128 ** (1 - normalized_distances)
    # colors = [(0, 255, 0, int(alpha)) for alpha in alphas]

    rect_tiles_model = model_utils.find_rect_tiles_model(tiles_descriptors_model)
    rect_tiles = list(computer_utils.compute_model(rect_tiles_model))
    slide_path = find_image_path(tiles_descriptors_model)
    slide_view_params = SlideViewParams(slide_path, grid_rects_0_level=rect_tiles, grid_color_alphas_0_level=alphas,
                                        grid_visible=True)
    item = SlideTilesDescriptorsModelsViewItem([tiles_descriptors_model], slide_view_params)
    return item


def build_query_tiles_descriptors_model(slide_path, tile_rect, tiles_descriptor_model):
    # important. Note that in perspective query can come from outside the system - in this case we will have no access to slide or slide_path
    slide = openslide.OpenSlide(slide_path)
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
