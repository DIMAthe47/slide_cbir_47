import os

import json_utils
from cbir_core.computer.computer_utils import compute_model, compute_models

from precompute.precompute_config import slide_pathes, get_path_for_model_json


def process_slide_tiling_models(slide_tiling_models):
    slide_tiling_model_items = slide_tiling_models["models"]
    compute_models(slide_tiling_model_items)


def main():
    for slide_path in slide_pathes:
        model_path = get_path_for_model_json(slide_path)
        slide_tiling_models = json_utils.read(model_path)
        process_slide_tiling_models(slide_tiling_models)



if __name__ == '__main__':
    main()
