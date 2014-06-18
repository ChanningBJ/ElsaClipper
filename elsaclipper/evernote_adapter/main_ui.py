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
import root


class AuthDialog():
    # EverNoteConsumerInfo.CONSUMER_KEY="channing"
    # EverNoteConsumerInfo.CONSUMER_SECRET="35627ab2ee94809f"

    STATUS_MESSAGE_CONNECTING = 'connecting ...'

    def __init__(self, ):
        self.__auth_token = None
        self.__authData = {}
        builder = Gtk.Builder()
        builder.add_from_file(FileCatalog.get_elsaclipper_glade())
        self.__dialog = builder.get_object('auth_dialog')
        self.__dialog.set_icon_from_file(FileCatalog.get_elsaclipper_icon('elsaclipper_config.png'))
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
            service_host = MetaData.get_evernote_host(),
            sandbox=False # Default: True ; if using yinxiang, set service_host='www.yinxiang.com' ; in using Evernote International, set  service_host='www.evernote.com'
        )

        callbackUrl = "http://"+PROGRAM_NAME
        request_token = client.get_request_token(callbackUrl)
        # Save the request token information for later
        self.__authData['oauth_token'] = request_token['oauth_token']
        self.__authData['oauth_token_secret'] = request_token['oauth_token_secret']

        # Redirect the user to the Evernote authorization URL
        url = client.get_authorize_url(request_token)
        logging.debug(url)
        return url

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
                service_host = MetaData.get_evernote_host(),
                sandbox=False # Default: True
            )
            self.__auth_token = client.get_access_token(
                self.__authData['oauth_token'],
                self.__authData['oauth_token_secret'],
                self.__authData['oauth_verifier']
            )
            self.__dialog.response(100)
        return False


class ErrorDialog():
    MESSAGE_AUTH_EXPIRED = 'Your authentication has expired, please authorize again.'
    MESSAGE_NO_AUTH = 'You need authorize this application to access your Evernote account before using it.'
    MESSAGE_NOTEBOOK_DELETED = 'Cann\'t find notebook %s, please authorize again and select a notebook'

    def __init__(self, message):
        self.__dialog = Gtk.MessageDialog(
            None, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, "Authorization Needed")
        self.__dialog.format_secondary_text(message)

    def run(self):
        self.__dialog.run()

    def destory(self):
        self.__dialog.destroy()
        
        

