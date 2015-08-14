# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Compotte
                                 A QGIS plugin
 Synchronize server composition and layer styles with local repository
                             -------------------
        begin                : 2013-11-15
        copyright            : (C) 2013 by Jan Bojko
        email                : jan.bojko@gmail.com
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

def classFactory(iface):
    # load Compotte class from file Compotte
    from compotte import Compotte
    return Compotte(iface)
