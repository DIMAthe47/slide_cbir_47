import json_utils
from cbir_core.computer.computer_utils import compute_model
from model_generators import generate_image_model, generate_rect_tiles_model, generate_tiling_model, \
    generate_histogram_model, generate_rgbapilimage_to_rgbpilimage_model, generate_pilimage_to_matrix_model
import openslide


def main():
    slide_path = r'C:\Users\DIMA\Downloads\JP2K-33003-1.svs'
    slide = openslide.OpenSlide(slide_path)
    slide_size = slide.level_dimensions[0]
    image_model = generate_image_model(slide_path)
    tile_size = (300, 300)
    rect_tiles_model = generate_rect_tiles_model(slide_size, tile_size, tile_size)
    tiling_model = generate_tiling_model(rect_tiles_model, image_model, 1)
    tiling_model = generate_rgbapilimage_to_rgbpilimage_model(tiling_model)
    tiling_model = generate_pilimage_to_matrix_model(tiling_model)

    histogram_model = generate_histogram_model(tiling_model, 128, True, "temp/computed/descriptors.hdf5")
    compute_model(histogram_model)

    db_models = [histogram_model]
    json_utils.write("temp/db_models/histogram_models1.json", db_models)
    json_utils.write("temp/db_models/histogram_models2.json", db_models)


if __name__ == '__main__':
    main()
