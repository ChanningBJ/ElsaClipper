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
    name = "elsaclipper",
    version = "0.1.1",
    maintainer='Channing',
    maintainer_email='channing.bj@gmail.com',
    license='GPL',
    URL='https://github.com/ChanningBJ/ElsaClipper',
    description='Evernote client which can make a screenshot and save to Evernote',
    packages = find_packages(),
    install_requires=[
        'evernote',
        'keyring',
        'pyinotify'
    ],
    # data_files = get_filename([
    #     ('elsaclipper/cliper/locale/','^.*\.mo$'),
    #     ('elsaclipper/cliper/po','^.*\.po$'),
    #     ('elsaclipper/cliper/theme',None),
    #     ('elsaclipper/evernote_adapter','^.*\.glade$'),
    #     ('elsaclipper/evernote_adapter/icon','^.*\.png$'),
    #     ('share/applications/', '^.*\.desktop$'),
    #     ('test/', '^.*\.ss$')
    #     ]),
    data_files = [
        ('share/locale/en_US/LC_MESSAGES/',['elsaclipper/cliper/locale/en_US/LC_MESSAGES/deepin-scrot.mo']),
        ('share/locale/zh_CN/LC_MESSAGES/',['elsaclipper/cliper/locale/zh_CN/LC_MESSAGES/deepin-scrot.mo']),
        ('share/locale/zh_TW/LC_MESSAGES/',['elsaclipper/cliper/locale/zh_TW/LC_MESSAGES/deepin-scrot.mo']),
        ('share/themes/elsaclipper/logo', ['elsaclipper/cliper/theme/logo/deepin-scrot.ico']),
        ('share/themes/elsaclipper/default', ['elsaclipper/cliper/theme/default/start_cursor.png']),
        ('share/themes/elsaclipper/default/color',
         ['elsaclipper/cliper/theme/default/color/yellow_dark.png',
          'elsaclipper/cliper/theme/default/color/wathet_dark.png',
          'elsaclipper/cliper/theme/default/color/gray.png',
          'elsaclipper/cliper/theme/default/color/white.png',
          'elsaclipper/cliper/theme/default/color/pink_dark.png',
          'elsaclipper/cliper/theme/default/color/wathet.png',
          'elsaclipper/cliper/theme/default/color/white_hover.png',
          'elsaclipper/cliper/theme/default/color/blue.png',
          'elsaclipper/cliper/theme/default/color/green_dark_hover.png',
          'elsaclipper/cliper/theme/default/color/blue_hover.png',
          'elsaclipper/cliper/theme/default/color/green.png',
          'elsaclipper/cliper/theme/default/color/red_dark.png',
          'elsaclipper/cliper/theme/default/color/pink.png',
          'elsaclipper/cliper/theme/default/color/pink_dark_hover.png',
          'elsaclipper/cliper/theme/default/color/blue_dark.png',
          'elsaclipper/cliper/theme/default/color/green_dark.png',
          'elsaclipper/cliper/theme/default/color/red_dark_hover.png',
          'elsaclipper/cliper/theme/default/color/red.png',
          'elsaclipper/cliper/theme/default/color/gray_hover.png',
          'elsaclipper/cliper/theme/default/color/yellow.png',
          'elsaclipper/cliper/theme/default/color/yellow_hover.png',
          'elsaclipper/cliper/theme/default/color/red_hover.png',
          'elsaclipper/cliper/theme/default/color/black.png',
          'elsaclipper/cliper/theme/default/color/wathet_hover.png',
          'elsaclipper/cliper/theme/default/color/gray_dark_hover.png',
          'elsaclipper/cliper/theme/default/color/pink_hover.png',
          'elsaclipper/cliper/theme/default/color/green_hover.png',
          'elsaclipper/cliper/theme/default/color/gray_dark.png',
          'elsaclipper/cliper/theme/default/color/wathet_dark_hover.png',
          'elsaclipper/cliper/theme/default/color/blue_dark_hover.png',
          'elsaclipper/cliper/theme/default/color/black_hover.png',
          'elsaclipper/cliper/theme/default/color/yellow_dark_hover.png']),
        ('share/themes/elsaclipper/default/action',
         ['elsaclipper/cliper/theme/default/action/normal_press.png',
          'elsaclipper/cliper/theme/default/action/download.jpg',
          'elsaclipper/cliper/theme/default/action/cancel_hover.png',
          'elsaclipper/cliper/theme/default/action/color_bg.png',
          'elsaclipper/cliper/theme/default/action/save_normal.png',
          'elsaclipper/cliper/theme/default/action/ellipse_hover.png',
          'elsaclipper/cliper/theme/default/action/rect_hover.png',
          'elsaclipper/cliper/theme/default/action/arrow_normal.png',
          'elsaclipper/cliper/theme/default/action/saveEverNote_hover.png',
          'elsaclipper/cliper/theme/default/action/finish_press.png',
          'elsaclipper/cliper/theme/default/action/small.png',
          'elsaclipper/cliper/theme/default/action/rect_press.png',
          'elsaclipper/cliper/theme/default/action/cancel_press.png',
          'elsaclipper/cliper/theme/default/action/line_press.png',
          'elsaclipper/cliper/theme/default/action/saveEverNote_normal.png',
          'elsaclipper/cliper/theme/default/action/small_hover.png',
          'elsaclipper/cliper/theme/default/action/undo_hover.png',
          'elsaclipper/cliper/theme/default/action/saveEverNote_press.png',
          'elsaclipper/cliper/theme/default/action/text_normal.png',
          'elsaclipper/cliper/theme/default/action/save_hover.png',
          'elsaclipper/cliper/theme/default/action/undo_press.png',
          'elsaclipper/cliper/theme/default/action/finish_normal.png',
          'elsaclipper/cliper/theme/default/action/ellipse_press.png',
          'elsaclipper/cliper/theme/default/action/big_press.png',
          'elsaclipper/cliper/theme/default/action/big_hover.png',
          'elsaclipper/cliper/theme/default/action/normal_hover.png',
          'elsaclipper/cliper/theme/default/action/images.jpg',
          'elsaclipper/cliper/theme/default/action/save_press.png',
          'elsaclipper/cliper/theme/default/action/big.png',
          'elsaclipper/cliper/theme/default/action/arrow_hover.png',
          'elsaclipper/cliper/theme/default/action/color_sep.png',
          'elsaclipper/cliper/theme/default/action/small_press.png',
          'elsaclipper/cliper/theme/default/action/arrow_press.png',
          'elsaclipper/cliper/theme/default/action/line_hover.png',
          'elsaclipper/cliper/theme/default/action/undo_normal.png',
          'elsaclipper/cliper/theme/default/action/text_press.png',
          'elsaclipper/cliper/theme/default/action/text_hover.png',
          'elsaclipper/cliper/theme/default/action/bg.png',
          'elsaclipper/cliper/theme/default/action/normal.png',
          'elsaclipper/cliper/theme/default/action/rect_normal.png',
          'elsaclipper/cliper/theme/default/action/sep.png',
          'elsaclipper/cliper/theme/default/action/ellipse_normal.png',
          'elsaclipper/cliper/theme/default/action/line_normal.png',
          'elsaclipper/cliper/theme/default/action/finish_hover.png',
          'elsaclipper/cliper/theme/default/action/cancel_normal.png']),
        ('share/pixmaps',
         ['elsaclipper/evernote_adapter/icon/elsaclipper_config.png',
          'elsaclipper/evernote_adapter/icon/elsaclipper_main_icon_error.png',
          'elsaclipper/evernote_adapter/icon/elsaclipper_main_icon.png',
          'elsaclipper/evernote_adapter/icon/elsaclipper_main_icon_upload.png'
         ]),
        ('share/pyshared/elsaclipper/evernote_adapter/',['elsaclipper/evernote_adapter/setting_dialog.glade'])
    ],
    entry_points = {
        'console_scripts': [
            'elsaclipper = elsaclipper:start_ui',
            'elsaclipper-clip = elsaclipper:do_scrot'
        ]
    }
)


