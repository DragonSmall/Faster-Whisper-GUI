# Faster-Whisper-GUI

這是一個基於 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 的圖形化語音轉錄工具。

為了使用上便利，製作了這個整合了圖形介面、OpenCC 自動繁簡轉換、以及模型下載管理工具。

![Language](https://img.shields.io/badge/Language-Python-blue) ![License](https://img.shields.io/badge/License-MIT-green)

## 🖥️ 介面預覽

<p>
  <img src="https://github.com/user-attachments/assets/e29547cf-b425-45b2-8c73-0ca1fdf44dcb" width="600px" alt="軟體介面預覽">
</p>

---

- **圖形操作**：完整的 Tkinter GUI 介面，支援影音檔案拖曳輸入。
- **繁體優化**：內建 OpenCC 轉換引擎，精準將轉錄結果轉換為標準繁體中文。
- **模型管理**：提供獨立的 `Download_Models.bat` 工具，支援 `small` 到 `large-v3` 的各級模型下載，並具備**自動補齊功能**（執行時若缺少模型將自動下載）。
- **硬體加速**：當使用 NVIDIA GPU (CUDA) 加速時，增加判斷若無GPU則切換至CPU。
- **格式輸出**：支援匯出為帶時間軸的 `.srt` 字幕檔或純文字 `.txt` 檔。

---

## 🚀 自行建置環境說明

> **⚠️ 建置環境**：請確保您的電腦已安裝 **Python 3.11**，目前其他版本尚未測試過。

### 🔹 方案一：適合 NVIDIA 顯示卡用戶
若您擁有 NVIDIA 顯卡，執行此步驟可獲得最快的轉錄速度。

```bash
# 1. 複製專案原始碼並進入資料夾
git clone https://github.com/DragonSmall/Faster-Whisper-GUI.git
cd Faster-Whisper-GUI

# 2. 建立並啟動虛擬環境 (資料夾名稱須為 runtime)
python -m venv runtime
runtime\Scripts\activate

# 3. 安裝所有依賴套件 (含 CUDA 加速庫)
pip install -r requirements.txt

# 4. 開始使用
# - 下載模型：執行 Download_Models.bat
# - 啟動程式：執行 Run.bat
```

### 🔹 方案二：適合無顯示卡 (純 CPU) 用戶
如果您使用內顯或純 CPU 進行轉錄，請使用此輕量化安裝方案。

```bash
# 1. 複製專案原始碼並進入資料夾
git clone https://github.com/DragonSmall/Faster-Whisper-GUI.git
cd Faster-Whisper-GUI

# 2. 建立並啟動虛擬環境
python -m venv runtime
runtime\Scripts\activate

# 3. 安裝核心套件 (跳過巨大的 NVIDIA 庫)
pip install faster-whisper av opencc-python-reimplemented tkinterdnd2

# 4. 開始使用
# - 下載模型：執行 Download_Models.bat
# - 啟動程式：執行 Run.bat (進入介面後「設備」請選擇 cpu)
```

---

## 🛠️ 工具說明

| 檔案 | 說明 |
| :--- | :--- |
| `app_gui.py` | 主程式 (GUI 介面與轉錄邏輯) |
| `download_tool.py` | 模型管理工具 (選單式下載與 Token 處理) |
| `Run.bat` | Windows 啟動腳本 |
| `Download_Models.bat` | 模型下載工具啟動檔 |

---

## 🙏 特別感謝
- **核心引擎**: [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- **繁簡轉換**: [OpenCC](https://github.com/BYVoid/OpenCC)
- **GUI擴展**: [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2)

---

> 💡 **提示**：為了確保技術說明的準確性與流暢度，本說明文件部分內容由 **AI 協助生成與優化**。
