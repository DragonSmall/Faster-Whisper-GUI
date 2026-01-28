@echo off
setlocal
cd /d "%~dp0"
title Faster-Whisper Model Downloader

:: ========================================================
:: 1. 設定 Runtime 根目錄與基礎路徑
:: ========================================================
set "BASE_DIR=%~dp0"
set "VENV_DIR=%BASE_DIR%runtime"

:: 設定模型下載存放路徑
set "HF_HOME=%BASE_DIR%models"
set "XDG_CACHE_HOME=%BASE_DIR%models"

:: ========================================================
:: 2. 自動搜尋 WinPython 的執行檔路徑 (智慧偵測)
:: ========================================================
set "FINAL_PY="

if exist "%VENV_DIR%\python.exe" (
    :: 情況 A: 直接在 runtime 根目錄 (Embedded版)
    set "FINAL_PY=%VENV_DIR%\python.exe"
) else (
    :: 情況 B: 搜尋 WinPython 子目錄 (例如 python-3.11.9.amd64)
    for /d %%D in ("%VENV_DIR%\python-*") do (
        if exist "%%D\python.exe" (
            set "FINAL_PY=%%D\python.exe"
            goto :FOUND_PYTHON
        )
    )
)

:FOUND_PYTHON
if not defined FINAL_PY (
    echo.
    echo [嚴重錯誤] 找不到 Python 環境！
    echo 請確認 runtime 資料夾是否為正確的 WinPython 結構。
    echo 預期路徑範例: runtime\python-3.11.x.amd64\python.exe
    pause
    exit /b
)

:: ========================================================
:: 3. 設定環境變數 (優化下載體驗)
:: ========================================================
:: 讓 Token 警告閉嘴
set "HF_HUB_DISABLE_IMPLICIT_TOKEN_WARNING=1"
:: 關閉 Symlinks 警告
set "HF_HUB_DISABLE_SYMLINKS_WARNING=1"
:: 強制顯示進度條
set "PYTHONUNBUFFERED=1"
:: 解決 Intel MKL 錯誤
set "KMP_DUPLICATE_LIB_OK=TRUE"
:: 確保允許連網
set "HF_HUB_OFFLINE=0"

echo =======================================================
echo    Faster-Whisper 模型下載工具
echo    使用核心: %FINAL_PY%
echo    模型存放: %HF_HOME%
echo =======================================================

:: 4. 啟動下載工具
"%FINAL_PY%" "%BASE_DIR%download_tool.py"

:: 5. 錯誤攔截
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [錯誤] 下載工具發生異常 (代碼: %ERRORLEVEL%)
)

echo.
echo 按任意鍵關閉視窗...
pause
endlocal