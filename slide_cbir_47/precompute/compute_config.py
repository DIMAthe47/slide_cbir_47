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
    # {
    #     "name": "histogram",
    #     "params": {
    #         "n_bins": 128,
    #         "density": True,
    #         "dtype": "int"
    #     },
    # },
    # {
    #     "name": "lbp",
    #     "params": {
    #         "P": 8,
    #         "R": 1,
    #         "method": "uniform",
    #         "dtype": "int"
    #     },
    # },
    {
        "name": "vgg16",
        "params": {
            "layer_name": "fc1",
            "chunk_size": 30
        },
    },
    # {
    #     "name": "vgg16",
    #     "params": {
    #         "layer_name": "fc2",
    #         "chunk_size": 30
    #     },
    # },
]

tile_size = (224, 224)

temp_folder = r"C:\Users\dmitriy\PycharmProjects\slide_cbir_47\temp"


def get_path_for_computed_hdf5(slide_path):
    slide_name = os.path.splitext(os.path.basename(slide_path))[0]
    computed_path = os.path.join(temp_folder, "computed\Aperio\{}.hdf5".format(slide_name))
    return computed_path


def get_path_for_model_json(slide_path):
    slide_name = os.path.splitext(os.path.basename(slide_path))[0]
    model_path = os.path.join(temp_folder, "db_models\Aperio\{}.json".format(slide_name))
    return model_path


slide_dir = os.path.join(temp_folder, "slides\Aperio")
slide_pathes = [os.path.join(slide_dir, f) for f in os.listdir(slide_dir)]
models_dir = os.path.join(temp_folder, "db_models\Aperio")
