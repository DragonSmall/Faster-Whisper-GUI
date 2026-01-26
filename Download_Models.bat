@echo off
setlocal
title Faster-Whisper Model Downloader

:: 1. 設定基礎目錄
set "BASE_DIR=%~dp0"
if "%BASE_DIR:~-1%"=="\" set "BASE_DIR=%BASE_DIR:~0,-1%"

:: 2. 設定模型路徑
set "HF_HOME=%BASE_DIR%\models"
set "XDG_CACHE_HOME=%BASE_DIR%\models"

:: ========================================================
:: 【關鍵修正區】 在這裡設定所有環境變數 (最優先生效)
:: ========================================================
:: (A) 讓 Token 警告閉嘴
set "HF_HUB_DISABLE_IMPLICIT_TOKEN_WARNING=1"

:: (B) 讓 Symlinks 警告閉嘴
set "HF_HUB_DISABLE_SYMLINKS_WARNING=1"

:: (C) 強制 Python 即時顯示輸出 (解決進度條不見的問題)
set "PYTHONUNBUFFERED=1"

:: (D) 解決 Intel MKL 錯誤
set "KMP_DUPLICATE_LIB_OK=TRUE"

:: (E) 確保允許連網
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

echo 正在啟動下載工具...
"%FINAL_PY%" "%BASE_DIR%\download_tool.py"

endlocal