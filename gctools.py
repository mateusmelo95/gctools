# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GC TOOLS

 AI Plugin for Qgis with all kind of info
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2023-10-06
        git sha              : $Format:%H$
        copyright            : (C) 2023 by Mateus Melo Siqueira/Remis Balaniuk
        email                : mms.projects0@gmail.com/remis.balaniuk@yahoo.com.br
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtWidgets import QToolButton, QMenu, QLineEdit, QLabel, QDialog, QPushButton, QCheckBox, QGridLayout
from qgis.PyQt.QtCore import QObject, Qt, QSize
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsWkbTypes, QgsGeometry, QgsPoint, QgsProject, QgsMapLayerProxyModel
from qgis.gui import QgsRubberBand, QgsMapLayerComboBox, QgsFieldComboBox
from PyQt5.QtWidgets import QTabWidget, QFrame,QAbstractItemView,  QMessageBox, QShortcut, QDockWidget, QComboBox, QLineEdit, QTableWidget, QTableWidgetItem, QCheckBox, QGridLayout, QLabel, QWidget, QSizePolicy,QSpacerItem, QPushButton
from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtGui import QColor, QCursor, QPixmap, QIcon, QImage
from PyQt5.QtCore import QThread, pyqtSignal
import base64
import io
from PIL import Image, ImageQt
from functools import partial

from .mods.ai_gis.ai_gis import AIGIS
from .mods.sample.sample import SAMPLE
from .mods.validation.validation import VALID
from .mods.about.about_dialog import ABOUTDialog
from .resources import *
# Import the code for the dialog
from .gctools_dialog import GCTOOLSDialog
import os.path
import time


class Worker(QThread):
    def __init__(self, plugin_dir,iface):
        QThread.__init__(self)
        self.stp = False
        self.plugin_dir = plugin_dir
        self.iface = iface
    up_list = pyqtSignal(list)

    def run(self):
        if not self.stp:
            pass



class GCTOOLS:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GCTOOLS{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []

        self.toolbar = self.iface.addToolBar(u'GCTOOLS')
        self.toolbar.setObjectName(u'gctools_bar')
        self.toolbar.setFixedHeight(40)
        self.toolbar.setIconSize(QSize(35, 35))

        #self.menu = self.tr(u'&MMSD GIS')

        self.menu = None
        self.menugc = QMenu(self.iface.mainWindow())
        self.menugc.setObjectName(u'gctools_menu')
        self.menugc.setTitle(u'GCTOOLS')
        self.menuBar = self.iface.mainWindow().menuBar()
        self.menuBar.insertMenu(self.iface.firstRightStandardMenu().menuAction(), self.menugc)

        #self.menuLogButton = self.createToolButton(self.toolbar, u'LOGIN', False)
        self.menuAiGisButton = self.createToolButton(self.toolbar, u'AIGIS', False)
        self.menuSampleButton = self.createToolButton(self.toolbar, u'SAMPLE', False)
        self.menuValidButton = self.createToolButton(self.toolbar, u'VALID', False)

        self.toolbar.addSeparator()
        #self.menuROSButton = self.createToolButton(self.toolbar, u'ROS', False)


        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GCTOOLS', message)

    def createToolButton(self, parent, text, setpop=True):
        """
        Creates a tool button (pop up menu)
        """
        button = QToolButton(parent)
        button.setObjectName(text)
        button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        if setpop:
            button.setPopupMode(QToolButton.MenuButtonPopup)
        parent.addWidget(button)
        self.actions.append(button)
        return button

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        #add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
        parentMenu = None,
        withShortcut=False,
        tooltip = None,
        parentToolbar = None,
        parentButton = None,
        isCheckable = False):
        """Add a toolbar icon to the InaSAFE toolbar.
        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str
        :param text: Text that should be shown in menu items for this action.
        :type text: str
        :param callback: Function to be called when the action is triggered.
        :type callback: function
        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool
        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool
        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool
        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str
        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget
        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.
        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        #if add_to_menu:
            #self.menu.addAction(action)
        if parentMenu:
            parentMenu.addAction(action)
        if withShortcut:
            self.iface.registerMainWindowAction(action, '')
        if isCheckable:
            action.setCheckable(True)
        if tooltip:
            action.setToolTip(tooltip)
        if parentToolbar:
            parentToolbar.addAction(action)
        if parentButton:
            parentButton.addAction(action)
        self.actions.append(action)
        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""


        icon_path_aigis = ':/plugins/gctools/icons/aigis.png'
        self.action_aigis = self.add_action(
            icon_path_aigis,
            text=u'AIGIS',
            callback=self.run_ai_gis,
            # add_to_menu=False,
            add_to_toolbar=False,
            # withShortcut=False,
            parentToolbar=self.menugc,
            isCheckable=False
        )
        self.menuAiGisButton.addAction(self.action_aigis)
        self.menuAiGisButton.setDefaultAction(self.action_aigis)

        icon_path_sample = ':/plugins/gctools/icons/sample.png'
        self.action_sample = self.add_action(
            icon_path_sample,
            text=u'SAMPLE',
            callback=self.run_gcsample,
            # add_to_menu=False,
            add_to_toolbar=False,
            # withShortcut=False,
            parentToolbar=self.menugc,
            isCheckable=False
        )
        self.menuSampleButton.addAction(self.action_sample)
        self.menuSampleButton.setDefaultAction(self.action_sample)

        icon_path_valid = ':/plugins/gctools/icons/valid.png'
        self.action_valid = self.add_action(
            icon_path_valid,
            text=u'VALID',
            callback=self.run_validation,
            # add_to_menu=False,
            add_to_toolbar=False,
            # withShortcut=False,
            parentToolbar=self.menugc,
            isCheckable=False
        )
        self.menuValidButton.addAction(self.action_valid)
        self.menuValidButton.setDefaultAction(self.action_valid)


        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        for action in self.actions:
            try:
                self.iface.removePluginMenu(
                    "gctools_menu",
                    action)
                self.iface.removeToolBarIcon(action)
                self.iface.unregisterMainWindowAction(action)
            except:
                pass
        if self.menugc is not None:
            self.menuBar.removeAction(self.menugc.menuAction())
        del self.menugc
        del self.toolbar

    def login(self):
        print("teste")

    def run_gcsample(self):
        """Run method that performs all the real work"""
       
        self.sample = SAMPLE(self.iface,self)
        self.sample.run()



    def run_ai_gis(self):
        self.ai_gis = AIGIS(self.iface,self)
        self.ai_gis.run()

    def run_validation(self):
        self.valid_samples = VALID(self.iface,self)
        self.valid_samples.run()

    def signal_worker(self,data):
        print("teste_signal",data)

    def start_worker(self):
        print("loggin") #
        self.worker = Worker(self.plugin_dir,self.iface)
        self.worker.stp = False
        self.worker.up_list.connect(self.signal_worker)
        self.worker.start()


    def stop_worker(self):
        print("stopped loggin")
        self.worker.stp = True

    def run_box(self):
        self.box_dlg = QDialog()