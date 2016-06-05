# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OSMDataDialog
                                 A QGIS plugin
 Download OSM Data
                             -------------------
        begin                : 2016-05-20
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Yassine Essadiki
        email                : y.essadiki9@gmail.com
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

from os.path import split, join, isfile, dirname, abspath
from json import load
from PyQt4.QtGui import QDialog, QApplication, QCompleter, QDialogButtonBox, QFileDialog, QDesktopServices
from PyQt4.QtCore import Qt, QUrl
from qgis.gui import QgsMessageBar
from osm_data_dialog_base import Ui_OSMDataDialogBase
from sys import exc_info
from core.exceptions import OsmDataException, OutPutGeomTypesException, DirectoryOutPutException, OsmObjectsException
from core.utilities.utilities_qgis import display_message_bar
from core.utilities.tools import tr,get_OSMData_folder
from core.query_factory import QueryFactory
from controller.process import process_osm_data_query
from qgis.utils import iface
from qgis.core import (
    QgsGeometry,
    QgsCoordinateTransform,
    QgsCoordinateReferenceSystem,
    QgsMapLayerRegistry)


class OSMDataDialog(QDialog, Ui_OSMDataDialogBase):
    def __init__(self, parent=None):
        """Constructor."""
        QDialog.__init__(self)
        self.last_places = []
        self.last_nominatim_places_filepath = join(
            get_OSMData_folder(),
            'nominatim.txt')

        
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
    
        registry = QgsMapLayerRegistry.instance()
        registry.layersAdded.connect(self.activate_extent_layer)
        registry.layersRemoved.connect(self.activate_extent_layer)
    

        # Setup UI
        self.label_progress.setText("")
        self.lineEdit_filePrefix.setDisabled(True)
        self.groupBox.setCollapsed(True)
        self.activate_extent_layer()
        self.groupBox.setCollapsed(True)
        self.comboBox_in_around.setDisabled(True)
        self.lineEdit_nominatim.setDisabled(True)
        self.radioButton_extentMapCanvas.setChecked(True)
        self.spinBox_distance_point.setDisabled(True)
        self.label_distance_point.setDisabled(True)

        # Setup in/around combobox
        self.comboBox_in_around.insertItem(0, tr('OSMDataDialogBase', u'Dans'))
        self.comboBox_in_around.insertItem(1, tr('OSMDataDialogBase', u'Autour'))

        # connect
        self.pushButton_runQuery.clicked.connect(self.run_query)
        self.pushButton_browse_output_file.clicked.connect(
            self.set_output_directory_path)
        self.comboBox_key.editTextChanged.connect(self.key_edited)
        self.lineEdit_browseDir.textEdited.connect(self.disable_prefix_file)
        self.radioButton_extentLayer.toggled.connect(
            self.allow_nominatim_or_extent)
        self.radioButton_extentMapCanvas.toggled.connect(
            self.allow_nominatim_or_extent)
        self.radioButton_place.toggled.connect(self.allow_nominatim_or_extent)
        self.pushButton_mapFeatures.clicked.connect(self.open_map_features)
        self.buttonBox.button(QDialogButtonBox.Reset).clicked.connect(
            self.reset_form)
        self.comboBox_in_around.currentIndexChanged.connect(self.in_or_around)

        

        # Setup auto completion
        map_features_json_file = join(
            dirname(abspath(__file__)), 'mapFeatures.json')

        if isfile(map_features_json_file):
            self.osmKeys = load(open(map_features_json_file))
            keys = self.osmKeys.keys()
            keys.sort()
            keys_completer = QCompleter(keys)
            self.comboBox_key.addItems(keys)
            self.comboBox_key.setCompleter(keys_completer)
            self.comboBox_key.completer().setCompletionMode(
                QCompleter.PopupCompletion)
        self.key_edited()

        self.init_nominatim_autofill()
        
    def allow_nominatim_or_extent(self):
        """
        Disable or enable radiobuttons if nominatim or extent
        """

        if self.radioButton_extentMapCanvas.isChecked() or \
                self.radioButton_extentLayer.isChecked():
            self.lineEdit_nominatim.setDisabled(True)
            self.spinBox_distance_point.setDisabled(True)
            self.label_distance_point.setDisabled(True)
            self.comboBox_in_around.setDisabled(True)
        else:
            self.lineEdit_nominatim.setDisabled(False)
            self.comboBox_in_around.setDisabled(False)
            self.in_or_around()

        if self.radioButton_extentLayer.isChecked():
            self.comboBox_extentLayer.setDisabled(False)
        else:
            self.comboBox_extentLayer.setDisabled(True)
            

               

    def reset_form(self):
        self.comboBox_key.setCurrentIndex(0)
        self.lineEdit_nominatim.setText("")
        self.radioButton_place.setChecked(True)
        self.spinBox_distance_point.setValue(1000)
        self.comboBox_in_around.setCurrentIndex(0)
        self.checkBox_points.setChecked(True)
        self.checkBox_lines.setChecked(True)
        self.checkBox_multilinestrings.setChecked(True)
        self.checkBox_multipolygons.setChecked(True)
        self.checkBox_node.setChecked(True)
        self.checkBox_way.setChecked(True)
        self.checkBox_relation.setChecked(True)
        self.spinBox_timeout.setValue(25)
        self.lineEdit_browseDir.setText("")
        self.lineEdit_filePrefix.setText("")


    def init_nominatim_autofill(self):

        # Usefull to avoid duplicate if we add a new completer.
        self.lineEdit_nominatim.setCompleter(None)
        self.last_places = []

        if isfile(self.last_nominatim_places_filepath):
            for line in open(self.last_nominatim_places_filepath, 'r'):
                self.last_places.append(line.rstrip('\n'))

            nominatim_completer = QCompleter(self.last_places)
            self.lineEdit_nominatim.setCompleter(nominatim_completer)
            self.lineEdit_nominatim.completer().setCompletionMode(
                QCompleter.PopupCompletion)
        else:
            open(self.last_nominatim_places_filepath,'a').close()

    @staticmethod
    def sort_nominatim_places(existing_places, place):
        if place in existing_places:
            existing_places.pop(existing_places.index(place))
        existing_places.insert(0, place)
        return existing_places[:10]

    def nominatim_value(self):
        value = unicode(self.lineEdit_nominatim.text())
        new_list = self.sort_nominatim_places(self.last_places, value)

        f = open(self.last_nominatim_places_filepath, 'w')
        for item in new_list:
            f.write("%s\n" % item)
        f.close()

        self.init_nominatim_autofill()

        return value
   
    

    def key_edited(self):
        """
        Disable show and run buttons if the key is empty
        and add values to the combobox
        """
        if self.comboBox_key.currentText():
            self.pushButton_runQuery.setDisabled(False)
        else:
            self.pushButton_runQuery.setDisabled(True)
        self.comboBox_value.clear()
        self.comboBox_value.setCompleter(None)

        try:
            current_values = self.osmKeys[
                unicode(self.comboBox_key.currentText())]
        except KeyError:
            return
        except AttributeError:
            return

        if current_values[0] != "":
            current_values.insert(0, "")

        values_completer = QCompleter(current_values)
        self.comboBox_value.setCompleter(values_completer)
        self.comboBox_value.addItems(current_values)

    def in_or_around(self):
        """
        Disable the spinbox distance if 'in' or 'around'
        """

        index = self.comboBox_in_around.currentIndex()

        if index == 1:
            self.spinBox_distance_point.setEnabled(True)
            self.label_distance_point.setEnabled(True)
        else:
            self.spinBox_distance_point.setEnabled(False)
            self.label_distance_point.setEnabled(False)
    
  

    
    def activate_extent_layer(self):
        """Activate or deactivate the radio button about the extent layer."""
        try:
            if self.comboBox_extentLayer.count() < 1:
                self.radioButton_extentLayer.setCheckable(False)
                self.radioButton_extentMapCanvas.setChecked(True)
            else:
                self.radioButton_extentLayer.setCheckable(True)
                
        except AttributeError:
            pass

    def disable_prefix_file(self):
        """
        If the directory is empty, we disable the file prefix
        """
        if self.lineEdit_browseDir.text():
            self.lineEdit_filePrefix.setDisabled(False)
        else:
            self.lineEdit_filePrefix.setText("")
            self.lineEdit_filePrefix.setDisabled(True)

    def set_output_directory_path(self):
        """
        Fill the output directory path
        """
        # noinspection PyTypeChecker
        output_file = QFileDialog.getExistingDirectory(
            None, caption=tr("OSMData", 'Select directory'))
        self.lineEdit_browseDir.setText(output_file)
        self.disable_prefix_file()

    def extent_radio(self):
        """
        Disable or enable the combox box
        """
        if self.radioButton_extentLayer.isChecked():
            self.comboBox_extentLayer.setDisabled(False)
        else:
            self.comboBox_extentLayer.setDisabled(True)


    def get_output_geometry_types(self):
        """
        Get all checkbox about outputs and return a list

        @rtype: list
        @return: list of layers
        """
        output_geom_types = []
        if self.checkBox_points.isChecked():
            output_geom_types.append('points')
        if self.checkBox_lines.isChecked():
            output_geom_types.append('lines')
        if self.checkBox_multilinestrings.isChecked():
            output_geom_types.append('multilinestrings')
        if self.checkBox_multipolygons.isChecked():
            output_geom_types.append('multipolygons')
        return output_geom_types

    def get_white_list_values(self):
        """
        Get all line edits about columns for each layers and return a dic

        @rtype: dic
        @return: doc of layers with columns
        """
        white_list_values = {}
        if self.checkBox_points.isChecked():
            white_list_values['points'] = self.lineEdit_csv_points.text()
        if self.checkBox_lines.isChecked():
            white_list_values['lines'] = self.lineEdit_csv_lines.text()
        if self.checkBox_multilinestrings.isChecked():
            white_list_values['multilinestrings'] = \
                self.lineEdit_csv_multilinestrings.text()
        if self.checkBox_multipolygons.isChecked():
            white_list_values['multipolygons'] = \
                self.lineEdit_csv_multipolygons.text()
        return white_list_values

    
    def get_bounding_box(self):
        """
        Get the geometry of the bbox in WGS84

        @rtype: QGsRectangle in WGS84
        @return: the extent of the map canvas
        """

        # If mapCanvas is checked
        if self.radioButton_extentMapCanvas.isChecked():
            geom_extent = iface.mapCanvas().extent()
            if hasattr(iface.mapCanvas(), "mapSettings"):
                source_crs = iface.mapCanvas().mapSettings().destinationCrs()
            else:
                source_crs = iface.mapCanvas().mapRenderer().destinationCrs()
        else:
            # Else if a layer is checked
            layer = self.comboBox_extentLayer.currentLayer()
            geom_extent = layer.extent()
            source_crs = layer.crs()

        geom_extent = QgsGeometry.fromRect(geom_extent)
        epsg_4326 = QgsCoordinateReferenceSystem('EPSG:4326')
        crs_transform = QgsCoordinateTransform(source_crs, epsg_4326)
        geom_extent.transform(crs_transform)
        return geom_extent.boundingBox()

    def start_process(self):
        """
        Make some stuff before launching the process
        """
        self.pushButton_runQuery.setDisabled(True)
        self.pushButton_runQuery.initialText = self.pushButton_runQuery.text()
        self.pushButton_runQuery.setText(tr('OSMData', 'Execution du requete ...'))
        self.progressBar_execution.setMinimum(0)
        self.progressBar_execution.setMaximum(0)
        self.progressBar_execution.setValue(0)
        self.label_progress.setText('')

    def end_process(self):
        """
        Make some stuff after the process
        """
        self.pushButton_runQuery.setDisabled(False)
        self.pushButton_runQuery.setText(self.pushButton_runQuery.initialText)
        self.progressBar_execution.setMinimum(0)
        self.progressBar_execution.setMaximum(100)
        self.progressBar_execution.setValue(100)
        QApplication.processEvents()

    def set_progress_percentage(self, percent):
        """
        Slot to update percentage during process
        """
        self.progressBar_execution.setValue(percent)
        QApplication.processEvents()

    def set_progress_text(self, text):
        """
        Slot to update text during process
        """
        self.label_progress.setText(text)
        QApplication.processEvents()

    def display_geo_algorithm_exception(self, e):
        """
        Display osmdata exceptions
        """
        self.label_progress.setText("")
        display_message_bar(e.msg, level=e.level, duration=e.duration)
        
    @staticmethod
    def display_exception(e):
        """
        Display others exceptions
        """
        exc_type, _, exc_tb = exc_info()
        f_name = split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, f_name, exc_tb.tb_lineno)
        _, _, tb = exc_info()
        import traceback
        traceback.print_tb(tb)
        print e
        display_message_bar(
            tr('OSMData', 'Error in the python console, please report it'),
            level=QgsMessageBar.CRITICAL,
            duration=20)
    @staticmethod
    def open_map_features():
        """
        Open MapFeatures
        """
        desktop_service = QDesktopServices()
        desktop_service.openUrl(
            QUrl("http://wiki.openstreetmap.org/wiki/Mapfeatures"))


    def run_query(self):
        """
        Process for running the query
        """

        # Block the button and save the initial text
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.pushButton_browse_output_file.setDisabled(True)
        self.start_process()
        QApplication.processEvents()

        # Get all values
        key = unicode(self.comboBox_key.currentText())
        value = unicode(self.comboBox_value.currentText())
        nominatim = self.nominatim_value()
        timeout = self.spinBox_timeout.value()
        output_directory = self.lineEdit_browseDir.text()
        prefix_file = self.lineEdit_filePrefix.text()
        if self.comboBox_in_around.currentIndex() == 1:
            is_around = True
        else:
            is_around = False
        distance = self.spinBox_distance_point.value()
               
        # Which geometry at the end ?
        output_geometry_types = self.get_output_geometry_types()

        # Which osm objects ?
        osm_objects = self._get_osm_objects()

        try:
            # Test values
            if not osm_objects:
                raise OsmObjectsException

            if not output_geometry_types:
                raise OutPutGeomTypesException

            # If bbox, we must set None to nominatim, we can't have both
            bbox = None
            if self.radioButton_extentLayer.isChecked() or \
                    self.radioButton_extentMapCanvas.isChecked():
                nominatim = None
                bbox = self.get_bounding_box()
                
            if nominatim =='':
                nominatim = None
       

            if output_directory and not isdir(output_directory):
                raise DirectoryOutPutException

            num_layers = process_osm_data_query(
                dialog=self,
                key=key,
                value=value,
                nominatim=nominatim,
                is_around=is_around,
                distance=distance,
                bbox=bbox,
                osm_objects=osm_objects,
                timeout=timeout,
                output_directory=output_directory,
                prefix_file=prefix_file,
                output_geometry_types=output_geometry_types)

            # We can test numLayers to see if there are some results
            if num_layers:
                self.label_progress.setText(
                    tr('OSMData', u'Successful query !'))

                display_message_bar(
                    tr('OSMData', u'Successful query !'),
                    level=QgsMessageBar.INFO,
                    duration=5)
            else:
                self.label_progress.setText(tr("OSMData", u'No result'))

                display_message_bar(
                    tr('OSMData', u'Successful query, but no result.'),
                    level=QgsMessageBar.WARNING,
                    duration=7)
                
          
        finally:
            # Resetting the button
            self.pushButton_browse_output_file.setDisabled(False)
            QApplication.restoreOverrideCursor()
            self.end_process()
            QApplication.processEvents()


    def _get_osm_objects(self):
        """
        Get a list of osm objects from checkbox

        @return: list of osm objects to query on
        @rtype: list
        """
        osm_objects = []
        if self.checkBox_node.isChecked():
            osm_objects.append('node')
        if self.checkBox_way.isChecked():
            osm_objects.append('way')
        if self.checkBox_relation.isChecked():
            osm_objects.append('relation')
        return osm_objects






   





        

    
