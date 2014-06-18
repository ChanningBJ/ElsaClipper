Evercliper
==========

A linux evernote client focus on taking a screenshot, make some marks and saved to evernote.

# Supported OS
This application is developped on Ubuntu 12.04 and tested on Ubuntu 14.04. Other Ubuntu version should be ok.

# Installation

## Install using DEB package
1. Install evernote python API using pip
> sudo pip install evernote

2. Install python-elsaclipper deb package
> sudo dpkg -i python-elsaclipper

After that, you can start the application from Unity dash or start from command line:
> $ elsaclipper


## Start from source

If you don't like deb package, you can also start this application from source code.´

1. Install evernote python API using pip
> sudo pip install evernote
2. Install depended deb packages
> sudo apt-get install gir1.2-keybinder-3.0 python-xlib python-pyinotify python-keyring
3. start `__init__.py` under ElsaClipper/elsaclipper
> python ElsaClipper/elsaclipper/\_\_init\_\_.py ui

# Key binding
ElsaClipper has the feature of binding a keyboard shortcut to taking snapshot of your screen, but this feature is limited by gir1.2-keybinder-3.0, which can only bind shortcuts start with ctrl or alt. If you want to bind other keys, just bind any shortcut to command `elsaclipper-clip` in your system configuration.

# Credits
The screenshot taking feature is from deepin-scrot (https://github.com/linuxdeepin-packages/deepin-scrot)
