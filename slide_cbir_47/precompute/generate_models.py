import json_utils
from model_generators import generate_image_model, generate_rect_tiles_model, generate_tiling_model, \
    generate_rgbapilimage_to_rgbpilimage_model, generate_pilimage_to_matrix_model
import openslide

from model_generators.descriptor_model_generators import descriptor_type__model_generator
from model_generators.image_transform_model_generators import generate_pilimage_to_resizedpilimage_model
from slide_cbir_47.precompute.compute_config import slide_pathes, descriptor_models, get_path_for_computed_hdf5, \
    get_path_for_model_json, tile_size


def generate_slide_tiling_model_item(slide_path, descriptor_model, tile_size, db_path=None,
                                     ds_name=None):
    level = 0
    slide = openslide.open_slide(slide_path)
    slide_size = slide.level_dimensions[level]
    image_model = generate_image_model(slide_path)
    downsample = slide.level_downsamples[level]
    rect_tiles_model = generate_rect_tiles_model(slide_size, tile_size, tile_size)
    tiling_model = generate_tiling_model(rect_tiles_model, image_model, downsample)
    tiling_model = generate_rgbapilimage_to_rgbpilimage_model(tiling_model)
    tiling_model = generate_pilimage_to_resizedpilimage_model(tiling_model, tile_size)
    tiling_model = generate_pilimage_to_matrix_model(tiling_model)

    model_generator = descriptor_type__model_generator[descriptor_model["name"]]
    slide_tiling_model = model_generator(tiling_model, **descriptor_model["params"], db_path=db_path, ds_name=ds_name)
    return slide_tiling_model


def generate_slide_tiling_models(slide_path, descriptor_models, tile_size, db_path=None):
    slide_tiles_descriptors_models = []
    level = 0
    for descriptor_model in descriptor_models:
        slide_tiling_model_item = generate_slide_tiling_model_item(slide_path, descriptor_model, level, tile_size,
                                                                   db_path)
        slide_tiles_descriptors_models.append(slide_tiling_model_item)

    slide_tiling_models = {"slide_tiles_descriptors_models": slide_tiles_descriptors_models, "slide_path": slide_path}
    return slide_tiling_models


def main():
    for slide_path in slide_pathes:
        computed_path = get_path_for_computed_hdf5(slide_path)
        model_path = get_path_for_model_json(slide_path)
        slide_tiling_models = generate_slide_tiling_models(slide_path, descriptor_models, tile_size,
                                                           db_path=computed_path)
        json_utils.write(model_path, slide_tiling_models)


if __name__ == '__main__':
    main()
