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

:: 4. 自動偵測 Python 位置 (WinPython 特化版)
set "FINAL_PY="
:: 先找根目錄 (相容性)
if exist "%VENV_DIR%\python.exe" (
    set "FINAL_PY=%VENV_DIR%\python.exe"
) else (
    :: 再找 WinPython 子目錄 (例如 python-3.11.x.amd64)
    for /d %%D in ("%VENV_DIR%\python-*") do (
        if exist "%%D\python.exe" (
            set "FINAL_PY=%%D\python.exe"
            goto :FOUND_PYTHON
        )
    )
)

:FOUND_PYTHON
if not defined FINAL_PY (
    echo [錯誤] 找不到 Python 環境。
    echo 請確認 runtime 資料夾是否為 WinPython 結構。
    pause
    exit
)

:: 取得 Python 所在的資料夾路徑 (例如 runtime\python-3.11...)
for %%F in ("%FINAL_PY%") do set "PY_ROOT=%%~dpF"

:: 5. 設定路徑 (NVIDIA 加速 - 動態對應 WinPython 結構)
set "PATH=%PY_ROOT%Scripts;%PY_ROOT%;%PY_ROOT%Lib\site-packages\nvidia\cuda_runtime\bin;%PY_ROOT%Lib\site-packages\nvidia\cudnn\bin;%PY_ROOT%Lib\site-packages\nvidia\cublas\bin;%PATH%"

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
