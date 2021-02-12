cd dist
Y || del /S *.exe
cd ..
rd /S /q build 
pyinstaller.exe --onefile --windowed --icon=Rectangle.ico rectangle.py
Y || del *.spec
rd /S /q build 

