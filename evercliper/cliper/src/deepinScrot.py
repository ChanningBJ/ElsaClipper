#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Deepin, Inc.
#               2011 Hou Shaohui
#
# Author:     Hou Shaohui <houshao55@gmail.com>
# Maintainer: Hou ShaoHui <houshao55@gmail.com>
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

# locale
import gtk, os, sys, time
from mainscrot import MainScrot
from window import getScrotPixbuf
from optparse import OptionParser
from tipswindow import countdownWindow
from utils import makeMenuItem, getFormatTime
from constant import DEFAULT_FILENAME
saveFiletype = "png"


def saveToFile(fullscreen=True, fileName=None):
    '''Save file to file.'''
    pixbuf = getScrotPixbuf(fullscreen)

    if fileName is None:
        dialog = gtk.FileChooserDialog(
                                       "Save..",
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                                        gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
            
        
        dialog.set_default_response(gtk.RESPONSE_ACCEPT)
        dialog.set_position(gtk.WIN_POS_CENTER)
        dialog.set_local_only(True)
        
        dialog.set_current_folder(os.environ['HOME'])
        dialog.set_current_name("%s%s.%s" % (DEFAULT_FILENAME, getFormatTime(), saveFiletype))
        
        optionMenu = gtk.OptionMenu()
        optionMenu.set_size_request(155, -1)
        menu = gtk.Menu()
        menu.set_size_request(155, -1)
        
        pngItem = makeMenuItem('PNG (*.png)',
                     lambda item, data: setSaveFiletype(dialog, 'png'))
        
        jpgItem = makeMenuItem('JPEG (*.jpeg)',
                     lambda item, data: setSaveFiletype(dialog, 'jpeg'))
        
        bmpItem = makeMenuItem('BMP (*.bmp)',
                     lambda item, data: setSaveFiletype(dialog, 'bmp'))
        
        menu.append(pngItem)
        menu.append(jpgItem)
        menu.append(bmpItem)
        optionMenu.set_menu(menu)
        
        hbox = gtk.HBox()
        hbox.pack_end(optionMenu, False, False)
        dialog.vbox.pack_start(hbox, False, False)
        hbox.show_all()                          
                
        response = dialog.run()
            
        if response == gtk.RESPONSE_ACCEPT:
            fileName = dialog.get_filename()
        dialog.destroy()
    if fileName is None:
        print 'Closed, no files selected'
    else:
        pixbuf.save(fileName, saveFiletype)
        print "Save snapshot to %s" % (fileName)
    

def setSaveFiletype(widget, filetype):
    widget.set_current_name("%s%s.%s" % (DEFAULT_FILENAME, getFormatTime(), filetype))
    saveFiletype =filetype

def getFileNameFileType(fileName):
    basename = os.path.basename(fileName).split(".")
    if len(basename)>1:
        fileType = basename[-1]
    else:
        fileType = None
    if fileType.lower() in ("png","jepg","bmp"):
        fileName = os.path.expanduser(fileName)
        fileName = os.path.abspath(fileName)
        dirName = os.path.dirname(fileName)
        if os.path.isdir(dirName):
            return (fileName,fileType)
        else:
            print dirName,"do not exist or not a directory"
            return (None,None)
    else:
        print "The only supported file types are png, jepg and bmp"
        return (None,None)
        
    

def processArguments():
    '''init processArguments '''
    parser = OptionParser(usage="Usage: %prog [options] [arg]", version="%prog v1.0")
    parser.add_option("-f", "--full", action="store_true", dest="fullscreen", help="Taking the fullscreen shot")
    parser.add_option("-w", "--window", action="store_true", dest="window", help="Taking the currently focused window")
    parser.add_option("-d", "--delay", dest="delay", type="int", help="wait NUM seconds before taking a shot", metavar="NUM")
    parser.add_option("-o", "--outfile", dest="outfile", type="str", help="Save the snapshot to a file, file type png,jepg and bmp are supported")    
    (options, args) = parser.parse_args()
    #print parser.parse_args()
    (fileName,saveFileType) = (None,"png")
    if options.outfile:
        (fileName,saveFileType) = getFileNameFileType(options.outfile)
        if fileName is None:
            sys.exit(-1)
    if options.fullscreen and options.window:
        parser.error("options -f and -w are mutually exclusive")
    elif options.fullscreen:
        if options.delay:
            countdownWindow(options.delay)
            saveToFile(True,fileName)
#            openFileDialog()
        else:
            saveToFile(True,fileName)
    elif options.window:
        if options.delay:
            countdownWindow(options.delay)
            saveToFile(False,fileName)
        else:
            saveToFile(False,fileName)
    elif options.fullscreen and options.window or options.delay:
        countdownWindow(options.delay)
        MainScrot(fileName,saveFileType)
    else:
        MainScrot(fileName,saveFileType)
        
        

if __name__ == '__main__':
    processArguments()
    
        
        
    


