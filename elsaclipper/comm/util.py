import keyring
import json
import os
import logging
import threading
PROGRAM_NAME = 'elsaclipper'

class KeyRing:
    
    AUTH_TOKEN = 'auth-token'

    @classmethod
    def get_auth_token(cls):
        try:
            token = keyring.get_password(PROGRAM_NAME,cls.AUTH_TOKEN)
        except IOError:
            logging.error("Error get Keyring data: %s/%s" % (PROGRAM_NAME,cls.AUTH_TOKEN))
            return None
        if token == '':
            return None
        return token

    @classmethod
    def set_auth_token(cls, token):
        keyring.set_password(PROGRAM_NAME,cls.AUTH_TOKEN,token)


class EverNoteConsumerInfo:
    CONSUMER_KEY="channing153"
    CONSUMER_SECRET="37dccf460191fa6c"
        



class NoteBookInfo:

    notebook_dict = {}

    @classmethod
    def set_notebooks(cls, notebook_list):
        for (name,guid) in notebook_list:
            cls.notebook_dict[name] = guid

    @classmethod
    def get_guid_by_notebook_name(cls,name):
        return cls.notebook_dict[name]


class MetaData:
    LOG_FILE_NAME = os.path.expanduser(os.path.join('~/','.'+PROGRAM_NAME,PROGRAM_NAME+'.log'))
    DATA_FILENAME = os.path.expanduser(os.path.join('~/','.'+PROGRAM_NAME,'metadata.json'))
    DATA_FILE_DIR_NAME = os.path.expanduser(os.path.join('~/','.'+PROGRAM_NAME))
    DEFAULT_NOTE_BUFFER_PATH = os.path.expanduser(os.path.join('~/','.'+PROGRAM_NAME,'note_buffer_path'))
    
    KEY_TARGET_NOTEBOOK = 'target_note_book'
    KEY_NOTE_LISTENER_PID = 'note_listener_pid'
    KEY_NOTE_BUFFER_PATH = 'note_buffer_path'
    KEY_SHORTCUT_ALT = 'shotrcut_alt'
    KEY_SHORTCUT_VAL = 'shortcut_val'
    KEY_APP_PID = 'application_pid'
    KEY_Evernote_HOST = 'evernote_host'
    VAL_Evernote_HOST_Yinxiang = 'www.yinxiang.com'
    VAL_Evernote_HOST_International = 'www.evernote.com'

    DATA = {}
    DATA_LOCK = threading.RLock()

    @classmethod
    def init_path(cls):
        if not os.path.exists(cls.DATA_FILE_DIR_NAME):
            os.mkdir(cls.DATA_FILE_DIR_NAME)
        if not os.path.exists(cls.DEFAULT_NOTE_BUFFER_PATH):
            os.mkdir(cls.DEFAULT_NOTE_BUFFER_PATH)
        try:
            with open(cls.DATA_FILENAME,'r') as fp:
                cls.DATA = json.load(fp)
        except IOError:
            pass

    @classmethod
    def set_evernote_host_international(cls):
        with cls.DATA_LOCK:
            cls.DATA[cls.KEY_Evernote_HOST] = cls.VAL_Evernote_HOST_International
            with open(cls.DATA_FILENAME,'w') as fp:
                json.dump(cls.DATA,fp)

    @classmethod
    def set_evernote_host_yinxiang(cls):
        with cls.DATA_LOCK:
            cls.DATA[cls.KEY_Evernote_HOST] = cls.VAL_Evernote_HOST_Yinxiang
            with open(cls.DATA_FILENAME,'w') as fp:
                json.dump(cls.DATA,fp)

    @classmethod
    def get_evernote_host(cls):
        with cls.DATA_LOCK:
            return cls.DATA.get(cls.KEY_Evernote_HOST,cls.VAL_Evernote_HOST_Yinxiang)
            
        
    @classmethod
    def get_snapshoot_shortcut(cls):
        enable_alt = None
        val = None
        with cls.DATA_LOCK:
            val = cls.DATA.get(cls.KEY_SHORTCUT_VAL,'N')
            enable_alt = cls.DATA.get(cls.KEY_SHORTCUT_ALT,True)
        if enable_alt:
            return '<ctrl><alt>'+val
        else:
            return '<ctrl>'+val

    @classmethod
    def set_snapshoot_shortcut_alt_modifier(cls, enable):
        with cls.DATA_LOCK:
            cls.DATA[cls.KEY_SHORTCUT_ALT] = enable
            with open(cls.DATA_FILENAME,'w') as fp:
                json.dump(cls.DATA,fp)

    @classmethod
    def get_snapshoot_shortcut_alt_modifier(cls):
        with cls.DATA_LOCK:
            return cls.DATA.get(cls.KEY_SHORTCUT_ALT,True)

    @classmethod
    def get_snapshoot_shortcut_value(cls):
        with cls.DATA_LOCK:
            return cls.DATA.get(cls.KEY_SHORTCUT_VAL,'N')
            
                
    @classmethod
    def set_snapshoot_shortcut_value(cls, value):
        with cls.DATA_LOCK:
            cls.DATA[cls.KEY_SHORTCUT_VAL] = value
            with open(cls.DATA_FILENAME,'w') as fp:
                json.dump(cls.DATA,fp)

    @classmethod
    def get_note_buffer_path_name(cls):
        with cls.DATA_LOCK:
            path = cls.DATA.get(
                MetaData.KEY_NOTE_BUFFER_PATH,
                os.path.expanduser(os.path.join('~/','.'+PROGRAM_NAME,'note_buffer_path'))
            )
        return path

    @classmethod
    def set_note_buffer_path_name(cls, new_path):
        with cls.DATA_LOCK:
            cls.DATA[MetaData.KEY_NOTE_BUFFER_PATH] = new_path
            with open(cls.DATA_FILENAME,'w') as fp:
                json.dump(cls.DATA,fp)
        return True                
                    

    @classmethod
    def get_target_notebook(cls):
        '''
        Will return (notebook,guid), if target notebook is not set, will return (None,None)
        '''
        logging.debug('data = '+str(cls.DATA))
        with cls.DATA_LOCK:
            (name,guid) = cls.DATA.get(MetaData.KEY_TARGET_NOTEBOOK,(None,None))
        if name is not None and type(name) is str:
            name = name.decode('utf-8')
        return (name,guid)

    @classmethod
    def set_target_notebook(cls,notebook,guid):
        logging.debug('target notenook : (%s,%s), (notebook,guid)')
        with cls.DATA_LOCK:
            if notebook is None or guid is None:
                if MetaData.KEY_TARGET_NOTEBOOK in cls.DATA:
                    del(cls.DATA[MetaData.KEY_TARGET_NOTEBOOK])
            else:
                cls.DATA[MetaData.KEY_TARGET_NOTEBOOK] = (notebook,guid)
            with open(cls.DATA_FILENAME,'w') as fp:
                json.dump(cls.DATA,fp)
        return True

        
