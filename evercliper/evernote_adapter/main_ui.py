from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Keybinder
from gi.repository import AppIndicator3 as AppIndicator
from gi.repository.Gdk import Color
from gi.repository import WebKit
import urlparse
import os
from evernote.api.client import EvernoteClient
import logging
from evernote_client import EvernoteAdapter
from comm.util import MetaData
from comm.util import NoteBookInfo
from comm.util import KeyRing
from comm.util import EverNoteConsumerInfo
from comm.util import PROGRAM_NAME
from comm.file_catalog import FileCatalog
import threading

from gi.repository import Notify
from Queue import Queue
from note_listener import NoteListenerThread
import socket
import sys
import time
import subprocess



class AuthDialog():
    # EverNoteConsumerInfo.CONSUMER_KEY="channing"
    # EverNoteConsumerInfo.CONSUMER_SECRET="35627ab2ee94809f"

    STATUS_MESSAGE_CONNECTING = 'connecting ...'

    def __init__(self, ):
        self.__auth_token = None
        self.__authData = {}
        builder = Gtk.Builder()
        builder.add_from_file(FileCatalog.get_evercliper_glade())
        self.__dialog = builder.get_object('auth_dialog')
        self.__dialog.set_icon_from_file(FileCatalog.get_evercliper_icon('evercliper_config.png'))
        self.__spinner = builder.get_object('connecting_spinner')
        self.__status_label = builder.get_object('connecting_label')
        self.__status_label.set_text(AuthDialog.STATUS_MESSAGE_CONNECTING)
        
        webview = WebKit.WebView()
        webview.connect("navigation-requested",self.on_navigation_requested)
        webview.connect("notify::load-status",self.on_load_status)
        url = self._getEverNoteOAuthURL()
        logging.debug(url)
        webview.open(url)

        viewport = builder.get_object('webkit_viewport')
        viewport.add(webview)
        self.__dialog.show_all()

        
    def on_close_button_clicked(self):
        self.__dialog.response(0)

    def get_auth_token(self,):
        return self.__auth_token
        
    def run(self):
        self.__dialog.run()

    def destroy(self,):
        self.__dialog.destroy()
        
    def _getEverNoteOAuthURL(self):
        client = EvernoteClient(
            consumer_key=EverNoteConsumerInfo.CONSUMER_KEY,
            consumer_secret=EverNoteConsumerInfo.CONSUMER_SECRET,
            sandbox=True # Default: True ; if using yinxiang, set service_host='www.yinxiang.com' ; in using Evernote International, set  service_host='www.evernote.com'
        )
        callbackUrl = "http://"+PROGRAM_NAME
        request_token = client.get_request_token(callbackUrl)
        # Save the request token information for later
        self.__authData['oauth_token'] = request_token['oauth_token']
        self.__authData['oauth_token_secret'] = request_token['oauth_token_secret']

        # Redirect the user to the Evernote authorization URL
        return client.get_authorize_url(request_token)

    def on_load_status(self, webkitView, *args, **kwargs):
        logging.debug("load status changed")
        status = webkitView.get_load_status()
        if status == status.FINISHED:
            logging.debug('Load finished')
            self.__spinner.hide()
            self.__status_label.set_text('')
        
        
    def on_navigation_requested(self, view, frame, req, data=None):
        logging.debug('Requesting new page')
        self.__spinner.show()
        self.__status_label.set_text(AuthDialog.STATUS_MESSAGE_CONNECTING)
        url = req.get_uri()
        if PROGRAM_NAME.lower() in url:
            query = urlparse.urlparse(url).query
            data = dict(urlparse.parse_qsl(query))
            
            try:
                self.__authData['oauth_verifier'] = data['oauth_verifier']
            except KeyError:
                logging.error('authorization failed')
                return False

            client = EvernoteClient(
                consumer_key=EverNoteConsumerInfo.CONSUMER_KEY,
                consumer_secret=EverNoteConsumerInfo.CONSUMER_SECRET,
                sandbox=True # Default: True
            )
            self.__auth_token = client.get_access_token(
                self.__authData['oauth_token'],
                self.__authData['oauth_token_secret'],
                self.__authData['oauth_verifier']
            )
            self.__dialog.response(100)
        return False




