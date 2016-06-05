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

from processing.core.GeoAlgorithmExecutionException import \
    GeoAlgorithmExecutionException
from qgis.gui import QgsMessageBar

from OSMData.core.utilities.tools import tr


class OsmDataException(GeoAlgorithmExecutionException):
    def __init__(self, msg=None):
        GeoAlgorithmExecutionException.__init__(self, msg)
        self.level = QgsMessageBar.CRITICAL
        self.duration = 7

'''
Overpass or network
'''


class OverpassBadRequestException(OsmDataException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('Exception', u'Bad request OverpassAPI')
        OsmDataException.__init__(self, msg)


class OverpassTimeoutException(OsmDataException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('Exception', u'OverpassAPI timeout')
        OsmDataException.__init__(self, msg)


class NetWorkErrorException(OsmDataException):
    def __init__(self, msg=None, suffix=None):
        if not msg:
            msg = tr("Exception", u"Network error")
        if suffix:
            msg = msg + " with " + suffix
        OsmDataException.__init__(self, msg)

'''
QueryFactory
'''


class QueryFactoryException(OsmDataException):
    def __init__(self, msg=None, suffix=None):
        if not msg:
            msg = tr("Exception", u"Error while building the query")
        if suffix:
            msg = msg + " : " + suffix
        OsmDataException.__init__(self, msg)

'''
Nominatim
'''


class NominatimAreaException(OsmDataException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr("Exception", u"No nominatim area")
        OsmDataException.__init__(self, msg)

'''
Ogr2Ogr
'''


class OsmDriver(OsmDataException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr(
                'Exception', u"The OSM's driver is not installed. "
                             u"You must have GDAL/OGR >= 1.10.")
        OsmDataException.__init__(self, msg)


class Ogr2OgrException(OsmDataException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr("Exception", u"Error with ogr2ogr")
        OsmDataException.__init__(self, msg)


class NoLayerException(OsmDataException):
    def __init__(self, msg=None, suffix=None):
        if not msg:
            msg = tr("Exception", u"The layer is missing :")
        if suffix:
            msg = msg + " " + suffix
        OsmDataException.__init__(self, msg)


class WrongOrderOSMException(OsmDataException):
    def __init__(self, msg=None, suffix=None):
        if not msg:
            msg = tr(
                'Exception',
                u'The order must be node-way-relation. '
                u'Check the print statement.')
        if suffix:
            msg = msg + " " + suffix
        OsmDataException.__init__(self, msg)

'''
File and directory
'''


class FileDoesntExistException(OsmDataException):
    def __init__(self, msg=None, suffix=None):
        if not msg:
            msg = tr("Exception", u"The file doesn't exist")
        if suffix:
            msg = msg + " " + suffix
        OsmDataException.__init__(self, msg)


class DirectoryOutPutException(OsmDataException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('Exception', u'The output directory does not exist.')
        OsmDataException.__init__(self, msg)


class FileOutPutException(OsmDataException):
    def __init__(self, msg=None, suffix=None):
        if not msg:
            msg = tr(
                'Exception', u'The output file already exist, set a prefix')
        if suffix:
            msg = msg + " " + suffix
        OsmDataException.__init__(self, msg)


class OutPutFormatException(OsmDataException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr("Exception", u"Output not available")
        OsmDataException.__init__(self, msg)


class QueryAlreadyExistsException(OsmDataException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr("Exception", u"This query already exists")
        OsmDataException.__init__(self, msg)

'''
Forms
'''


class MissingParameterException(OsmDataException):
    def __init__(self, msg=None, suffix=None):
        if not msg:
            msg = tr("Exception", u"A parameter is missing :")
        if suffix:
            msg = msg + " " + suffix
        OsmDataException.__init__(self, msg)


class OsmObjectsException(OsmDataException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr("Exception", u"No osm objects selected")
        OsmDataException.__init__(self, msg)


class OutPutGeomTypesException(OsmDataException):
    def __init__(self, msg=None):
        if not msg:
            msg = tr('Exception', u'No outputs selected')
        OsmDataException.__init__(self, msg)
