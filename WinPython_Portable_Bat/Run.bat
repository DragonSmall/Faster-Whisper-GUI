@echo off
setlocal
cd /d "%~dp0"
title Faster-Whisper-Portable

:: 1. 設定 Runtime 根目錄
set "BASE_DIR=%~dp0"
set "VENV_DIR=%BASE_DIR%runtime"

:: 2. 自動搜尋 WinPython 的執行檔路徑
:: WinPython 的結構通常是 runtime\python-3.11.x.amd64\python.exe
:: 我們用一個迴圈去抓取 "python-*" 開頭的資料夾
set "FINAL_PY="

if exist "%VENV_DIR%\python.exe" (
    :: 情況 A: 直接在 runtime 根目錄 (Embedded版)
    set "FINAL_PY=%VENV_DIR%\python.exe"
) else (
    :: 情況 B: 搜尋 WinPython 子目錄
    for /d %%D in ("%VENV_DIR%\python-*") do (
        if exist "%%D\python.exe" (
            set "FINAL_PY=%%D\python.exe"
            goto :FOUND_PYTHON
        )
    )
)

:FOUND_PYTHON
if not defined FINAL_PY (
    echo [嚴重錯誤] 找不到 Python 執行檔！
    echo 請確認 runtime 資料夾是否為正確的 WinPython 結構。
    pause
    exit /b
)

:: 3. 設定環境變數 (讓程式跑得更順)
set "HF_HOME=%BASE_DIR%models"
set "PYTHONUTF8=1"
set "HF_HUB_DISABLE_IMPLICIT_TOKEN_WARNING=1"
set "HF_HUB_DISABLE_SYMLINKS_WARNING=1"
set "KMP_DUPLICATE_LIB_OK=TRUE"

echo =======================================================
echo    Faster-Whisper-GUI (Portable)
echo    Python 核心: %FINAL_PY%
echo =======================================================

:: 4. 啟動主程式
"%FINAL_PY%" "%BASE_DIR%app_gui.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [錯誤] 程式異常結束 (代碼: %ERRORLEVEL%)
    pause
)