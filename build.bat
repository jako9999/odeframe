@echo off
setlocal EnableExtensions

set "ROOT=%~dp0"
cd /d "%ROOT%"

set "BUNDLE_TESSERACT=0"
if not defined TESSDATA_LANGS (
    set "TESSDATA_LANGS=eng"
)

echo [INFO] Tesseract will NOT be bundled.
echo [INFO] Runtime requires a system-installed Tesseract-OCR.
echo [INFO] Refer to README.md for install guidance.
echo [INFO] Bundling tessdata languages: %TESSDATA_LANGS%

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=py -3"
) else (
    set "PYTHON_CMD=python"
)

echo [INFO] Installing build dependencies...
call %PYTHON_CMD% -m pip install --upgrade pip
if errorlevel 1 goto fail
call %PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 goto fail

echo [INFO] Cleaning previous build output...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo [INFO] Building onefile executable...
call %PYTHON_CMD% -m PyInstaller --noconfirm odeframe.spec
if errorlevel 1 goto fail

echo [DONE] Build complete.
echo [DONE] Output: "%ROOT%dist\OdeFrame.exe"
goto end

:fail
echo [ERROR] Build failed.
exit /b 1

:end
endlocal
