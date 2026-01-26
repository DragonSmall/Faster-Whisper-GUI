@echo off
setlocal
title Faster-Whisper-Portable

:: 1. 設定基礎目錄
set "BASE_DIR=%~dp0"
if "%BASE_DIR:~-1%"=="\" set "BASE_DIR=%BASE_DIR:~0,-1%"

:: 2. 設定模型路徑
set "HF_HOME=%BASE_DIR%\models"
set "XDG_CACHE_HOME=%BASE_DIR%\models"
set "PYTHONUTF8=1"

:: ========================================================
:: 【環境變數區】 停用警告，保持介面乾淨
:: ========================================================
set "HF_HUB_DISABLE_SYMLINKS_WARNING=1"
set "HF_HUB_DISABLE_IMPLICIT_TOKEN_WARNING=1"
set "KMP_DUPLICATE_LIB_OK=TRUE"
set "PYTHONUNBUFFERED=1"
set "HF_HUB_OFFLINE=0"
:: ========================================================

:: 3. 定義 Runtime 目錄
set "VENV_DIR=%BASE_DIR%\runtime"

:: 4. 尋找 Python
if exist "%VENV_DIR%\Scripts\python.exe" (
    set "FINAL_PY=%VENV_DIR%\Scripts\python.exe"
) else (
    if exist "%VENV_DIR%\python.exe" (
        set "FINAL_PY=%VENV_DIR%\python.exe"
    ) else (
        echo [錯誤] 找不到 Python 環境。
        pause
        exit
    )
)

:: 5. 設定路徑 (NVIDIA 加速)
set "PATH=%VENV_DIR%\Scripts;%VENV_DIR%;%VENV_DIR%\Lib\site-packages\nvidia\cuda_runtime\bin;%VENV_DIR%\Lib\site-packages\nvidia\cudnn\bin;%VENV_DIR%\Lib\site-packages\nvidia\cublas\bin;%PATH%"

echo =======================================================
echo    Faster-Whisper-Portable
echo    正在啟動主程式...(請勿關閉此視窗)
echo.
echo    提示: 若需下載其他模型，請執行 Download_Models.bat
echo =======================================================

:: 6. 啟動 GUI
"%FINAL_PY%" "%BASE_DIR%\app_gui.py"

endlocal
exit