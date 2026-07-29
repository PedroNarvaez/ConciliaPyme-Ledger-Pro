@echo off
echo Instalando dependencias y generando ejecutable con PyInstaller...
pip install pyinstaller
pyinstaller --clean ConciliaPymeLedgerPro.spec
echo Construccion finalizada. El ejecutable se encuentra en: dist\ConciliaPymeLedgerPro.exe
pause
