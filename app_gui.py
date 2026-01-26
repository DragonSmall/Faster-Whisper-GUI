import os
import threading
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext, messagebox
import opencc
from faster_whisper import WhisperModel
import logging
from datetime import datetime
import glob
import gc
import json
import ctypes

# --- 1. 拖曳功能載入 ---
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False

# 防止 Intel MKL 庫重複載入衝突
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def get_system_default_device():
    """ 偵測系統是否有可用的 NVIDIA GPU (由 ctranslate2 判斷) """
    try:
        import ctranslate2
        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda"
    except:
        pass
    return "cpu"

class WhisperApp:
    def __init__(self, root):
        self.root = root
        
        # --- 核心路徑偵測 ---
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_dir = os.path.join(self.base_dir, "logs")
        self.config_path = os.path.join(self.base_dir, "config.json")
        self.default_out_dir = os.path.join(self.base_dir, "Out")
        
        self._init_folders()
        self._setup_logging()
        self.safe_log(f"--- 程式啟動 (目錄: {self.base_dir}) ---")
        
        self.root.title("Faster-Whisper 語音轉錄工具")
        self.root.geometry("850x820")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # --- 核心變數 ---
        self.stop_event = threading.Event()
        self.is_running = False
        self.file_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        
        self.model_size = tk.StringVar()
        self.device = tk.StringVar()
        self.compute_type = tk.StringVar()
        self.trans_mode = tk.StringVar()
        self.enable_vad = tk.BooleanVar()
        self.output_format = tk.StringVar()
        
        self.cc_s2t = opencc.OpenCC('s2t')
        self.cc_t2s = opencc.OpenCC('t2s')
        
        # 先建立介面，再載入設定
        self._create_widgets()
        self.load_config()

    def _init_folders(self):
        os.makedirs(self.log_dir, exist_ok=True)
        os.makedirs(self.default_out_dir, exist_ok=True)
        log_files = sorted(glob.glob(os.path.join(self.log_dir, "*.log")), key=os.path.getmtime)
        while len(log_files) >= 5:
            try: os.remove(log_files.pop(0))
            except: break

    def _setup_logging(self):
        log_filename = datetime.now().strftime("whisper_%Y%m%d_%H%M%S.log")
        log_path = os.path.join(self.log_dir, log_filename)
        self.logger = logging.getLogger("WhisperApp")
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(log_path, encoding='utf-8')
        fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(fh)

    def load_config(self):
        """ 載入設定 """
        default_dev = get_system_default_device()
        default_compute = "float16" if default_dev == "cuda" else "int8"
        
        defaults = {
            "model_size": "large-v2", "device": default_dev, "compute_type": default_compute,
            "trans_mode": "繁體中文 (若偵測為中文則轉碼)", "enable_vad": False,
            "output_format": "srt", "output_dir": self.default_out_dir
        }
        
        config = defaults
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    saved_path = saved_config.get("output_dir", "")
                    if not saved_path or not os.path.exists(os.path.dirname(saved_path)):
                        self.safe_log("⚠️ 偵測到原始存檔路徑失效，已重設為目前 Out 目錄。")
                        saved_config["output_dir"] = self.default_out_dir
                    config.update(saved_config)
            except: pass
            
        self.model_size.set(config.get("model_size"))
        self.device.set(config.get("device"))
        self.compute_type.set(config.get("compute_type"))
        self.trans_mode.set(config.get("trans_mode"))
        self.enable_vad.set(config.get("enable_vad"))
        self.output_format.set(config.get("output_format"))
        self.output_dir.set(config.get("output_dir"))
        
        # 載入後手動觸發一次 UI 更新
        self.update_compute_options()

    def save_config(self):
        config = {
            "model_size": self.model_size.get(), "device": self.device.get(),
            "compute_type": self.compute_type.get(), "trans_mode": self.trans_mode.get(),
            "enable_vad": self.enable_vad.get(), "output_format": self.output_format.get(),
            "output_dir": self.output_dir.get()
        }
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except: pass

    def safe_log(self, message, level="info"):
        if self.root.winfo_exists():
            self.root.after(0, lambda: self._update_log(message))
        if level == "error": self.logger.error(message)
        elif level == "debug": self.logger.debug(message)
        else: self.logger.info(message)

    def _update_log(self, message):
        try:
            self.log_area.configure(state='normal')
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
            self.log_area.configure(state='disabled')
        except: pass

    def update_compute_options(self, event=None):
        """ 當設備切換時，自動過濾精度選項 """
        if self.device.get() == "cpu":
            # CPU 只允許 int8
            self.cb_compute.config(values=["int8"])
            self.compute_type.set("int8")
        else:
            # CUDA 顯示全部
            self.cb_compute.config(values=["float16", "int8", "int8_float16"])
            # 如果目前是從 CPU 切換回 CUDA，給予一個預設值
            if self.compute_type.get() not in ["float16", "int8", "int8_float16"]:
                self.compute_type.set("float16")

    def _create_widgets(self):
        # 1. 檔案區
        frame_file = tk.LabelFrame(self.root, text="1. 影音來源", padx=10, pady=10)
        frame_file.pack(fill="x", padx=10, pady=5)
        entry_file = tk.Entry(frame_file, textvariable=self.file_path)
        entry_file.pack(side="left", padx=5, fill="x", expand=True)
        if DND_AVAILABLE:
            entry_file.drop_target_register(DND_FILES)
            entry_file.dnd_bind('<<Drop>>', lambda e: self.drop_handler(e, self.file_path))
        tk.Button(frame_file, text="瀏覽檔案", command=lambda: self.browse_file(self.file_path, "media")).pack(side="left")

        # 2. 參數設定區
        frame_settings = tk.LabelFrame(self.root, text="2. 參數設定", padx=10, pady=10)
        frame_settings.pack(fill="x", padx=10, pady=5)
        
        f_row1 = tk.Frame(frame_settings)
        f_row1.pack(fill="x", pady=2)
        tk.Label(f_row1, text="輸出目錄:").pack(side="left")
        entry_out = tk.Entry(f_row1, textvariable=self.output_dir)
        entry_out.pack(side="left", padx=5, fill="x", expand=True)
        tk.Button(f_row1, text="瀏覽...", command=self.browse_output_folder).pack(side="left")
        tk.Button(f_row1, text="📂 開啟資料夾", command=self.open_output_folder).pack(side="left", padx=5)

        f_row2 = tk.Frame(frame_settings)
        f_row2.pack(fill="x", pady=5)
        tk.Label(f_row2, text="語言模式:").pack(side="left")
        ttk.Combobox(f_row2, textvariable=self.trans_mode, values=["繁體中文 (若偵測為中文則轉碼)", "簡體中文 (若偵測為中文則轉碼)", "原始原文 (自動偵測)"], width=28, state="readonly").pack(side="left", padx=5)
        
        tk.Label(f_row2, text="設備:").pack(side="left", padx=(10, 0))
        # 綁定事件：當設備選中時觸發精度更新
        self.cb_device = ttk.Combobox(f_row2, textvariable=self.device, values=["cuda", "cpu"], width=8, state="readonly")
        self.cb_device.pack(side="left", padx=5)
        self.cb_device.bind("<<ComboboxSelected>>", self.update_compute_options)
        
        tk.Label(f_row2, text="精度:").pack(side="left", padx=(10, 0))
        self.cb_compute = ttk.Combobox(f_row2, textvariable=self.compute_type, values=["float16", "int8", "int8_float16"], width=12, state="readonly")
        self.cb_compute.pack(side="left", padx=5)

        f_row3 = tk.Frame(frame_settings)
        f_row3.pack(fill="x", pady=2)
        tk.Label(f_row3, text="模型:").pack(side="left")
        ttk.Combobox(f_row3, textvariable=self.model_size, values=["small", "medium", "large-v2", "large-v3"], width=8).pack(side="left", padx=5)
        tk.Label(f_row3, text="格式:").pack(side="left", padx=(10, 0))
        ttk.Combobox(f_row3, textvariable=self.output_format, values=["srt", "txt"], width=5, state="readonly").pack(side="left", padx=(5, 15))
        
        tk.Checkbutton(f_row3, text="VAD過濾 (音樂請勿勾選)", variable=self.enable_vad).pack(side="left")
        tk.Button(f_row3, text="↺ 恢復預設", command=self.reset_to_defaults, fg="#666", bd=1).pack(side="left", padx=(20, 0))

        # 3. 按鈕區
        frame_btns = tk.Frame(self.root)
        frame_btns.pack(fill="x", padx=10, pady=10)
        self.btn_run = tk.Button(frame_btns, text="開始執行 (Start)", command=self.start_thread, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), height=2)
        self.btn_run.pack(side="left", expand=True, fill="x", padx=(0, 5))
        self.btn_stop = tk.Button(frame_btns, text="中斷 (Stop)", command=self.stop_process, font=("Arial", 12, "bold"), height=2, width=15, state="disabled")
        self.btn_stop.pack(side="right", fill="x", padx=(5, 0))

        # 4. 紀錄區
        frame_log = tk.LabelFrame(self.root, text="執行紀錄", padx=10, pady=10)
        frame_log.pack(fill="both", expand=True, padx=10, pady=5)
        self.log_area = scrolledtext.ScrolledText(frame_log, state='disabled', height=12)
        self.log_area.pack(fill="both", expand=True)

    def open_output_folder(self):
        path = self.output_dir.get()
        if os.path.exists(path): os.startfile(path)
        else: messagebox.showwarning("警告", "輸出目錄不存在！")

    def reset_to_defaults(self):
        dev = get_system_default_device()
        self.device.set(dev)
        self.output_dir.set(self.default_out_dir)
        self.update_compute_options() # 重設時也要觸發
        self.safe_log(f"💡 已恢復預設 (設備: {dev})")

    def _on_finish(self, success, result_path):
        self.is_running = False
        self.btn_run.config(state="normal", text="開始執行 (Start)")
        self.btn_stop.config(state="disabled", bg="SystemButtonFace", fg="black")
        gc.collect()
        if success:
            self.safe_log("-" * 30 + f"\n✅ 完成！存於: {result_path}\n" + "-" * 30)
        else:
            self.safe_log("\n❌ 任務結束")

    def on_close(self):
        self.save_config()
        if self.is_running:
            if messagebox.askokcancel("退出", "轉錄中，確定要退出嗎？"):
                self.stop_event.set()
                self.root.destroy()
        else:
            self.root.destroy()

    def drop_handler(self, event, var):
        path = event.data
        if path.startswith('{') and path.endswith('}'): path = path[1:-1]
        var.set(path)

    def browse_file(self, var, type_):
        ft = [("影音檔", "*.mp4 *.mp3 *.wav *.mkv *.m4a *.flac"), ("所有檔案", "*.*")]
        f = filedialog.askopenfilename(filetypes=ft)
        if f: var.set(f)
            
    def browse_output_folder(self):
        f = filedialog.askdirectory()
        if f: self.output_dir.set(f)

    def stop_process(self):
        if not self.stop_event.is_set():
            self.stop_event.set()
            self.safe_log("\n⚠️ 正在請求中斷...")
            self.btn_stop.config(text="停止中...", state="disabled")

    def start_thread(self):
        if not self.file_path.get():
            messagebox.showwarning("警告", "請先選擇影音檔案！")
            return
        self.stop_event.clear()
        self.is_running = True
        self.btn_run.config(state="disabled", text="運算中...")
        self.btn_stop.config(state="normal", text="中斷 (Stop)", bg="#F44336", fg="white") 
        self.log_area.configure(state='normal')
        self.log_area.delete(1.0, tk.END)
        self.log_area.configure(state='disabled')
        threading.Thread(target=self.run_transcription, daemon=True).start()

    def format_timestamp(self, seconds):
        td = float(seconds)
        hours, rem = divmod(td, 3600)
        minutes, seconds = divmod(rem, 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{milliseconds:03d}"

    def run_transcription(self):
        model = None
        try:
            f_path = self.file_path.get()
            file_ext = self.output_format.get()
            m_size = self.model_size.get()
            dev = self.device.get()
            c_type = self.compute_type.get()
            mode = self.trans_mode.get()
            use_vad = self.enable_vad.get()

            # --- 安全性檢查：選CPU時強制切到int8 ---
            if dev == "cpu" and c_type != "int8":
                self.safe_log("⚠️ CPU 模式下強制使用 int8 精度運算。", level="warning")
                c_type = "int8"
                self.root.after(0, lambda: self.compute_type.set("int8"))

            raw_fname = os.path.splitext(os.path.basename(f_path))[0]
            for char in '<>:"/\\|?*': raw_fname = raw_fname.replace(char, "_")
            final_out_dir = self.output_dir.get()
            os.makedirs(final_out_dir, exist_ok=True)
            out_path = os.path.join(final_out_dir, raw_fname + f".{file_ext}")

            self.safe_log(f"--- 啟動引擎 ({m_size}) ---")
            
            try:
                model = WhisperModel(m_size, device=dev, compute_type=c_type, local_files_only=False)
            except Exception as e:
                err_str = str(e)
                if dev == "cuda" and ("CUDA" in err_str or "insufficient" in err_str):
                    self.safe_log("⚠️ 顯卡驅動不足，自動降級切換至 CPU 模式...", level="warning")
                    model = WhisperModel(m_size, device="cpu", compute_type="int8")
                    self.root.after(0, lambda: (self.device.set("cpu"), self.compute_type.set("int8"), self.update_compute_options()))
                else: raise e
            
            segments_generator, info = model.transcribe(
                f_path, beam_size=5, vad_filter=use_vad, task="transcribe",
                condition_on_previous_text=True, temperature=0
            )
            
            detected_lang = info.language
            self.safe_log(f"偵測語言: {detected_lang} | 總時長: {info.duration:.2f}s")
            
            do_convert = "s2t" if detected_lang == "zh" and "繁體中文" in mode else ("t2s" if detected_lang == "zh" and "簡體中文" in mode else None)
            
            with open(out_path, "w", encoding="utf-8") as f:
                seg_count = 0
                for segment in segments_generator:
                    if self.stop_event.is_set(): break
                    start, end, text = self.format_timestamp(segment.start), self.format_timestamp(segment.end), segment.text.strip()
                    if do_convert == "s2t": text = self.cc_s2t.convert(text)
                    elif do_convert == "t2s": text = self.cc_t2s.convert(text)
                    self.safe_log(f"[{start}] {text}", level="debug")
                    seg_count += 1
                    if file_ext == "srt": f.write(f"{seg_count}\n{start} --> {end}\n{text}\n\n")
                    else: f.write(f"{text}\n")

            del model
            gc.collect()
            self.root.after(0, lambda: self._on_finish(not self.stop_event.is_set(), out_path if not self.stop_event.is_set() else ""))
        except Exception as e:
            if model: del model
            gc.collect()
            self.safe_log(f"發生異常: {str(e)}", level="error")
            self.root.after(0, lambda: self._on_finish(False, ""))

if __name__ == "__main__":
    try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
    except: root = tk.Tk()
    app = WhisperApp(root)
    root.mainloop()