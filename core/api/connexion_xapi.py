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
import urllib2
import tempfile

from OSMData.core.exceptions import NetWorkErrorException


class ConnexionXAPI(object):
    """
    Manage connexion to the eXtend API (XAPI)
    """

    def __init__(self, url="api.openstreetmap.fr/xapi?"):
        """
        Constructor

        @param url:URL of OverPass
        @type url:str
        """

        self.__url = url

    def query(self, query):
        """
        Make a query to the xapi

        @param query:Query to execute
        @type query:str

        @raise Exception : Bad, should be a ExceptionOSMData

        @return: the result of the query
        @rtype: str
        """
        query = query.encode('utf8')
        url_query = self.__url + query

        try:
            data = urllib2.urlopen(url=url_query).read()
        except urllib2.HTTPError:
            raise NetWorkErrorException(suffix="XAPI")

        return data

    def get_file_from_query(self, query):
        """
        Make a query to the xapi and put the result in a temp file

        @param query:Query to execute
        @type query: str

        @return: temporary file path
        @rtype: str
        """
        query = self.query(query)
        tf = tempfile.NamedTemporaryFile(delete=False, suffix=".osm")
        tf.write(query)
        name_file = tf.name
        tf.flush()
        tf.close()
        return name_file
