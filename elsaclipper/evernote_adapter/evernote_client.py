import os
import logging
from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as ErrorTypes
from comm.util import KeyRing
from comm.util import EverNoteConsumerInfo
from comm.util import MetaData
import hashlib


class EvernoteAdapter():

    FILE_TYPE = ['PNG']
    notebook_guid = None
    notebook_name = None
    note_store = None


    STATUS_OK = 0
    STATUS_NO_AUTH_TOKEN = 1
    STATUS_NOTEBOOK_DELETED = 2

    STATUS_SAVE_OK = 3
    STATUS_UNSUPPORTED_FILE_TYPE = 4
    STATUS_SAVE_ERROR = 5
    STATUS_SAVE_ERROR_NOTEBOOK_DELETED = 6
    
    @classmethod
    def login(cls,):
        '''
        Get the notebook name and guid, get note_store
        Returns:
          STATUS_OK              : Everything is fine
          STATUS_NO_AUTH_TOKEN   : No auth token can be found in keying, user should authorize this application
          STATUS_NOTEBOOK_DELETED: The application is authorized but 'app notebooks' maybe deleted by user, user should authorize this application again.

        For mote information about "app notebooks": http://dev.yinxiang.com/doc/articles/app_notebook.php
        '''
        auth_token = KeyRing.get_auth_token()
        if auth_token is not None:
            client = EvernoteClient(
                consumer_key=EverNoteConsumerInfo.CONSUMER_KEY,
                consumer_secret=EverNoteConsumerInfo.CONSUMER_SECRET,
                service_host = MetaData.get_evernote_host(),
                token=auth_token,
                sandbox=False)
            cls.note_store = client.get_note_store()
            notebooks = cls.note_store.listNotebooks()
            len_notebooks = len(notebooks)
            if len_notebooks == 0:
                logging.error("Application notebook has been deleted")
                return cls.STATUS_NOTEBOOK_DELETED
            cls.notebook_name = notebooks[0].name
            cls.notebook_guid = notebooks[0].guid
            return cls.STATUS_OK
        else:
            return cls.STATUS_NO_AUTH_TOKEN

    @classmethod
    def logoff(cls):
        cls.notebook_guid = None
        cls.notebook_name = None
        cls.note_store = None
            
    @classmethod
    def auth_OK(cls):
        return cls.note_store is not None

    @classmethod
    def get_notebook_name(cls):
        if cls.notebook_name is None:
            return ''
        else:
            return cls.notebook_name
            
    @classmethod
    def savePicture(cls,filename, ):
        '''
        Save the picture to evernote
        Returns:
          STATUS_SAVE_OK                    : The picture is saved to evernote
          STATUS_UNSUPPORTED_FILE_TYPE      : The file type if not supported
          STATUS_SAVE_ERROR                 : Error saving picture to Evernote
          STATUS_SAVE_ERROR_NOTEBOOK_DELETED: Target notebook is deleted 
        '''
        logging.debug(str(filename))
        extension = filename.split('.')[-1]
        if extension.upper() not in cls.FILE_TYPE:
            logging.debug('Unsupported file type : %s' % filename)
            return cls.STATUS_UNSUPPORTED_FILE_TYPE
        # auth_token = KeyRing.get_auth_token()
        # logging.debug('auth_token = '+str(auth_token))
        # if auth_token is None:
            # return False
        # logging.debug('')
        # client = EvernoteClient(token=auth_token)
        # try:
        #     noteStore = cls.client.get_note_store()
        # except Exception, e:
        #     logging.error(str(e))
        #     logging.error('Auth token is not correct')
        #     return False
                
        note = Types.Note()
        # if notebook_guid :
        note.notebookGuid = cls.notebook_guid
        note.title = os.path.basename(filename)
        note.content = '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
        note.content += '<en-note><br/>'

        # Calculate the md5 hash of the png
        md5 = hashlib.md5()
        with open(filename,'rb') as f:
            png_bytes = f.read()
        md5.update(png_bytes)
        md5hash = md5.hexdigest()

        # Create the Data type for evernote that goes into a resource
        png_data = Types.Data()
        png_data.bodyHash = md5hash
        png_data.size = len(png_bytes) 
        png_data.body = png_bytes

        # Add a link in the evernote boy for this content
        #<en-media width="640" height="480" type="image/jpeg" hash="f03c1c2d96bc67eda02968c8b5af9008"/>
        link = '<en-media type="image/png" hash="%s"/>' % md5hash
        note.content += link
        note.content += '</en-note>'

        # Create a resource for the note that contains the png
        png_resource = Types.Resource()
        png_resource.data = png_data
        png_resource.mime = "application/png"

        # Create a resource list to hold the png resource
        resource_list = []
        resource_list.append(png_resource)

        # Set the note's resource list
        note.resources = resource_list
        try:
            note =  cls.note_store.createNote(note)
        except ErrorTypes.EDAMNotFoundException:
            # the target notenook is deleted
            logging.error('The target notenook is deleted')
            return cls.STATUS_SAVE_ERROR_NOTEBOOK_DELETED

        # TODO: auth expired
        
        logging.debug('Saving to Evernote Done, file = %s' % filename)
        return cls.STATUS_SAVE_OK

