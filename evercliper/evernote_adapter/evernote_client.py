import os
import logging
from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types
from comm.util import KeyRing
import hashlib


class EvernoteAdapter():

    FILE_TYPE = ['PNG']

    def __init__(self,):
        auth_token = KeyRing.get_auth_token()
        if auth_token is None:
            self.__notebooks = []
        else:
            client = EvernoteClient(token=auth_token)
            noteStore = client.get_note_store()
            notebooks = noteStore.listNotebooks()
            self.__notebooks = [(notebook.name,notebook.guid,notebook.defaultNotebook) for notebook in notebooks]

    def get_notebook_name_list(self,):
        return [name for (name,guid,default) in self.__notebooks]

    def get_default_notebook(self,):
        if len(self.__notebooks)==0:
            return (None,None)
        else:
            return [ (name.decode('utf-8'),guid) for (name,guid,default) in self.__notebooks if default][0]

    def get_notebook_name_guid_list(self,):
        return [ (name,guid) for (name,guid,default) in self.__notebooks]
        
    @classmethod
    def savePicture(cls,filename, notebook_guid = None):
        logging.debug(str(filename))
        extension = filename.split('.')[-1]
        if extension.upper() not in cls.FILE_TYPE:
            logging.debug('Unsupported file type : %s' % filename)
            return False
        auth_token = KeyRing.get_auth_token()
        logging.debug('auth_token = '+str(auth_token))
        if auth_token is None:
            return False
        logging.debug('')
        client = EvernoteClient(token=auth_token)
        try:
            noteStore = client.get_note_store()
        except Exception, e:
            logging.error(str(e))
            logging.error('Auth token is not correct')
            return False
                
        note = Types.Note()
        if notebook_guid :
            note.notebookGuid = notebook_guid 
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
            note = noteStore.createNote(note)
        except Exception,e:
            logging.error(str(e))
            logging.error('error saving the note')
        
        logging.debug('Saving to Evernote Done, file = %s' % filename)
        return True

