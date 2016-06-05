# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OSMData
                                 A QGIS plugin
 Download OSM Data
                             -------------------
        begin                : 2016-05-20
        copyright            : (C) 2016 by Yassine Essadiki
        email                : y.essadiki9@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load OSMData class from file OSMData.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .osm_data import OSMData
    return OSMData(iface)