class SettingDialog:

    class KeyBinder:

        old_key_shortcut = None
        
        @staticmethod
        def callback(p1, p2):
            logging.debug("shotrcut key pressed")
            logging.debug("Run evercliper-clip")
            subprocess.call("evercliper-clip", shell=True)
            logging.debug("evercliper-clip done")
            
        @classmethod
        def bind_key(cls):
            Keybinder.init()
            shortcut = MetaData.get_snapshoot_shortcut()
            if Keybinder.bind(shortcut,cls.callback,""):
                if cls.old_key_shortcut is not None:
                    Keybinder.unbind(cls.old_key_shortcut)
                cls.old_key_shortcut = shortcut
            else:
                logging.error("Bind shortcut key failed ")


    class NotebookUpdater(threading.Thread):

        def __init__(self, spinner, image, notebook_selecter):
            threading.Thread.__init__(self)
            self.__spinner = spinner
            self.__image = image
            self.__notebook_selecter = notebook_selecter
            
        def run(self, ):
            self.__spinner.show()
            self.__spinner.start()
            self.__image.hide();

            evernote_adapter = EvernoteAdapter()
            NoteBookInfo.set_notebooks(evernote_adapter.get_notebook_name_guid_list())
            (default_notebook_name, default_notebook_guid) = MetaData.get_target_notebook()
            if default_notebook_name is None:
                (default_notebook_name, default_notebook_guid) = evernote_adapter.get_default_notebook()
                MetaData.set_target_notebook(default_notebook_name, default_notebook_guid)
            listmodel = Gtk.ListStore(str)
            notebook_index = -1
            default_notebook_index = -1
            for notebook in evernote_adapter.get_notebook_name_list():
                notebook_index += 1
                if default_notebook_name == notebook.decode('utf-8'):
                    default_notebook_index = notebook_index
                listmodel.append([notebook])
            self.__notebook_selecter.set_model(listmodel)
            self.__notebook_selecter.set_active(default_notebook_index)

            cell = Gtk.CellRendererText()

            # pack the cell into the beginning of the combobox, allocating
            # no more space than needed
            self.__notebook_selecter.pack_start(cell, True)
            self.__spinner.hide()
            if default_notebook_name is None:
                self.__image.set_from_icon_name('dialog-warning',Gtk.IconSize.BUTTON)
            else:
                self.__image.set_from_icon_name('accessories-text-editor',Gtk.IconSize.BUTTON)
            self.__image.show()
    
    
    BUTTON_LABLE_AUTHORIZE = 'authorize'
    BUTTON_LABLE_UNAUTHORIZE = 'remove authorization'

    UI_OBJECT_AUTH_BUTTON = 'authorize_button'
    UI_NOTEBOOK_SELECTER = 'default_note_book_selecter'
    UI_NOTEBOOK_SPINNER = 'notebook_spinner'
    UI_NOTEBOOK_IMAGE = 'notebook_image'
    UI_AUTH_STATUS_IMAGE = 'authorization_status_image'
    UI_AUTH_STATUS_SPINNER = 'auth_status_spinner'
    UI_SHORTCUT_ENTRY = 'shortcut_entry'
    UI_SHORTCUT_ALT_CHECK = 'alt_check'
    UI_RADIOBUTTON_EVERNOTE_INTERNATIONAL = 'radiobutton_evernote_international'
    UI_RADIOBUTTON_YINXIANG = 'radiobutton_yinxiang'

    def __init__(self, parent):

        builder = Gtk.Builder()
        builder.add_from_file(FileCatalog.get_evercliper_glade())
        self.__dialog = builder.get_object("SettingLogDialog")
        self.__dialog.set_icon_from_file(FileCatalog.get_evercliper_icon('evercliper_config.png'))
        self.__dialog.show_all()

        self.__radiobutton_yinxiang = builder.get_object(SettingDialog.UI_RADIOBUTTON_YINXIANG)
        self.__radiobutton_evernote_international = builder.get_object(SettingDialog.UI_RADIOBUTTON_EVERNOTE_INTERNATIONAL)
        if MetaData.get_evernote_host() == MetaData.VAL_Evernote_HOST_Yinxiang:
            self.__radiobutton_yinxiang.set_active(True)
        else:
            self.__radiobutton_evernote_international.set_active(True)
        
        self.__notebook_selecter = builder.get_object(SettingDialog.UI_NOTEBOOK_SELECTER)
        self.__notebook_selecter_changed_times = 0
        self.__notebook_spinner = builder.get_object(SettingDialog.UI_NOTEBOOK_SPINNER)
        self.__notebook_spinner.start()
        self.__notebook_image = builder.get_object(SettingDialog.UI_NOTEBOOK_IMAGE)
        self.__notebook_image.hide()
        self.__auth_status_image = builder.get_object(SettingDialog.UI_AUTH_STATUS_IMAGE)
        self.__auth_status_spinner = builder.get_object(SettingDialog.UI_AUTH_STATUS_SPINNER)
        self.__auth_status_spinner.hide()

        self.__notebook_updater =  None
        

        self.__shortcut_text_entry = builder.get_object(SettingDialog.UI_SHORTCUT_ENTRY)
        self.__shortcut_text_entry.set_text(MetaData.get_snapshoot_shortcut_value())

        self.__shortcut_alt_check_box = builder.get_object(SettingDialog.UI_SHORTCUT_ALT_CHECK)
        self.__shortcut_alt_check_box.set_active(MetaData.get_snapshoot_shortcut_alt_modifier())

        
        builder.connect_signals(
            {
                "on_close_button_clicked" : self.on_close_button_clicked,
                'on_authorize_button_clicked': self.on_authorize_button_clicked_cb,
                'on_default_note_book_selecter_changed': self.on_default_note_book_selecter_changed,
                'on_shortcut_entry_changed': self.on_shortcut_entry_changed,
                'on_alt_check_toggled': self.on_alt_check_toggled,
                'on_account_type_changed':self.on_account_type_changed
            }
        )
        authorize_button = builder.get_object(SettingDialog.UI_OBJECT_AUTH_BUTTON)
        authToken = KeyRing.get_auth_token()
        logging.debug('auth token = %s' % authToken)
        if authToken is None or authToken=='':
            authorize_button.set_label(SettingDialog.BUTTON_LABLE_AUTHORIZE)
            self.__auth_status_image.set_from_icon_name('dialog-warning',Gtk.IconSize.BUTTON)
            self.__notebook_image.set_from_icon_name('dialog-warning',Gtk.IconSize.BUTTON)
            self.__notebook_image.show()
            self.__notebook_spinner.hide()
        else:
            authorize_button.set_label(SettingDialog.BUTTON_LABLE_UNAUTHORIZE)
            self.__auth_status_image.set_from_icon_name('dialog-ok',Gtk.IconSize.BUTTON)
            self.__notebook_image.hide()
            self.__notebook_spinner.show()
            self.__notebook_updater = SettingDialog.NotebookUpdater(
                self.__notebook_spinner,
                self.__notebook_image,
                self.__notebook_selecter
            )
            self.__notebook_updater.start()
            
    def on_shortcut_entry_changed(self, widget):
        text = widget.get_text().upper()
        widget.set_text(text)
        if (text >= 'A' and text <= 'Z') or (text >= '0' and text <= '9'):
            widget.modify_fg(Gtk.StateFlags.NORMAL, None)
            MetaData.set_snapshoot_shortcut_value(text)
            logging.debug(MetaData.get_snapshoot_shortcut())
            SettingDialog.KeyBinder.bind_key()
        else:
            COLOR_INVALID = Color(50000, 0, 0) 
            widget.modify_fg(Gtk.StateFlags.NORMAL, COLOR_INVALID)

    def on_alt_check_toggled(self, checker):
        checked = checker.get_active()
        MetaData.set_snapshoot_shortcut_alt_modifier(checked)
        logging.debug(MetaData.get_snapshoot_shortcut())
        SettingDialog.KeyBinder.bind_key()
        

        
    def on_default_note_book_selecter_changed(self,combo):
        '''
        Change the default notebook 
        '''
        if self.__notebook_updater is None or not self.__notebook_updater.is_alive():
            text = combo.get_active_text()
            logging.debug('combo selected text: '+str(text))
            if text != None:
                guid = NoteBookInfo.get_guid_by_notebook_name(text)
                MetaData.set_target_notebook(text,guid)

    def on_account_type_changed(self, radiobutton):
        if radiobutton.get_active():
            if radiobutton is self.__radiobutton_yinxiang:
                logging.debug('change to yinxiang')
                MetaData.set_evernote_host_yinxiang()
            else:
                logging.debug('change to international')
                MetaData.set_evernote_host_international()
            if KeyRing.get_auth_token()!=None:
                logging.debug('remove auth from keyring')
                KeyRing.set_auth_token('')
                self.__auth_token.set_label(SettingDialog.BUTTON_LABLE_AUTHORIZE)
                self.__auth_status_image.set_from_icon_name('dialog-warning',Gtk.IconSize.BUTTON)
                self.__notebook_updater = SettingDialog.NotebookUpdater(
                    self.__notebook_spinner,
                    self.__notebook_image,
                    self.__notebook_selecter
                )
                MetaData.set_target_notebook(None,None)
                self.__notebook_updater.start()

            
    def on_authorize_button_clicked_cb(self, button):
        logging.debug('')
        if button.get_label() == SettingDialog.BUTTON_LABLE_AUTHORIZE:
            logging.debug('auth with Evernote')
            self.__auth_status_image.hide()
            self.__auth_status_spinner.show()
            dialog = AuthDialog()
            dialog.run()
            dialog.destroy()
            auth_token = dialog.get_auth_token()
            if auth_token :
                KeyRing.set_auth_token(auth_token)
                button.set_label(SettingDialog.BUTTON_LABLE_UNAUTHORIZE)
                self.__auth_status_image.set_from_icon_name('dialog-ok',Gtk.IconSize.BUTTON)
                self.__auth_status_image.show()
                self.__auth_status_spinner.hide()
                self.__notebook_updater = SettingDialog.NotebookUpdater(
                    self.__notebook_spinner,
                    self.__notebook_image,
                    self.__notebook_selecter
                )
                self.__notebook_updater.start()
            else:
                self.__auth_status_spinner.hide()
                self.__auth_status_image.show()
        else:
            logging.debug('remove auth from keyring')
            KeyRing.set_auth_token('')
            button.set_label(SettingDialog.BUTTON_LABLE_AUTHORIZE)
            self.__auth_status_image.set_from_icon_name('dialog-warning',Gtk.IconSize.BUTTON)
            self.__notebook_updater = SettingDialog.NotebookUpdater(
                self.__notebook_spinner,
                self.__notebook_image,
                self.__notebook_selecter
            )
            MetaData.set_target_notebook(None,None)
            self.__notebook_updater.start()
            

    def on_close_button_clicked(self, param):
        self.__dialog.response(0)

    def run(self,):
        self.__dialog.run()

    def destroy(self,):
        self.__dialog.destroy()

