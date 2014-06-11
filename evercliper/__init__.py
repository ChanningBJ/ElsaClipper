import sys
import os
sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)))


    
def start_ui():
    import evernote_adapter.main_ui
    evernote_adapter.main_ui.main()

    
                
def do_scrot():
    import cliper.src.deepinScrot
    cliper.src.deepinScrot.processArguments()



if __name__ == '__main__':
    start_ui()
