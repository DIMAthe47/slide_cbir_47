# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cbir.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(799, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.top_layout = QtWidgets.QHBoxLayout()
        self.top_layout.setObjectName("top_layout")
        self.left_widget = SimpleListView(self.centralwidget)
        self.left_widget.setObjectName("left_widget")
        self.top_layout.addWidget(self.left_widget)
        self.right_widget = SlideViewer3(self.centralwidget)
        self.right_widget.setObjectName("right_widget")
        self.top_layout.addWidget(self.right_widget)
        self.top_layout.setStretch(0, 1)
        self.top_layout.setStretch(1, 1)
        self.verticalLayout_2.addLayout(self.top_layout)
        self.bottom_widget = SimpleListView(self.centralwidget)
        self.bottom_widget.setObjectName("bottom_widget")
        self.verticalLayout_2.addWidget(self.bottom_widget)
        self.verticalLayout_2.setStretch(0, 1)
        self.verticalLayout_2.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 799, 20))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))

from app3 import SlideViewer3
from tiles_descriptors_models_view import SimpleListView
