import os
from slide_cbir_47.precompute.compute_config import models_dir

# start_query_slide_path = r'C:\Users\dmitriy\Downloads\JP2K-33003-1.svs'
# start_query_slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'

start_query_slide_path = r'C:\Users\DIMA\PycharmProjects\slide_cbir_47\temp\slides\Aperio\JP2K-33003-1.svs'
# start_query_slide_path=None

start_db_filepathes_to_models = [os.path.join(models_dir, f) for f in os.listdir(models_dir)]

start_selection_rect = (0, 0, 500, 500)

main_window_size = (1500, 1000)

result_items_icon_max_size_or_ratio = (0.25, 1.0)
base_items_icon_max_size_or_ratio = (0.5, 0.5)

cache_size_in_kb = 700 * 10 ** 3
