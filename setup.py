from setuptools import setup, find_packages
import SetupHelper
import os
import re


def get_filename(path_list):
    '''
    A list of (path, reg)
    '''
    data_files = []
    for (path,reg) in path_list:
        if type(reg) is list:
            data_files.append((path,reg))
            continue
        if reg is not None:
            filename_reg = re.compile(reg)
        for root,dirs,files in os.walk(path):
            for filename in files:
                if reg is None:
                    m = True
                else:
                    m = filename_reg.match(filename)
                if m is not None:
                    data_files.append(
                        (root, [os.path.join(root,filename)])
                    )
    return data_files


setup(
    name = "evercliper",
    version = "0.1.1",
    maintainer='Channing',
    maintainer_email='channing.bj@gmail.com',
    license='GPL',
    URL='https://github.com/ChanningBJ/Evercliper',
    description='Evernote client which can make a screenshot and save to Evernote',
    packages = find_packages(),
    install_requires=[
        'evernote',
        'keyring',
        'pyinotify'
    ],
    # data_files = get_filename([
    #     ('evercliper/cliper/locale/','^.*\.mo$'),
    #     ('evercliper/cliper/po','^.*\.po$'),
    #     ('evercliper/cliper/theme',None),
    #     ('evercliper/evernote_adapter','^.*\.glade$'),
    #     ('evercliper/evernote_adapter/icon','^.*\.png$'),
    #     ('share/applications/', '^.*\.desktop$'),
    #     ('test/', '^.*\.ss$')
    #     ]),
    data_files = [
        ('share/locale/en_US/LC_MESSAGES/',['evercliper/cliper/locale/en_US/LC_MESSAGES/deepin-scrot.mo']),
        ('share/locale/zh_CN/LC_MESSAGES/',['evercliper/cliper/locale/zh_CN/LC_MESSAGES/deepin-scrot.mo']),
        ('share/locale/zh_TW/LC_MESSAGES/',['evercliper/cliper/locale/zh_TW/LC_MESSAGES/deepin-scrot.mo']),
        ('share/themes/evercliper/logo', ['evercliper/cliper/theme/logo/deepin-scrot.ico']),
        ('share/themes/evercliper/default', ['evercliper/cliper/theme/default/start_cursor.png']),
        ('share/themes/evercliper/default/color',
         ['evercliper/cliper/theme/default/color/yellow_dark.png',
          'evercliper/cliper/theme/default/color/wathet_dark.png',
          'evercliper/cliper/theme/default/color/gray.png',
          'evercliper/cliper/theme/default/color/white.png',
          'evercliper/cliper/theme/default/color/pink_dark.png',
          'evercliper/cliper/theme/default/color/wathet.png',
          'evercliper/cliper/theme/default/color/white_hover.png',
          'evercliper/cliper/theme/default/color/blue.png',
          'evercliper/cliper/theme/default/color/green_dark_hover.png',
          'evercliper/cliper/theme/default/color/blue_hover.png',
          'evercliper/cliper/theme/default/color/green.png',
          'evercliper/cliper/theme/default/color/red_dark.png',
          'evercliper/cliper/theme/default/color/pink.png',
          'evercliper/cliper/theme/default/color/pink_dark_hover.png',
          'evercliper/cliper/theme/default/color/blue_dark.png',
          'evercliper/cliper/theme/default/color/green_dark.png',
          'evercliper/cliper/theme/default/color/red_dark_hover.png',
          'evercliper/cliper/theme/default/color/red.png',
          'evercliper/cliper/theme/default/color/gray_hover.png',
          'evercliper/cliper/theme/default/color/yellow.png',
          'evercliper/cliper/theme/default/color/yellow_hover.png',
          'evercliper/cliper/theme/default/color/red_hover.png',
          'evercliper/cliper/theme/default/color/black.png',
          'evercliper/cliper/theme/default/color/wathet_hover.png',
          'evercliper/cliper/theme/default/color/gray_dark_hover.png',
          'evercliper/cliper/theme/default/color/pink_hover.png',
          'evercliper/cliper/theme/default/color/green_hover.png',
          'evercliper/cliper/theme/default/color/gray_dark.png',
          'evercliper/cliper/theme/default/color/wathet_dark_hover.png',
          'evercliper/cliper/theme/default/color/blue_dark_hover.png',
          'evercliper/cliper/theme/default/color/black_hover.png',
          'evercliper/cliper/theme/default/color/yellow_dark_hover.png']),
        ('share/themes/evercliper/default/action',
         ['evercliper/cliper/theme/default/action/normal_press.png',
          'evercliper/cliper/theme/default/action/download.jpg',
          'evercliper/cliper/theme/default/action/cancel_hover.png',
          'evercliper/cliper/theme/default/action/color_bg.png',
          'evercliper/cliper/theme/default/action/save_normal.png',
          'evercliper/cliper/theme/default/action/ellipse_hover.png',
          'evercliper/cliper/theme/default/action/rect_hover.png',
          'evercliper/cliper/theme/default/action/arrow_normal.png',
          'evercliper/cliper/theme/default/action/saveEverNote_hover.png',
          'evercliper/cliper/theme/default/action/finish_press.png',
          'evercliper/cliper/theme/default/action/small.png',
          'evercliper/cliper/theme/default/action/rect_press.png',
          'evercliper/cliper/theme/default/action/cancel_press.png',
          'evercliper/cliper/theme/default/action/line_press.png',
          'evercliper/cliper/theme/default/action/saveEverNote_normal.png',
          'evercliper/cliper/theme/default/action/small_hover.png',
          'evercliper/cliper/theme/default/action/undo_hover.png',
          'evercliper/cliper/theme/default/action/saveEverNote_press.png',
          'evercliper/cliper/theme/default/action/text_normal.png',
          'evercliper/cliper/theme/default/action/save_hover.png',
          'evercliper/cliper/theme/default/action/undo_press.png',
          'evercliper/cliper/theme/default/action/finish_normal.png',
          'evercliper/cliper/theme/default/action/ellipse_press.png',
          'evercliper/cliper/theme/default/action/big_press.png',
          'evercliper/cliper/theme/default/action/big_hover.png',
          'evercliper/cliper/theme/default/action/normal_hover.png',
          'evercliper/cliper/theme/default/action/images.jpg',
          'evercliper/cliper/theme/default/action/save_press.png',
          'evercliper/cliper/theme/default/action/big.png',
          'evercliper/cliper/theme/default/action/arrow_hover.png',
          'evercliper/cliper/theme/default/action/color_sep.png',
          'evercliper/cliper/theme/default/action/small_press.png',
          'evercliper/cliper/theme/default/action/arrow_press.png',
          'evercliper/cliper/theme/default/action/line_hover.png',
          'evercliper/cliper/theme/default/action/undo_normal.png',
          'evercliper/cliper/theme/default/action/text_press.png',
          'evercliper/cliper/theme/default/action/text_hover.png',
          'evercliper/cliper/theme/default/action/bg.png',
          'evercliper/cliper/theme/default/action/normal.png',
          'evercliper/cliper/theme/default/action/rect_normal.png',
          'evercliper/cliper/theme/default/action/sep.png',
          'evercliper/cliper/theme/default/action/ellipse_normal.png',
          'evercliper/cliper/theme/default/action/line_normal.png',
          'evercliper/cliper/theme/default/action/finish_hover.png',
          'evercliper/cliper/theme/default/action/cancel_normal.png']),
        ('share/pixmaps',
         ['evercliper/evernote_adapter/icon/evercliper_config.png',
          'evercliper/evernote_adapter/icon/evercliper_main_icon_error.png',
          'evercliper/evernote_adapter/icon/evercliper_main_icon.png',
          'evercliper/evernote_adapter/icon/evercliper_main_icon_upload.png'
         ]),
        ('share/pyshared/evercliper/evernote_adapter/',['evercliper/evernote_adapter/setting_dialog.glade'])
    ],
    entry_points = {
        'console_scripts': [
            'evercliper = evercliper:start_ui',
            'evercliper-clip = evercliper:do_scrot'
        ]
    }
)


