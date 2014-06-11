import os
import root

class FileCatalogDebMode:
    '''
    Use this class if the program is installed using deb package
    '''
    def __init__(self, ):
        file_list = os.popen('dpkg -L python-evercliper')
        for line in file_list.readlines():
            line = line.strip()
            basename = os.path.split(line)[1]
            if basename == 'locale':
                self.__locale_path = line
            elif basename == 'themes':
                self.__theme_path = os.path.join(line,'evercliper')
            elif basename == 'deepin-scrot.ico':
                self.__deepin_scrot_icon_file_name = line
            elif basename == 'pixmaps':
                self.__evercliper_icon_path = line
            elif basename == 'setting_dialog.glade':
                self.__evercliper_glade_file_name = line
        
    def get_locale_path(self):
        return self.__locale_path

    def get_theme_path(self, theme_name):
        return os.path.join(self.__theme_path,theme_name)

    def get_deepin_scrot_icon(self):
        return self.__deepin_scrot_icon_file_name

    def get_evercliper_icon(self,icon_filename):
        return os.path.join(self.__evercliper_icon_path,icon_filename)

    def get_evercliper_glade(self):
        return self.__evercliper_glade_file_name
        
class FileCatalogSrcMode:
    '''
    Use this class if the program is run from source (not installed from deb package)
    '''
    def __init__(self, ):
        file_path = os.path.realpath(__file__)
        self.perfix = os.path.dirname(os.path.dirname(file_path))


    def get_locale_path(self):
        return os.path.join(self.perfix,'cliper/locale')

    def get_theme_path(self, theme_name):
        return os.path.join(self.perfix,'cliper/theme',theme_name)

    def get_deepin_scrot_icon(self):
        return os.path.join(self.perfix,'cliper/themes/logo/deepin-scrot.ico')

    def get_evercliper_icon(self,icon_filename):
        return os.path.join(self.perfix,'evernote_adapter/icon',icon_filename)        

    def get_evercliper_glade(self):
        return os.path.join(self.perfix,'evernote_adapter/setting_dialog.glade')        
        
class FileCatalog:
    file_catalog_instance = None

    @classmethod
    def detect_install_mode(cls):
        flag_file_name = root.get_full_path('comm','flagfile')
        if os.path.exists(flag_file_name):
            cls.file_catalog_instance = FileCatalogSrcMode()
        else:
            cls.file_catalog_instance = FileCatalogDebMode()

    @classmethod
    def get_locale_path(cls):
        if cls.file_catalog_instance is None:
            cls.detect_install_mode()
        return cls.file_catalog_instance.get_locale_path()

    @classmethod
    def get_theme_path(cls,theme_name):
        if cls.file_catalog_instance is None:
            cls.detect_install_mode()
        return cls.file_catalog_instance.get_theme_path(theme_name)
        
    @classmethod
    def get_deepin_scrot_icon(cls):
        if cls.file_catalog_instance is None:
            cls.detect_install_mode()
        return cls.file_catalog_instance.get_deepin_scrot_icon()

    @classmethod
    def get_evercliper_icon(cls,icon_filename):
        if cls.file_catalog_instance is None:
            cls.detect_install_mode()
        return cls.file_catalog_instance.get_evercliper_icon(icon_filename)

    @classmethod
    def get_evercliper_glade(cls):
        if cls.file_catalog_instance is None:
            cls.detect_install_mode()
        return cls.file_catalog_instance.get_evercliper_glade()
        
if __name__ == '__main__':
    print os.path.realpath(__file__)
