# -*- coding: utf-8 -*-
'''
Created on 20 Jul 2018
Icons courtesy of www.iconarchive.com.
Icons licence: http://graphicloads.com/license/
Linux only: Depends on image-magick
@author: matze
'''
import gi
import locale
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk,GObject
GObject.threads_init() # Important!

import os,urllib
from urllib.parse import urlparse
import threading
from datetime import datetime
from configparser import ConfigParser
from os.path import expanduser
from subprocess import Popen
import subprocess

TARGET_ENTRY_TEXT =0
DRAG_ACTION = Gdk.DragAction.COPY

lang = locale.getdefaultlocale()
'''
Template
    TEXT_MAP["TITLE"]="
    TEXT_MAP["LABEL_DROP_AREA"]="
    TEXT_MAP["BUTTON_OK"]="
    TEXT_MAP["BUTTON_CANX"]="
    TEXT_MAP["BUTTON_DEL"]="
    TEXT_MAP["FOLDER_PIC"]="
    TEXT_MAP["DEFAULT_PDF"]="
    TEXT_MAP["DIALOG_TITLE_ERROR"]="
    TEXT_MAP["NOT_A_FILE_ERROR"]="
    TEXT_MAP["FILE_SAVE"]="
    TEXT_MAP["COL1"]="
    TEXT_MAP["COL2"]="
    TEXT_MAP["COL3"]="
'''
TEXT_MAP = {}
if "en" in lang[0]:
    TEXT_MAP["TITLE"]="PDF converter"
    TEXT_MAP["LABEL_DROP_AREA"]="Drop files onto list below"
    TEXT_MAP["BUTTON_OK"]="Convert"
    TEXT_MAP["BUTTON_CANX"]="Done"
    TEXT_MAP["BUTTON_DEL"]="Delete"
    TEXT_MAP["FOLDER_PIC"]="Pictures"
    TEXT_MAP["DEFAULT_PDF"]="My.pdf"
    TEXT_MAP["DIALOG_TITLE_ERROR"]="An error occurred )-:"
    TEXT_MAP["NOT_A_FILE_ERROR"]="Drop files not folders"
    TEXT_MAP["FILE_SAVE"]="Name of the PDF File"
    TEXT_MAP["COL1"]="File"
    TEXT_MAP["COL2"]="Size KB"
    TEXT_MAP["COL3"]="Date"
elif "de" in lang[0]:
    TEXT_MAP["TITLE"]="Erichs PDF Konverter"
    TEXT_MAP["LABEL_DROP_AREA"]="Dateien auf die Liste ziehen"
    TEXT_MAP["BUTTON_OK"]="Konvertieren"
    TEXT_MAP["BUTTON_CANX"]="   Fertig   "
    TEXT_MAP["BUTTON_DEL"]=" Löschen "
    TEXT_MAP["FOLDER_PIC"]="Bilder"
    TEXT_MAP["DEFAULT_PDF"]="Bilder.pdf"
    TEXT_MAP["DIALOG_TITLE_ERROR"]="Da ist ein Fehler passiert )-:"
    TEXT_MAP["NOT_A_FILE_ERROR"]="Bitte nur Dateien ablegen, keine Ordner"
    TEXT_MAP["FILE_SAVE"]="Wie soll die Datei heißen?"
    TEXT_MAP["COL1"]="Datei"
    TEXT_MAP["COL2"]="Größe KB"
    TEXT_MAP["COL3"]="Datum"

def _t(s):
    return TEXT_MAP[s]

