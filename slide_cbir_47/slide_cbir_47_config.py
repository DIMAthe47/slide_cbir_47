import os
from slide_cbir_47.precompute.compute_config import models_dir

"""
start_query_slide_path - on startup path to slide to view as source for query tile
start_db_filepathes_to_slide_tiles_descriptors_models - on startup paths to json-models
start_selection_rect - on startup selected rect on query-slide
"""

# start_query_slide_path = r'C:\Users\DIMA\PycharmProjects\slide_cbir_47\temp\slides\Aperio\JP2K-33003-1.svs'
start_query_slide_path = r"C:\Users\dmitriy\PycharmProjects\slide_cbir_47\temp\slides\Aperio\JP2K-33003-1.svs"

start_db_filepathes_to_slide_tiles_descriptors_models = [os.path.join(models_dir, f) for f in os.listdir(models_dir)]

start_selection_rect = (0, 0, 500, 500)

# main_window_size = (1200, 800)
main_window_size = None

# result_items_icon_max_size_or_ratio = (0.25, 0.5)
# base_items_icon_max_size_or_ratio = (0.5, 0.5)
base_items_icon_max_size_or_ratio = (200, 200)
result_items_icon_max_size_or_ratio = (300, 300)

cache_size_in_kb = 700 * 10 ** 3
