import numpy as np
from PyQt5.QtGui import QColor
from tiled_pixmap import TiledPixmap


class TilesDistancesIndicatorTiledPixmap(TiledPixmap):
    def __init__(self, img, tile_rects, distances) -> None:
        self.distances = distances
        self.normalized_distances = distances / np.max(distances)
        qcolors = [QColor(0, 255, 0, normalized_distance * 128) for normalized_distance in
                   self.normalized_distances]
        super().__init__(img, tile_rects, qcolors)