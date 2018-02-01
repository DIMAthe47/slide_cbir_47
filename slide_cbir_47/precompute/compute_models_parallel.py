from concurrent.futures import ProcessPoolExecutor

import json_utils
from cbir_core.computer.computer_utils import compute_model

from slide_cbir_47.precompute.compute_config import slide_pathes, get_path_for_model_json

from concurrent.futures import wait

import multiprocessing


def process_slide_tilimg_models_separate(slide_tiles_descriptors_models):
    """
    with 3gb only gpu on my machine I need to run only one process using gpu
    :param slide_tiles_descriptors_models:
    :return:
    """
    max_workers = 1

    futures = set()
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for model_item in slide_tiles_descriptors_models:
            future = executor.submit(process_slide_tiling_model_item, model_item)
            futures.add(future)

        done, not_done = wait(futures)
        print("done, not_done: ", done, not_done)


def process_slide_tiling_model_item(slide_tiling_model_item):
    compute_model(slide_tiling_model_item)


def main():
    futures = set()
    max_workers = multiprocessing.cpu_count() - 2

    models_for_gpu = []
    models_for_cpu = []
    for slide_path in slide_pathes:
        model_path = get_path_for_model_json(slide_path)
        slide_tiling_models = json_utils.read(model_path)
        for model_item in slide_tiling_models["slide_tiles_descriptors_models"]:
            if model_item["computer_func_name"] == "vgg16":
                models_for_gpu.append(model_item)
            else:
                models_for_cpu.append(model_item)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future = executor.submit(process_slide_tilimg_models_separate, models_for_gpu)
        futures.add(future)
        for model_item in models_for_cpu:
            future = executor.submit(process_slide_tiling_model_item, model_item)
            futures.add(future)

        done, not_done = wait(futures)
        print("done, not_done: ", done, not_done)


if __name__ == '__main__':
    main()
