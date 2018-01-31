from cbir_core.computer.model_utils import find_image_path
from slide_viewer_47.common.slide_view_params import SlideViewParams


class DescriptorTileModels():
    def __init__(self, models) -> None:
        super().__init__()
        img_path = find_image_path(models[0])
        self.slide_view_params = SlideViewParams(img_path)
        self.slide_tiling_models = {"slide_tiling_models": models, "slide_path": img_path}
