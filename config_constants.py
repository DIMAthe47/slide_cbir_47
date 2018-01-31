from PyQt5.QtCore import QRectF

start_query_slide_path = r'C:\Users\dmitriy\Downloads\JP2K-33003-1.svs'
# start_query_slide_path = '/home/dimathe47/Downloads/JP2K-33003-1.svs'
# start_query_slide_path = r'C:\Users\DIMA\Downloads\JP2K-33003-1.svs'

# start_db_filepathes_to_models = ["/home/dimathe47/PycharmProjects/slide_cbir_47/models/array0.json",
#                               "/home/dimathe47/PycharmProjects/slide_cbir_47/models/array1.json"]

start_db_filepathes_to_models = [
    # "temp/db_models/JP2K-33003-1.json",
    # "temp/db_models/CMU-1-Small-Region.json",
    # "temp/db_models/JP2K-33003-1-copy.json",
]
start_db_filepathes_to_models = [
    r"C:\Users\dmitriy\PycharmProjects\slide_cbir_47\precompute\temp\db_models\19403.json"
]

start_selection_rect = (0, 0, 500, 500)

main_window_size = (1500, 1000)

result_items_icon_max_size_or_ratio = (200, 0.5)
base_items_icon_max_size_or_ratio = (100, 0.25)

cache_size_in_kb = 700 * 10 ** 3
