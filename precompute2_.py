import os

import json_utils
from cbir_core.computer.computer_utils import compute_model, compute_models
from model_generators import generate_image_model, generate_rect_tiles_model, generate_tiling_model, \
    generate_histogram_model, generate_rgbapilimage_to_rgbpilimage_model, generate_pilimage_to_matrix_model
import openslide

from model_generators.descriptor_model_generators import generate_models_array


def main():
    slide_path = r'C:\Users\DIMA\Downloads\JP2K-33003-1.svs'
    slide = openslide.OpenSlide(slide_path)
    slide_size = slide.level_dimensions[0]
    image_model = generate_image_model(slide_path)
    tile_size = (224, 224)
    rect_tiles_model = generate_rect_tiles_model(slide_size, tile_size, tile_size)
    tiling_model = generate_tiling_model(rect_tiles_model, image_model, 1)
    tiling_model = generate_rgbapilimage_to_rgbpilimage_model(tiling_model)
    tiling_model = generate_pilimage_to_matrix_model(tiling_model)

    descriptor_models = [
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