class PDFMakerWindow(Gtk.Window):

    def __init__(self):
        self.should_abort=False
        Gtk.Window.__init__(self, title=_t("TITLE"))
        self.config=ConfigAccessor("pdfmaker.ini")
        self._assureConfig()
        self._initWidgets()
        self.add_text_targets()
        '''
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        hbox = Gtk.Box(spacing=12)
        vbox.pack_start(hbox, True, True, 0)

        self.iconview = DragSourceIconView()
        self.drop_area = DropArea()

        hbox.pack_start(self.iconview, True, True, 0)
        hbox.pack_start(self.drop_area, True, True, 0)

        button_box = Gtk.Box(spacing=6)
        vbox.pack_start(button_box, True, False, 0)

        image_button = Gtk.RadioButton.new_with_label_from_widget(None,
            "Images")
        image_button.connect("toggled", self.add_image_targets)
        button_box.pack_start(image_button, True, False, 0)

        text_button = Gtk.RadioButton.new_with_label_from_widget(image_button,
            "Text")
        text_button.connect("toggled", self.add_text_targets)
        button_box.pack_start(text_button, True, False, 0)

        self.add_image_targets()
        '''
        

    def _initWidgets(self):
        '''
        '''
        here = os.path.dirname(os.path.realpath(__file__))
        self.set_icon_from_file(os.path.join(here,"pdf-icon.png"))
        mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=4)
        labelbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        color = Gdk.RGBA();
        color.parse('#fcf88d')
        labelbox.override_background_color(Gtk.StateFlags.NORMAL,color)
        lowerBtnBox= Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        self.list = self._makeList()
        
        #Top label
        srclabel= Gtk.Label(_t("LABEL_DROP_AREA"))
        labelbox.pack_start(srclabel,True,False,0)
        
        self.spinner = Gtk.Spinner()
        lowerBtnBox.pack_start(self.spinner,False, False, 5)
        
        self.buttonStart = Gtk.Button(label=_t("BUTTON_OK"),image=Gtk.Image(stock=Gtk.STOCK_APPLY))
        self.buttonStart.connect("clicked", self.on_convert_clicked)
        lowerBtnBox.pack_end(self.buttonStart, False, False, 5)
        
        self.buttonCanx = Gtk.Button(label=_t("BUTTON_CANX"),image=Gtk.Image(stock=Gtk.STOCK_CANCEL))
        self.buttonCanx.connect("clicked", self.on_close_clicked)
        lowerBtnBox.pack_end(self.buttonCanx, False, False,5)
        
        self.buttonDel = Gtk.Button(label=_t("BUTTON_DEL"),image=Gtk.Image(stock=Gtk.STOCK_DELETE))
        self.buttonDel.connect("clicked", self.on_delete_clicked)
        lowerBtnBox.pack_end(self.buttonDel, False, False,5)

        self.buttonStart.set_sensitive(False)
        self.buttonDel.set_sensitive(False)

        # expand = false, fill not relevant- height stays!
        mainbox.pack_start(labelbox,False,True,0)
        mainbox.pack_start(self.list,True,True,3)
        mainbox.pack_end(lowerBtnBox,False,False,3)
        
        self.add(mainbox)
        self.set_border_width(5)
        self.set_default_size(self.config.getInt("SCREENX"), self.config.getInt("SCREENY"))
        self.connect("delete-event", self.on_winClose, None)

    def _makeList(self):
        self.fileStore = Gtk.ListStore(str,str,str);
        theList = Gtk.TreeView(self.fileStore)
       
        for n,name in enumerate([_t("COL1"),_t("COL2"),_t("COL3")]):
            if n is 0:
                cell = Gtk.CellRendererText()
            else:
                cell = Gtk.CellRendererText(xalign=1)
            column = Gtk.TreeViewColumn(name,cell,text=n);
            column.set_resizable(True)
            if n is 0:
                column.set_expand(True)
            else:
                column.set_alignment(0.5)
            theList.append_column(column)
        
        self.selection = theList.get_selection()
        self.selection.connect("changed", self.on_selected)
        swH = Gtk.ScrolledWindow()
        swH.add(theList)
        swH.connect("drag-data-received", self.on_drag_data_received)
        return swH

    def on_drag_data_received(self, widget, drag_context, x,y, data,info, time):
        if info == TARGET_ENTRY_TEXT:
            rawData =  data.get_data().decode("utf8")

            text = urllib.parse.unquote(rawData)
            entries = text.split('\r\n')
            for item in entries:
                p = urlparse(item)
                if len(p.path)<3:
                    continue
                finalPath = os.path.abspath(os.path.join(p.netloc, p.path))
                if os.path.isfile(finalPath):
                    self.addFileInfo(finalPath)
                else:
                    self._showError(_t("NOT_A_FILE_ERROR"))
            
            self.buttonStart.set_sensitive(True)
            
    def addFileInfo(self,path):
        fsize = os.stat(path).st_size
        mtime = os.stat(path).st_mtime
        date = datetime.fromtimestamp(mtime)
        
        rowData=[path,str(int(fsize/1024)),date.strftime("%d.%m %H:%M")]
        self.fileStore.append(rowData)
    

    def _assureConfig(self):

        self.config.read()
        x = self.config.getInt("SCREENX")
        if not x:
            home = expanduser("~")
            self.config.add("SCREENX","400")
            self.config.add("SCREENY","400")
            path = os.path.join(home,_t("FOLDER_PIC"))
            target = os.path.join(path,_t("DEFAULT_PDF"))
            self.config.add("DEST",target)
        self.last_target=self.config.get("DEST")

    def add_text_targets(self):
        self.list.drag_dest_set(Gtk.DestDefaults.ALL, [], DRAG_ACTION)
        self.list.drag_dest_set_target_list(None)
        self.list.drag_dest_add_text_targets()
        self.list.drag_dest_add_uri_targets()


    def on_close_clicked(self, widget):
        self.should_abort=True
        self.on_winClose(None,None,None)
        Gtk.main_quit()
        
        
    def on_convert_clicked(self, widget):
        self.should_abort=False
        self.buttonStart.set_sensitive(False)
        self.buttonDel.set_sensitive(False)
        self.buttonCanx.set_sensitive(False)
        self.spinner.start()
        
        result = self._selectFile(self.config.get("DEST"))  
        if result:
            self.last_target = result
            proc = PDFBuilder(self.fileStore,result)            
            w = WorkerThread(self._pdfBuildDone,proc)
            w.start() 
        else:
            self._pdfBuildDone("")

    def _pdfBuildDone(self,res):
        self.spinner.stop()
        self.buttonStart.set_sensitive(True)
        self.buttonCanx.set_sensitive(True)
        if len(res)>0:
            self._showError(res)
                
    
    def _selectFile(self,defaultFolder):
        dialog = Gtk.FileChooserDialog(_t("FILE_SAVE"), self,Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        dialog.set_filename(defaultFolder)
        pdfFilter = Gtk.FileFilter()
        pdfFilter.set_name("PDF (*.pdf)")
        pdfFilter.add_pattern("*.[Pp][Dd][Ff]")
        dialog.add_filter(pdfFilter)
        
        pngFilter = Gtk.FileFilter()
        pngFilter.set_name("PNG (*.png)")
        pngFilter.add_pattern("*.[Pp][Nn][Gg]")
        dialog.add_filter(pngFilter)

        response = dialog.run()
        thePath = None
        if response == Gtk.ResponseType.OK:
            thePath = dialog.get_filename()

        dialog.destroy()
        return thePath
    
    def _showError(self,text):
        image = Gtk.Image()
        image.set_from_stock(Gtk.STOCK_CAPS_LOCK_WARNING, Gtk.IconSize.DIALOG)
        image.show()
        
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK, _t("DIALOG_TITLE_ERROR"))
        dialog.set_image(image)
        dialog.format_secondary_text(text)
        dialog.run()
        dialog.destroy()   
        return False      
    
    def on_delete_clicked(self,widget):
        (model, item) = self.selection.get_selected()
        if item is not None:
            model.remove(item)

    def on_selected(self, selection):
        hasItems = len(self.fileStore) != 0
        self.buttonDel.set_sensitive(hasItems)
        self.buttonStart.set_sensitive(hasItems)
    

    def on_winClose(self, widget, event, data):
        geo = self.get_allocation()
        self.config.add("SCREENX",str(geo.width))
        self.config.add("SCREENY",str(geo.height))
        aPath = self.last_target
        if self.last_target is not None:            
            self.config.add("DEST",aPath);
        self.config.store()

