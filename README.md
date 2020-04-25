# Pixiv-Downloader
Simple pixiv downloader.

## Notes
-Package dependencies:
https://github.com/azuline/pixiv-api <br />
https://pypi.org/project/PySide2/

Compile using Pyinstaller: <br />
pyinstaller --clean --hidden-import PySide2.QtXml --name pixivdownloader --windowed main.py

## Features
-Single image downloads from url.
-Bulk bookmark downloads (Private or Public) from user Id.