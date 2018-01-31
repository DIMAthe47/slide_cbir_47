import os

import json_utils
from cbir_core.computer import model_utils
from cbir_core.computer.computer_utils import compute_model, compute_models
from model_generators import generate_image_model, generate_rect_tiles_model, generate_tiling_model, \
    generate_histogram_model, generate_rgbapilimage_to_rgbpilimage_model, generate_pilimage_to_matrix_model
import openslide

from model_generators.descriptor_model_generators import generate_models_array, descriptor_type__model_generator
from model_generators.image_transform_model_generators import generate_pilimage_to_resizedpilimage_model


def generate_slide_tiling_model_item(slide_path, descriptor_model, level=0, tile_size=(224, 224), db_path=None,
                                     ds_name=None):
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


def generate_slide_tiling_models(slide_path, descriptor_models, level=0, tile_size=(224, 224), db_path=None):
    slide_tiling_model_items = []
    for descriptor_model in descriptor_models:
        slide_tiling_model_item = generate_slide_tiling_model_item(slide_path, descriptor_model, level, tile_size,
                                                                   db_path)
        slide_tiling_model_items.append(slide_tiling_model_item)

    slide_tiling_models = {"slide_tiling_models": slide_tiling_model_items, "slide_path": slide_path}
    return slide_tiling_models


def process_slide_tiling_models(slide_tiling_models):
    slide_tiling_model_items = slide_tiling_models["models"]
    compute_models(slide_tiling_model_items)


def main():
    # slide_path = r'C:\Users\DIMA\Downloads\JP2K-33003-1.svs'
    # slide_path = r'C:\Users\DIMA\Downloads\CMU-1-Small-Region.svs'
    slide_path = r'C:\Users\DIMA\Downloads\11096.svs'
    # slide_path = r'C:\Users\dmitriy\Downloads\JP2K-33003-1.svs'
    # slide_path = r'C:\Users\dmitriy\Downloads\CMU-1-Small-Region.svs'

    descriptor_models = [
        {
            "name": "histogram",
            "params": {
                "n_bins": 64,
                "density": True,
                "dtype": "int"
            },
        },
        {
            "name": "histogram",
            "params": {
                "n_bins": 128,
                "density": True,
                "dtype": "int"
            },
        },
        {
            "name": "histogram",
            "params": {
                "n_bins": 256,
                "density": True,
                "dtype": "int"
            },
        },
        {
            "name": "vgg16",
            "params": {
                "layer_name": "fc1",
                "chunk_size": 30
            },
        },
        {
            "name": "vgg16",
            "params": {
                "layer_name": "fc2",
                "chunk_size": 30
            },
        },
    ]

    img_name = os.path.splitext(os.path.basename(slide_path))[0]
    db_models = generate_models_array(tiling_model, descriptor_models, "temp/computed/{0}.hdf5".format(img_name))
    print(db_models)
    json_utils.write("temp/db_models/{0}.json".format(img_name), db_models)
    json_utils.write("temp/db_models/{0}-copy.json".format(img_name), db_models)

    compute_models(db_models)


if __name__ == '__main__':
    main()
