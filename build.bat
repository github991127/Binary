@echo off
chcp 65001 >nul
setlocal

echo [1/3] Cleaning old builds...
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

echo [2/3] Building onedir package...
python -m PyInstaller source\Binary_webview.spec
if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

echo [3/3] Build complete: dist\Binary_webview\Binary_webview.exe
pause
endlocal
