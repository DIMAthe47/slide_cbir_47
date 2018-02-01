from cbir_core.computer.model_utils import find_image_path
from slide_viewer_47.common.slide_view_params import SlideViewParams


class SlideTilesDescriptorsModelsViewItem():
    def __init__(self, slide_tiles_descriptors_models, slide_view_params) -> None:
        super().__init__()
        self.slide_tiles_descriptors_models = slide_tiles_descriptors_models
        self.slide_view_params = slide_view_params