class PDFBuilder():
    def __init__(self,fileStore,target):
        self.fileStore=fileStore
        self.target = target

    def run(self):
        item = self.fileStore.get_iter_first ()
        files =[]
        while ( item != None ):
            path = self.fileStore.get_value (item, 0)
            files.append(path)
            item = self.fileStore.iter_next(item)
            res = self.makePDF(files)
            if len(res)>0:
                return res
        return ""    
        
    def makePDF(self,files):
        cmd =["/usr/bin/convert"]
        for path in files:
            cmd.append(path)
        cmd.append("-quality")
        cmd.append("100")
        cmd.append(self.target)
        #no error ever showed up....
        result = Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
        ##That aint working in thread!
        if len(result[1])>0:
            return result[1].decode("utf-8")       
        return ""

class WorkerThread(threading.Thread):
    def __init__(self, callback,processor):
        threading.Thread.__init__(self)
        self.callback = callback
        self.processor = processor

    def run(self):
        res = self.processor.run()

        # The callback runs a GUI task, so wrap it!
        GObject.idle_add(self.callback,res)

class ConfigAccessor():
    __SECTION="DATA"
    

    def __init__(self,filePath):
        self._path=filePath
        self.parser = ConfigParser()
        self.parser.add_section(self.__SECTION)

    def read(self):
        self.parser.read(self._path)

    def add(self,key,value):
        self.parser.set(self.__SECTION,key,value)

    def get(self,key):
        if self.parser.has_option(self.__SECTION, key):
            return self.parser.get(self.__SECTION,key)
        return None

    def getInt(self,key):
        if self.parser.has_option(self.__SECTION, key):
            return self.parser.getint(self.__SECTION,key)
        return None

    def store(self):
        try:
            with open(self._path, 'w') as aFile:
                self.parser.write(aFile)
        except IOError:
            return False
        return True


win = PDFMakerWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()

if __name__ == '__main__':
    pass
