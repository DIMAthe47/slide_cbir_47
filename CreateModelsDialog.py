import typing

from PyQt5 import QtCore

from PyQt5.QtWidgets import QDialog, QWidget, QGroupBox, QHBoxLayout, QLineEdit, QFormLayout, QDialogButtonBox, \
    QVBoxLayout


class CreateModelsDialog(QDialog):
    def __init__(self, parent: typing.Optional[QWidget] = ...,
                 flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = ...) -> None:
        super().__init__(parent)

        formGroupBox = QGroupBox("Tile params")
        horizontal_layout = QHBoxLayout(formGroupBox)
        tile_w = QLineEdit(str(500))
        tile_h = QLineEdit(str(500))
        horizontal_layout.addWidget(tile_w)
        horizontal_layout.addWidget(tile_h)
        layout = QFormLayout(formGroupBox)
        layout.addRow("tile_size: ", horizontal_layout)
        formGroupBox.setLayout(layout)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        def on_set_tile_size():
            try:
                w = int(tile_w.text())
            except:
                w = float(tile_w.text())
            try:
                h = int(tile_h.text())
            except:
                h = float(tile_h.text())
            self.close()

        buttonBox.accepted.connect(on_set_tile_size)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(formGroupBox)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)
