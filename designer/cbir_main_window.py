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
        MainWindow.resize(794, 618)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.top_layout = QtWidgets.QHBoxLayout()
        self.top_layout.setContentsMargins(-1, -1, 0, -1)
        self.top_layout.setObjectName("top_layout")
        self.left_widget = MediaObjectWidget(self.centralwidget)
        self.left_widget.setObjectName("left_widget")
        self.top_layout.addWidget(self.left_widget)
        self.right_widget = SlideViewer(self.centralwidget)
        self.right_widget.setObjectName("right_widget")
        self.top_layout.addWidget(self.right_widget)
        self.verticalLayout_2.addLayout(self.top_layout)
        self.bottom_widget = MediaObjectWidget(self.centralwidget)
        self.bottom_widget.setObjectName("bottom_widget")
        self.verticalLayout_2.addWidget(self.bottom_widget)
        self.verticalLayout_2.setStretch(0, 4)
        self.verticalLayout_2.setStretch(1, 3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 794, 21))
        self.menubar.setObjectName("menubar")
        self.db_menu = QtWidgets.QMenu(self.menubar)
        self.db_menu.setObjectName("db_menu")
        self.query_menu = SlideViewerMenu(self.menubar)
        self.query_menu.setObjectName("query_menu")
        self.menu_action = QtWidgets.QMenu(self.menubar)
        self.menu_action.setObjectName("menu_action")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLoad_slide = QtWidgets.QAction(MainWindow)
        self.actionLoad_slide.setObjectName("actionLoad_slide")
        self.db_action_load = QtWidgets.QAction(MainWindow)
        self.db_action_load.setObjectName("db_action_load")
        self.actionSearch = QtWidgets.QAction(MainWindow)
        self.actionSearch.setObjectName("actionSearch")
        self.actionShow_query_tile = QtWidgets.QAction(MainWindow)
        self.actionShow_query_tile.setObjectName("actionShow_query_tile")
        self.action_search = QtWidgets.QAction(MainWindow)
        self.action_search.setObjectName("action_search")
        self.action_show_query_tile = QtWidgets.QAction(MainWindow)
        self.action_show_query_tile.setObjectName("action_show_query_tile")
        self.query_load_action = QtWidgets.QAction(MainWindow)
        self.query_load_action.setObjectName("query_load_action")
        self.action_select_all_images = QtWidgets.QAction(MainWindow)
        self.action_select_all_images.setObjectName("action_select_all_images")
        self.menu_action.addAction(self.action_select_all_images)
        self.menubar.addAction(self.db_menu.menuAction())
        self.menubar.addAction(self.query_menu.menuAction())
        self.menubar.addAction(self.menu_action.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.db_menu.setTitle(_translate("MainWindow", "db"))
        self.query_menu.setTitle(_translate("MainWindow", "query"))
        self.menu_action.setTitle(_translate("MainWindow", "actions"))
        self.actionLoad_slide.setText(_translate("MainWindow", "load_slide"))
        self.db_action_load.setText(_translate("MainWindow", "load"))
        self.actionSearch.setText(_translate("MainWindow", "search"))
        self.actionShow_query_tile.setText(_translate("MainWindow", "show query tile"))
        self.action_search.setText(_translate("MainWindow", "search"))
        self.action_show_query_tile.setText(_translate("MainWindow", "show query tile"))
        self.query_load_action.setText(_translate("MainWindow", "load"))
        self.action_select_all_images.setText(_translate("MainWindow", "select all images"))

from media_object_widget import MediaObjectWidget
from slide_viewer import SlideViewer
from slide_viewer_menu import SlideViewerMenu