class StatusIcon:

    PNG_MAIN_ICON = FileCatalog.get_evercliper_icon('evercliper_main_icon.png') #  root.get_full_path('evernote_adapter','icon','main_icon.png')
    PNG_MAIN_ICON_UPLOAD = FileCatalog.get_evercliper_icon('evercliper_main_icon_upload.png') #root.get_full_path('evernote_adapter','icon','main_icon_upload.png')
    PNG_MAIN_ICON_ERROR = FileCatalog.get_evercliper_icon('evercliper_main_icon_error.png') # root.get_full_path('evernote_adapter','icon','main_icon_error.png')
    
    class NoteListenerManagerThread(threading.Thread):
        def __init__(self, indicator):
            threading.Thread.__init__(self)
            self.status_queue = Queue()
            NoteListenerThread.init(self.status_queue)
            Notify.init(__file__)
            self.__indicator = indicator

            
        def run(self,):
            NoteListenerThread.start()
            while True:
                filename = self.status_queue.get()
                if type(filename) is str:
                    # logging.debug(str(filename))
                    self.__indicator.set_icon(StatusIcon.PNG_MAIN_ICON_UPLOAD)
                    (name,guid) = MetaData.get_target_notebook()
                    
                    ret = EvernoteAdapter.savePicture(filename,guid)
                    if ret:
                        self.__indicator.set_icon(StatusIcon.PNG_MAIN_ICON)
                        time_str = time.ctime(os.path.getmtime(filename))
                        Notify.Notification.new('Snapshoot saved to Evernote',time_str,'').show()
                        os.remove(filename)
                    else:
                        self.__indicator.set_icon(StatusIcon.PNG_MAIN_ICON_ERROR)
                        Notify.Notification.new('Failed saving snapshoot to Evernote','','').show()
                else:
                    break
            pass

        def stop(self,):
            NoteListenerThread.stop()
                

    
    def __init__(self,):

        self.ind = AppIndicator.Indicator.new("evercliper-indicator",
                                              "indicator-messages",
                                              AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.ind.set_icon(StatusIcon.PNG_MAIN_ICON)

        menu = Gtk.Menu()

        # setting menu
        setting_item = Gtk.MenuItem("Setting")
        setting_item.connect("activate", self.on_setting)
        setting_item.show()
        menu.append(setting_item)

        # quit menu
        quit_item = Gtk.MenuItem("Quit")
        quit_item.connect("activate", self.on_quit)
        quit_item.show()
        menu.append(quit_item)

        self.ind.set_menu(menu)
        
        self.note_listener_manager = StatusIcon.NoteListenerManagerThread(self.ind)
        self.note_listener_manager.start()

    def on_setting(self, widget):
        settingDtalog = SettingDialog(widget)
        settingDtalog.run()
        settingDtalog.destroy()

    def on_quit(self, widget):
        self.note_listener_manager.stop()
        Gtk.main_quit(widget)
        sys.exit()


def get_lock(process_name):
    global lock_socket
    lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        lock_socket.bind('\0' + process_name)
    except socket.error:
        logging.error('Another process already running')
        sys.exit()

        

def main():
    try:
        MetaData.init_path()
        FORMAT = "<%(asctime)s> [ %(levelname)s %(filename)s:%(lineno)s - %(funcName)20s()  ] %(message)s"
        logging.basicConfig(filename = MetaData.LOG_FILE_NAME, level = logging.DEBUG, format=FORMAT)
        get_lock(__file__)
        
        logging.debug('init start')
        GLib.threads_init()
        Gdk.threads_init()
        Gdk.threads_enter()
        SettingDialog.KeyBinder.bind_key()
        StatusIcon()
        Gtk.main()
        Gdk.threads_leave()
    except Exception,e:
        logging.error(str(e))
        print e
        

if __name__ == '__main__':
    main()
