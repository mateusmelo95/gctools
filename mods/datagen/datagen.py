# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AIGIS
                                 A QGIS plugin
 Modelos de inteligência artificial no Qgis
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-10-06
        git sha              : $Format:%H$
        copyright            : (C) 2023 by MMS
        email                : mateusmelosiqueira@gmail.com
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
from qgis.core import QgsProject, QgsLayerTreeLayer, QgsStyle, QgsProject, QgsCategorizedSymbolRenderer, QgsSymbol, QgsLineSymbol, QgsRendererCategory,QgsFeature, QgsField, QgsFeatureRequest,QgsWkbTypes, QgsGeometry, QgsPoint, QgsProject, QgsMapLayerProxyModel, QgsVectorLayer, QgsField, QgsVectorFileWriter, QgsRectangle
from qgis.gui import QgsRubberBand, QgsMapLayerComboBox, QgsFieldComboBox,QgsMapTool, QgsMapCanvas
from PyQt5.QtWidgets import QTabWidget, QFrame,QAbstractItemView,  QMessageBox, QShortcut, QFileDialog, QDockWidget, QComboBox, QLineEdit, QTableWidget, QTableWidgetItem, QCheckBox, QGridLayout, QLabel, QWidget, QSizePolicy,QSpacerItem, QPushButton
from qgis.PyQt.QtCore import Qt, QSize, QVariant
from qgis.PyQt.QtGui import QColor, QCursor, QPixmap, QIcon, QImage
from PyQt5.QtCore import QThread, pyqtSignal
from .datagen_dialog import DATAGENDialog
import os
from PIL import Image, ImageOps
Image.MAX_IMAGE_PIXELS = 10000000000
import random
import sqlite3
# import osr


class WorkerInference(QThread):
    def __init__(self, plugin_dir):
        QThread.__init__(self)
        self.stp = False
        self.plugin_dir = plugin_dir

    up_list = pyqtSignal(list)
    def run(self):
        self.transform()

    def transform(self):

        # Abra a imagem original
        imagem_original = Image.open("caminho_para_sua_imagem.jpg")

        # Defina o número de iterações (N)
        N = 10  # Altere para o número desejado de iterações

        # Execute o processo de data augmentation N vezes
        for i in range(N):
            # Crie uma cópia da imagem original para cada iteração
            imagem = imagem_original.copy()

            # Gere um ângulo de rotação aleatório (entre -45 e 45 graus)
            angulo = random.randint(-45, 45)

            # Realize a rotação com expansão para não cortar a imagem
            imagem_rotacionada = imagem.rotate(angulo, expand=True)

            # Realize o espelhamento horizontal aleatório
            if random.choice([True, False]):
                imagem_rotacionada = ImageOps.mirror(imagem_rotacionada)

            # Desloque o centro da imagem aleatoriamente
            x_offset = random.randint(-100, 100)  # Ajuste os valores conforme necessário
            y_offset = random.randint(-100, 100)  # Ajuste os valores conforme necessário
            imagem_transformada = Image.new("RGB", imagem_rotacionada.size, (0, 0, 0))  # Crie uma nova imagem preta
            imagem_transformada.paste(imagem_rotacionada, (x_offset, y_offset))

            # Defina o tamanho desejado para o corte (1280x1280)
            tamanho_corte = (1280, 1280)

            # Calcule a posição do corte para centralizar a imagem
            largura, altura = imagem_transformada.size
            esquerda = (largura - tamanho_corte[0]) // 2
            superior = (altura - tamanho_corte[1]) // 2
            direita = (largura + tamanho_corte[0]) // 2
            inferior = (altura + tamanho_corte[1]) // 2

            # Realize o corte da imagem
            imagem_final = imagem_transformada.crop((esquerda, superior, direita, inferior))

            # Salve a imagem transformada com um nome de arquivo único
            nome_arquivo_saida = f"{i}_imagem.jpg"
            imagem_final.save(nome_arquivo_saida)

        # Feche a imagem original
        imagem_original.close()


class DATAGEN:
    def __init__(self, iface, cls_main):

        # Save reference to the QGIS interface
        self.gctools = cls_main
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = self.gctools.plugin_dir

    def run(self):
        self.dlg = DATAGENDialog()
        self.dlg.show()

    def transform(self):
        pass

