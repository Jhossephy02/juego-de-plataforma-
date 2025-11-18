@echo off
echo ================================================
echo   INSTALADOR DE LIBRERIAS DE AUDIO MEJORADAS
echo ================================================
echo.
echo Este script instalara las librerias necesarias
echo para el analisis musical avanzado con Librosa.
echo.
echo NOTA: En Windows, puede que necesites instalar
echo Microsoft Visual C++ 14.0 o superior.
echo.
pause

echo.
echo [1/4] Actualizando pip...
python -m pip install --upgrade pip

echo.
echo [2/4] Instalando NumPy y SciPy...
pip install numpy>=1.24.0 scipy>=1.10.0

echo.
echo [3/4] Instalando Librosa y dependencias...
pip install librosa>=0.10.0 soundfile>=0.12.0 audioread>=3.0.0

echo.
echo [4/4] Instalando Pygame...
pip install pygame>=2.5.0

echo.
echo ================================================
echo   INSTALACION COMPLETADA
echo ================================================
echo.
echo Ahora puedes ejecutar el juego con:
echo     python -m src.main
echo.
echo O simplemente:
echo     run_game.bat
echo.
pause