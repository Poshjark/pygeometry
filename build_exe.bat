if exist "dist" (
	cd dist
	Y || del /S *.exe
	cd ..
	) ELSE (
	echo dist missing)
rd /S /q build 
pyinstaller.exe --onefile --windowed --name=HPGLgenerator --icon=Rectangle.ico main.py
Y || del *.spec
rd /S /q build 