class SettingDialog:

    class KeyBinder:

        old_key_shortcut = None
        
        @staticmethod
        def callback(p1, p2):
            logging.debug("shotrcut key pressed")
            logging.debug("Run elsaclipper-clip")
            flag_file_name = root.get_full_path('comm','flagfile')
            if os.path.exists(flag_file_name):
                init_file = root.get_full_path('__init__.py')
                subprocess.call("python "+init_file+" clip", shell=True)
            else:
                subprocess.call("elsaclipper-clip", shell=True)
            logging.debug("elsaclipper-clip done")
            
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


    BUTTON_LABLE_AUTHORIZE = 'authorize'
    BUTTON_LABLE_UNAUTHORIZE = 'remove authorization'

    UI_OBJECT_AUTH_BUTTON = 'authorize_button'
    UI_AUTH_STATUS_IMAGE = 'authorization_status_image'
    UI_AUTH_STATUS_SPINNER = 'auth_status_spinner'
    UI_SHORTCUT_ENTRY = 'shortcut_entry'
    UI_SHORTCUT_ALT_CHECK = 'alt_check'
    UI_RADIOBUTTON_EVERNOTE_INTERNATIONAL = 'radiobutton_evernote_international'
    UI_RADIOBUTTON_YINXIANG = 'radiobutton_yinxiang'

    def __init__(self, parent, auth_event):
        self.__auth_event = auth_event
        builder = Gtk.Builder()
        builder.add_from_file(FileCatalog.get_elsaclipper_glade())
        self.__dialog = builder.get_object("SettingLogDialog")
        self.__dialog.set_icon_from_file(FileCatalog.get_elsaclipper_icon('elsaclipper_config.png'))
        self.__dialog.show_all()

        self.__radiobutton_yinxiang = builder.get_object(SettingDialog.UI_RADIOBUTTON_YINXIANG)
        self.__radiobutton_evernote_international = builder.get_object(SettingDialog.UI_RADIOBUTTON_EVERNOTE_INTERNATIONAL)
        if MetaData.get_evernote_host() == MetaData.VAL_Evernote_HOST_Yinxiang:
            self.__radiobutton_yinxiang.set_active(True)
        else:
            self.__radiobutton_evernote_international.set_active(True)

        # self.__notebook_selecter = builder.get_object(SettingDialog.UI_NOTEBOOK_SELECTER)
        # self.__notebook_selecter_changed_times = 0
        # self.__notebook_spinner = builder.get_object(SettingDialog.UI_NOTEBOOK_SPINNER)
        # self.__notebook_spinner.start()
        # self.__notebook_image = builder.get_object(SettingDialog.UI_NOTEBOOK_IMAGE)
        # self.__notebook_image.hide()
        self.__auth_status_image = builder.get_object(SettingDialog.UI_AUTH_STATUS_IMAGE)
        self.__auth_status_spinner = builder.get_object(SettingDialog.UI_AUTH_STATUS_SPINNER)
        self.__auth_status_spinner.hide()

        # self.__notebook_updater =  None
        

        self.__shortcut_text_entry = builder.get_object(SettingDialog.UI_SHORTCUT_ENTRY)
        self.__shortcut_text_entry.set_text(MetaData.get_snapshoot_shortcut_value())

        self.__shortcut_alt_check_box = builder.get_object(SettingDialog.UI_SHORTCUT_ALT_CHECK)
        self.__shortcut_alt_check_box.set_active(MetaData.get_snapshoot_shortcut_alt_modifier())

        
        builder.connect_signals(
            {
                "on_close_button_clicked" : self.on_close_button_clicked,
                'on_authorize_button_clicked': self.on_authorize_button_clicked_cb,
                'on_shortcut_entry_changed': self.on_shortcut_entry_changed,
                'on_alt_check_toggled': self.on_alt_check_toggled,
                'on_account_type_changed':self.on_account_type_changed
            }
        )
        self.__authorize_button = builder.get_object(SettingDialog.UI_OBJECT_AUTH_BUTTON)
        authToken = KeyRing.get_auth_token()
        logging.debug('auth token = %s' % authToken)
        if authToken is None or authToken=='':
            self.__authorize_button.set_label(SettingDialog.BUTTON_LABLE_AUTHORIZE)
            self.__auth_status_image.set_from_icon_name('dialog-warning',Gtk.IconSize.BUTTON)
            # self.__notebook_image.set_from_icon_name('dialog-warning',Gtk.IconSize.BUTTON)
            # self.__notebook_image.show()
            # self.__notebook_spinner.hide()
        else:
            self.__authorize_button.set_label(SettingDialog.BUTTON_LABLE_UNAUTHORIZE)
            self.__auth_status_image.set_from_icon_name('dialog-ok',Gtk.IconSize.BUTTON)
            # self.__notebook_image.hide()
            # self.__notebook_spinner.show()
            # self.__notebook_updater = SettingDialog.NotebookUpdater(
            #     self.__notebook_spinner,
            #     self.__notebook_image,
            #     self.__notebook_selecter
            # )
            # self.__notebook_updater.start()
            
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
        

        
    # def on_default_note_book_selecter_changed(self,combo):
    #     '''
    #     Change the default notebook 
    #     '''
    #     if self.__notebook_updater is None or not self.__notebook_updater.is_alive():
    #         text = combo.get_active_text()
    #         logging.debug('combo selected text: '+str(text))
    #         if text != None:
    #             guid = NoteBookInfo.get_guid_by_notebook_name(text)
    #             MetaData.set_target_notebook(text,guid)

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
                self.__authorize_button.set_label(SettingDialog.BUTTON_LABLE_AUTHORIZE)
                self.__auth_status_image.set_from_icon_name('dialog-warning',Gtk.IconSize.BUTTON)
                # self.__notebook_updater = SettingDialog.NotebookUpdater(
                #     self.__notebook_spinner,
                #     self.__notebook_image,
                #     self.__notebook_selecter
                # )
                # MetaData.set_target_notebook(None,None)
                # self.__notebook_updater.start()

            
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
                self.__auth_event.set()
            else:
                self.__auth_status_spinner.hide()
                self.__auth_status_image.show()
        else:
            logging.debug('remove auth from keyring')
            KeyRing.set_auth_token('')
            EvernoteAdapter.logoff()
            button.set_label(SettingDialog.BUTTON_LABLE_AUTHORIZE)
            self.__auth_status_image.set_from_icon_name('dialog-warning',Gtk.IconSize.BUTTON)
            # self.__notebook_updater = SettingDialog.NotebookUpdater(
            #     self.__notebook_spinner,
            #     self.__notebook_image,
            #     self.__notebook_selecter
            # )
            # MetaData.set_target_notebook(None,None)
            # self.__notebook_updater.start()
            

    def on_close_button_clicked(self, param):
        self.__dialog.response(0)

    def run(self,):
        self.__dialog.run()

    def destroy(self,):
        self.__dialog.destroy()

