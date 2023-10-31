from qgis.core import QgsMapLayerProxyModel, QgsProject, QgsVectorLayer, QgsFeatureRequest, QgsField, QgsFeature
from PyQt5.QtCore import QVariant
import random
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QFormLayout, QPushButton, QComboBox
from qgis.gui import QgsMapLayerComboBox




class VALID:
    def __init__(self, iface, cls_main):
        # Save reference to the QGIS interface
        self.gctools = cls_main
        self.iface = iface



    def run(self):


        self.dlg = QDialog()

        # Layout principal
        layout = QVBoxLayout()

        # Map Layer Combo Box
        self.layer_combo = QgsMapLayerComboBox()
        self.layer_combo.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        layout.addWidget(self.layer_combo)

        # Layout de formulário para outros elementos
        form_layout = QFormLayout()

        # Variáveis num_samples_per_stratum
        self.num_samples_combo = QComboBox()
        self.num_samples_combo.addItem("100")
        self.num_samples_combo.addItem("200")
        self.num_samples_combo.addItem("300")
        form_layout.addRow("Amostras por Estrato:", self.num_samples_combo)

        # Variáveis num_strata
        self.num_strata_combo = QComboBox()
        self.num_strata_combo.addItem("4")
        self.num_strata_combo.addItem("6")
        self.num_strata_combo.addItem("8")
        form_layout.addRow("Número de Estratos:", self.num_strata_combo)

        layout.addLayout(form_layout)

        # Botão OK
        ok_button = QPushButton("Gerar Amostra")
        ok_button.clicked.connect(self.get_sample)
        layout.addWidget(ok_button)

        # Definir o layout do diálogo
        self.dlg.setLayout(layout)

    def get_sample(self):
        # Parâmetros
        layer_name = 'nome_da_camada'
        num_samples_per_stratum = 200
        num_strata = 8

        # Carregando a camada de polígonos
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]

        # Obtendo a área total da camada
        total_area = sum([feature.geometry().area() for feature in layer.getFeatures()])

        # Calculando os limites de área para cada estrato
        stratum_bounds = [total_area * i / num_strata for i in range(1, num_strata + 1)]
        stratum_areas = [0] * num_strata

        # Criando uma lista de estratos
        strata = [[] for _ in range(num_strata)]

        # Classificando as feições em estratos com base em suas áreas
        for feature in layer.getFeatures():
            feature_area = feature.geometry().area()
            for i, boundary in enumerate(stratum_bounds):
                if stratum_areas[i] + feature_area <= boundary:
                    strata[i].append(feature)
                    stratum_areas[i] += feature_area
                    break

        # Selecionando aleatoriamente amostras de cada estrato
        sampled_features = []

        for stratum in strata:
            if len(stratum) >= num_samples_per_stratum:
                sampled_features.extend(random.sample(stratum, num_samples_per_stratum))
            else:
                sampled_features.extend(stratum)

        # Criando uma nova camada para as amostras
        sample_layer = QgsVectorLayer("Polygon?crs=" + layer.crs().authid(), "amostras", "memory")
        sample_layer.startEditing()

        # Adicione um campo "area" à camada de amostras
        field = QgsField("area", QVariant.Double)
        sample_layer.dataProvider().addAttributes([field])
        sample_layer.updateFields()

        # Adicione as amostras à camada e calcule a área para cada amostra
        for feature in sampled_features:
            new_feature = QgsFeature(sample_layer.fields())
            new_feature.setGeometry(feature.geometry())
            new_feature.setAttribute("area", feature.geometry().area())
            sample_layer.dataProvider().addFeatures([new_feature])

        sample_layer.commitChanges()

        # Adicionando a camada de amostras ao projeto
        QgsProject.instance().addMapLayer(sample_layer)
