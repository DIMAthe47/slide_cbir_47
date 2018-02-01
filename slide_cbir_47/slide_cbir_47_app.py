import sys
from PyQt5.QtGui import QPixmapCache
from PyQt5.QtWidgets import QApplication
from slide_cbir_47.slide_cbir_47_config import cache_size_in_kb
from slide_cbir_47.widgets.slide_cbir_main_window import CbirMainWindow


def excepthook(excType, excValue, tracebackobj):
    print(excType, excValue, tracebackobj)


sys.excepthook = excepthook


def main():
    app = QApplication(sys.argv)
    QPixmapCache.setCacheLimit(cache_size_in_kb)
    QPixmapCache.clear()
    win = CbirMainWindow()
    win.show()
    win.after_show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