class StatusIcon:

    PNG_MAIN_ICON = FileCatalog.get_elsaclipper_icon('elsaclipper_main_icon.png') #  root.get_full_path('evernote_adapter','icon','main_icon.png')
    PNG_MAIN_ICON_UPLOAD = FileCatalog.get_elsaclipper_icon('elsaclipper_main_icon_upload.png') #root.get_full_path('evernote_adapter','icon','main_icon_upload.png')
    PNG_MAIN_ICON_ERROR = FileCatalog.get_elsaclipper_icon('elsaclipper_main_icon_error.png') # root.get_full_path('evernote_adapter','icon','main_icon_error.png')
    
    class NoteListenerManagerThread(threading.Thread):
        def __init__(self, status_icon, auth_event):
            threading.Thread.__init__(self)
            self.status_queue = Queue()
            NoteListenerThread.init(self.status_queue)
            Notify.init(__file__)
            self.__status_icon = status_icon
            self.__auth_event = auth_event

            
        def run(self,):
            
            self.__status_icon.change_state(StatusIcon.STATE_NORMAL)
                
            NoteListenerThread.start()
            while True:
                filename = self.status_queue.get()
                if type(filename) is str:
                    # logging.debug(str(filename))

                    if not EvernoteAdapter.auth_OK():
                        login_res = EvernoteAdapter.login()
                        while login_res!=EvernoteAdapter.STATUS_LOGIN_OK:
                            if login_res == EvernoteAdapter.STATUS_LOGIN_AUTH_EXPIRED:
                                self.__status_icon.change_state(StatusIcon.STATE_AUTH_EXPIRED)
                            elif login_res == EvernoteAdapter.STATUS_LOGIN_NO_AUTH_TOKEN:
                                self.__status_icon.change_state(StatusIcon.STATE_NOTAUTHED)
                            elif login_res == EvernoteAdapter.STATE_NOTEBOOK_DELETED:
                                self.__status_icon.change_state(StatusIcon.STATE_NOTEBOOK_DELETED)
                            self.__auth_event.clear()
                            self.__auth_event.wait()
                            if not NoteListenerThread.is_running():
                                return
                            login_res = EvernoteAdapter.login()
                    #     self.__status_icon.change_state(StatusIcon.STATE_NOTAUTHED)
                    #     # self.__indicator.set_icon(StatusIcon.PNG_MAIN_ICON_ERROR)
                    #     self.__auth_event.clear()
                    #     self.__auth_event.wait()
                    #     if not NoteListenerThread.is_running():
                    #         return
                    #     logging.debug('Trying login')
                    #     EvernoteAdapter.login()
                    self.__status_icon.change_state(StatusIcon.STATE_UPLADING)
                    # self.__indicator.set_icon(StatusIcon.PNG_MAIN_ICON_UPLOAD)
                    while True:
                        ret = EvernoteAdapter.savePicture(filename) 
                        if ret == EvernoteAdapter.STATUS_SAVE_OK :
                            self.__status_icon.change_state(StatusIcon.STATE_NORMAL)
                            time_str = time.ctime(os.path.getmtime(filename))
                            Notify.Notification.new('Snapshoot saved to Evernote',time_str,
                                                    FileCatalog.get_elsaclipper_icon('elseclipper_save_icon.png')
                                                ).show()
                            os.remove(filename)
                            break
                        elif ret == EvernoteAdapter.STATUS_SAVE_ERROR_NOTEBOOK_DELETED:
                            self.__status_icon.change_state(StatusIcon.STATE_NOTEBOOK_DELETED)
                            self.__auth_event.clear()
                            self.__auth_event.wait()
                            if not NoteListenerThread.is_running():
                                return
                            logging.debug('Trying login')
                            EvernoteAdapter.login()
                else:
                    break
            pass

        def stop(self,):
            NoteListenerThread.stop()
            self.__auth_event.set()
                
    STATE_NORMAL = 0
    STATE_UPLADING = 1
    STATE_NOTEBOOK_DELETED = 2
    STATE_NOTAUTHED = 3
    STATE_AUTH_EXPIRED = 4

    ERROR_MSG_FAILED_SAVING = 'Failed saving snapshoot to Evernote'
    ERROR_MSG_NOTAUTHED = 'Authorization is needed before uploading any screenshot.'
    ERROR_MSG_NOTEBOOK_DELETED = 'Notebook %s is deleted, please authorize again'
    ERROR_MSG_AUTH_EXPIRED = 'Authorization expired, please authorize again'
    
    
    def __init__(self,):

        self.ind = AppIndicator.Indicator.new("elsaclipper-indicator",
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

        # error message menu
        self.error_item = Gtk.MenuItem("Error message")
        self.error_item.hide()
        menu.append(self.error_item)
        
        # quit menu
        quit_item = Gtk.MenuItem("Quit")
        quit_item.connect("activate", self.on_quit)
        quit_item.show()
        menu.append(quit_item)

        menu.set_has_tooltip(True)
        menu.set_tooltip_text("Make screenshot and save to Evernote")
        menu.trigger_tooltip_query()
        self.ind.set_menu(menu)

        self.__auth_event = threading.Event()
        self.note_listener_manager = StatusIcon.NoteListenerManagerThread(self,self.__auth_event)
        self.note_listener_manager.start()

    def show_error_message(self, msg):
        menu_sub = Gtk.Menu()
        error_info_item = Gtk.MenuItem(msg)
        error_info_item.show()
        menu_sub.append(error_info_item)        
        self.error_item.set_submenu(menu_sub)
        self.error_item.show()

        
    def change_state(self,state):
        cls = self.__class__
        if state == cls.STATE_NORMAL:
            logging.debug("State change to STATE_NORMAL")
            self.ind.set_icon(cls.PNG_MAIN_ICON)
            self.error_item.hide()
        elif state == cls.STATE_UPLADING:
            logging.debug("State change to STATE_UPLADING")
            self.ind.set_icon(cls.PNG_MAIN_ICON_UPLOAD)
            self.error_item.hide()
        elif state == cls.STATE_NOTAUTHED:
            logging.debug("State change to STATE_NOTAUTHED")
            self.ind.set_icon(cls.PNG_MAIN_ICON_ERROR)
            self.show_error_message(cls.ERROR_MSG_NOTAUTHED)
            # self.error_info_item.set_label(cls.ERROR_MSG_NOTAUTHED)
            Notify.Notification.new(cls.ERROR_MSG_FAILED_SAVING,
                                    cls.ERROR_MSG_NOTAUTHED,
                                    FileCatalog.get_elsaclipper_icon('elseclipper_alert_icon.png')
                                ).show()
        elif state == cls.STATE_NOTEBOOK_DELETED:
            logging.debug("State change to STATE_NOTEBOOK_DELETED")
            self.ind.set_icon(cls.PNG_MAIN_ICON_ERROR)
            self.show_error_message(cls.ERROR_MSG_NOTEBOOK_DELETED % (EvernoteAdapter.get_notebook_name()))
            # self.error_info_item.set_label('sdfsd')
            # self.error_info_item.set_label(
            #     cls.ERROR_MSG_NOTEBOOK_DELETED % (EvernoteAdapter.get_notebook_name())
            # )
            Notify.Notification.new(cls.ERROR_MSG_FAILED_SAVING,
                                    cls.ERROR_MSG_NOTEBOOK_DELETED % (EvernoteAdapter.get_notebook_name()),
                                    FileCatalog.get_elsaclipper_icon('elseclipper_alert_icon.png')
                                ).show()
            KeyRing.set_auth_token('')
        elif state==cls.STATE_AUTH_EXPIRED:
            logging.debug("State change to STATE_AUTH_EXPIRED")
            self.ind.set_icon(cls.PNG_MAIN_ICON_ERROR)
            self.show_error_message(cls.ERROR_MSG_AUTH_EXPIRED)
            Notify.Notification.new(cls.ERROR_MSG_AUTH_EXPIRED,
                                    '',
                                    FileCatalog.get_elsaclipper_icon('elseclipper_alert_icon.png')
                                ).show()
            KeyRing.set_auth_token('')
    def show_error(self,message):
        self.error_info_item.set_label(message)
        self.error_item.show()

    def hide_error(self):
        self.error_item.hide()
        
    def on_setting(self, widget):
        settingDtalog = SettingDialog(widget, self.__auth_event)
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
