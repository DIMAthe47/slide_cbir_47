import os

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

# slide_pathes = [
#     r'C:\Users\DIMA\Downloads\svs\JP2K-33003-1.svs',
#     r'C:\Users\DIMA\Downloads\svs\CMU-1-JP2K-33005.svs',
#     r'C:\Users\DIMA\Downloads\svs\CMU-1.svs',
# ]
slide_dir = r"C:\Users\DIMA\PycharmProjects\slide_cbir_47\downloads\images"
slide_pathes = [os.path.join(slide_dir, f) for f in os.listdir(slide_dir)]


def get_path_for_computed_hdf5(slide_path):
    slide_name = os.path.splitext(os.path.basename(slide_path))[0]
    computed_path = "temp/computed/{}.hdf5".format(slide_name)
    return computed_path


def get_path_for_model_json(slide_path):
    slide_name = os.path.splitext(os.path.basename(slide_path))[0]
    model_path = "temp/db_models/{}.json".format(slide_name)
    return model_path
