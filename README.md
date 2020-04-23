# Pixiv-Downloader
Simple pixiv downloader.

## Notes
-Requires:  
https://github.com/azuline/pixiv-api <br />
https://pypi.org/project/PySide2/

Inorder to compact using Pyinstaller: <br />
pyinstaller --windowed --hidden-import PySide2.QtXml --onefile main.py

## Features
-Downloads single images from image Id. <br />
-Downloads either all, or a range, of bookmarks from user Id. <br />
