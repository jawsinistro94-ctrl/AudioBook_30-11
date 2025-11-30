@echo off
echo ========================================
echo    AudioBook - Compilador para .exe
echo ========================================
echo.

REM Verificar se PyInstaller está instalado
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando PyInstaller...
    pip install pyinstaller
)

echo Compilando AudioBook...
echo.

pyinstaller --onefile --windowed ^
    --icon=fire_icon.png ^
    --add-data "magma_background.jpg;." ^
    --add-data "power_icon.png;." ^
    --add-data "fire_icon.png;." ^
    --add-data "trophy_icon.png;." ^
    --add-data "sword_icon.png;." ^
    --add-data "location_icon.png;." ^
    --add-data "target_icon.png;." ^
    --add-data "checkbox_on.png;." ^
    --add-data "checkbox_off.png;." ^
    --add-data "mana_icon.png;." ^
    --add-data "sd_icon.png;." ^
    --add-data "sd_rune_icon.png;." ^
    --add-data "explo_rune_icon.png;." ^
    --add-data "uh_rune_icon.png;." ^
    --add-data "settings_icon.png;." ^
    --add-data "auto_icon.png;." ^
    --add-data "tibia_key_icon.png;." ^
    --name "AudioBook" ^
    audiobook.py

echo.
echo ========================================
if exist "dist\AudioBook.exe" (
    echo SUCESSO! AudioBook.exe criado em: dist\
    echo.
    echo Hotkey Global: Alt+F12 para pausar tudo
) else (
    echo ERRO na compilacao. Verifique os erros acima.
)
echo ========================================
pause
