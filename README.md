# slide_cbir_47
A pyqt5 GUI for CBIR in whole-slide images with [Openslide](http://openslide.org).

Project depends on:
- [cbir](https://github.com/DIMAthe47/cbir)
- [slide_viewer_47](https://github.com/DIMAthe47/slide_viewer_47)
- [slide_list_view_47](https://github.com/DIMAthe47/slide_list_view_47)

#### Implemented CBIR-technique:

##### Precompute stage. For each db-slide (slide from collection of slides you want to search):
- slice each db-slide image into tiles
- compute descriptor of some type for each tile 

##### Search stage. For a given query-tile (tile from some slide image):
- compute descriptor of some type (corresponding to types selected in precompute stage)
- exhaustively compare each descriptor of each db-slide with descriptor of query-tile
- visualize distances between db-tiles and query-tile


#### Use:
- set up [configuration-file](/slide_cbir_47/precompute/compute_config.py) (configuring descriptor types, tile size, path to db-slides, path to descriptors to be computed)
- use [download_utils](/slide_cbir_47/download_utils) to load some whole-slide images if you havent
- [generate json-models](/slide_cbir_47/precompute/generate_models.py) for future computation 
- [run descriptors computation](/slide_cbir_47/precompute/compute_models_parallel.py) (time-consuming)(very time-consuming if you selected vgg16 descriptor type)
- [configure ui-specific options](/slide_cbir_47/slide_cbir_47_config.py)
- run [gui app](/slide_cbir_47/slide_cbir_47_app.py)
- select collection of db-slides to search in (left pane)
- select tile in query-slide viewer (right pane)
- select in menu "actions"->"search in selected db_models"
- search results (represented as intensities proportional to distances between tiles) will be populated (bottom pane)

###### Notes:
- for any db-slide or result-slide there is an extended view mode (activated by doubleclick)
where you can zoom it and toggle grid visibility.
- descriptors are stored in hdf5 files.

Examples of whole-slide images can be downloaded from [openslide-testdata](http://openslide.cs.cmu.edu/download/openslide-testdata/) page.

Screenshot of slide_cbir_47:

![screenshot](/slide_cbir_47_app_screen_2.png)
