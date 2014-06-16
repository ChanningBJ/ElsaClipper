
import pyinotify
from comm.util import MetaData
import os

class NoteListenerThread():
    class NewFileHandler(pyinotify.ProcessEvent):
        def process_IN_CLOSE_WRITE(self, event):
            filename = os.path.join(event.path,event.name)
            NoteListenerThread.status_queue.put(filename)

    notify_thread = None
    status_queue = None

    @classmethod
    def init(cls, statue_queue):
        cls.status_queue = statue_queue
    
    @classmethod
    def start(cls):
        '''
        Start the listening thread, is another thread is alreay started, stop it first
        '''
        if cls.notify_thread is not None and cls.notify_thread.is_alive():
            cls.notify_thread.stop()

        pathname = MetaData.get_note_buffer_path_name()
        # get all not uploaded files
        file_list = [ files for root,dirs,files in os.walk(pathname) ][0]
        for filename in file_list:
            NoteListenerThread.status_queue.put(os.path.join(pathname,filename))

        wm = pyinotify.WatchManager()
        wm.add_watch(pathname, pyinotify.IN_CLOSE_WRITE, rec=True)
        eh = cls.NewFileHandler()
        cls.notify_thread = pyinotify.ThreadedNotifier(wm,eh)
        cls.notify_thread.start()

    @classmethod
    def stop(cls):
        if cls.notify_thread is not None:
            cls.notify_thread.stop()
            cls.notify_thread = None
            cls.status_queue.put(None)


    @classmethod
    def is_running(cls):
        return cls.notify_thread is not None
