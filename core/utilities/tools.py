# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OSMData
                                 A QGIS plugin
 Download OSM Data
                              -------------------
        begin                : 2016-05-01
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

import ConfigParser
from qgis.core import QgsApplication
from os.path import join, dirname, abspath
from PyQt4.QtCore import QDir, QSettings, QFileInfo
from PyQt4.QtGui import QApplication

from operating_system import copy_tree


def tr(section, text):
    return QApplication.translate(section, text)


def read_metadata(section, item):
    root = dirname(dirname(dirname(__file__)))
    metadata = join(root, 'metadata.txt')
    parser = ConfigParser.ConfigParser()
    parser.read(metadata)
    return parser.get(section, item)


def get_current_version():
    return read_metadata('general', 'version')


def new_queries_available():
    status = read_metadata('general', 'newQueries')
    if status == u'True':
        return True
    else:
        return False


def get_OSMData_folder():
    """
    Get the user folder, ~/.qgis2/OSMData on linux for instance

    @rtype: str
    @return: path
    """
    folder = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + 'OSMData'
    return unicode(QDir.toNativeSeparators(folder))


def get_user_query_folder(over_write=False):
    """
    Get the user folder for queries.
    For instance on linux : ~/.qgis2/OSMData

    @rtype: str
    @return: path
    """
    folder = get_OSMData_folder()
    queries_folder = join(folder, 'queries')
    if not QDir(queries_folder).exists() or over_write:
        folder = join(dirname(dirname(dirname(abspath(__file__)))), 'queries')
        copy_tree(folder, QDir.toNativeSeparators(queries_folder))
    return unicode(QDir.toNativeSeparators(queries_folder))


def get_setting(key):
    """
    Get a value in the QSettings
    @param key: key
    @type key: str
    @return: value
    @rtype: str
    """
    qs = QSettings()
    prefix = '/OSMData/'
    return qs.value(prefix + key)


def set_setting(key, value):
    """
    Set a value in the QSettings
    @param key: key
    @type key: str
    @param value: value
    @type value: str
    @return: result
    @rtype: bool
    """
    qs = QSettings()
    prefix = '/OSMData/'
    return qs.setValue(prefix + key, value)

