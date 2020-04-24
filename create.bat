::Changes current working directory to the location of the bat file.
cd "%~dp0"

if exist build (
rmdir "build" /S /Q
)

if exist dist (
rmdir "dist" /S /Q
)

::Changes the current working directory to the src file.
cd "%~dp0src"

pyinstaller --clean --hidden-import PySide2.QtXml --distpath ../dist --workpath ../build --noconfirm --specpath ../build/spec --name pixivdownloader --windowed main.py

cd "%~dp0"

rmdir "build" /S /Q
rmdir "%~dp0src\__pycache__" /S /Q

copy "%cd%\src\*.ui" "%~dp0dist/pixivdownloader" /Y