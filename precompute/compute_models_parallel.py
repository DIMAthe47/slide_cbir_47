import multiprocessing
import os
from concurrent.futures import ProcessPoolExecutor

import json_utils
from cbir_core.computer.computer_utils import compute_model, compute_models

from precompute.precompute_config import slide_pathes, get_path_for_model_json

from concurrent.futures import wait


def process_slide_tiling_models(slide_tiling_models):
    slide_tiling_model_items = slide_tiling_models["models"]
    compute_models(slide_tiling_model_items)
    print("slide_tiling_models for slide done: {}"(slide_tiling_model_items["slide_path"]))


def main():
    futures = set()
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count() - 1) as executor:
        for slide_path in slide_pathes:
            model_path = get_path_for_model_json(slide_path)
            slide_tiling_models = json_utils.read(model_path)
            future = executor.submit(process_slide_tiling_models, slide_tiling_models)
            futures.add(future)

        done, not_done = wait(futures)
        print("done,not_done: {}, {}", done, not_done)


if __name__ == '__main__':
    main()
