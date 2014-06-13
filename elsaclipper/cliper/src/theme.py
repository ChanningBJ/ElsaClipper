#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Deepin, Inc.
#               2011 Wang Yong
# 
# Author:     Wang Yong <lazycat.manatee@gmail.com>
# Maintainer: Wang Yong <lazycat.manatee@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from utils import *
import gobject, gtk
from comm.file_catalog import FileCatalog 
import os
import root
class DynamicPixbuf:
    '''Dynamic pixbuf.'''
    
    def __init__(self, filepath):
        '''Init.'''
        self.updatePath(filepath)
        
    def updatePath(self, filepath):
        '''Update path.'''
        self.pixbuf = gtk.gdk.pixbuf_new_from_file(filepath)

    def getPixbuf(self):
        '''Get pixbuf.'''
        return self.pixbuf

class Theme:
    '''Theme.'''
    
    def __init__(self):
        '''Init theme.'''
        # Init.
        self.themeName = "default"
        self.pixbufDict = {}
        
        # Scan theme files.
        themeDir = self.getThemeDir()
        for root, dirs, files in os.walk(themeDir):
            for filepath in files:
                self.pixbufDict[filepath] = DynamicPixbuf(os.path.join(root, filepath))
    
    def getThemeDir(self):
        '''Get theme directory.'''
        return FileCatalog.get_theme_path(self.themeName)
        # return root.get_full_path('cliper','theme',self.themeName)
                
    def getThemePath(self, path):
        '''Get pixbuf path.'''
        return os.path.join(self.getThemeDir(), path)
            
    def getDynamicPixbuf(self, path):
        '''Get dynamic pixbuf.'''
        return self.pixbufDict[path]
    
    def changeTheme(self, newThemeName):
        '''Change theme.'''
        # Change theme name.
        self.themeName = newThemeName

        # Update dynmaic pixbuf.
        for (path, pixbuf) in self.pixbufDict.items():
            pixbuf.updatePath(self.getThemePath(path))
    
# Init.
appTheme = Theme()            
