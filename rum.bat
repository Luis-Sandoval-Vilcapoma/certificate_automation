@echo off
cd /d "%~dp0"

echo Activando entorno virtual...
call env\Scripts\activate

echo Ejecutando script...
python main.py

echo.
echo ===============================
echo PROCESO FINALIZADO
echo ===============================
pause
