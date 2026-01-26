import os
import sys

# 1. 基礎環境設定
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["PYTHONUNBUFFERED"] = "1"

# 2. 匯入下載模組
try:
    from faster_whisper import download_model
except ImportError:
    print("[錯誤] 找不到 faster_whisper 套件，請確認環境是否安裝完整。")
    input("請按任意鍵退出...")
    sys.exit(1)

def get_clean_path(full_path):
    """
    將含有 snapshots/hash 的長路徑切短，只顯示到模型主目錄
    """
    try:
        parent = os.path.dirname(full_path) # snapshots
        grandparent = os.path.dirname(parent) # model-folder
        return grandparent + "\\"
    except:
        return full_path

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base_dir, "models")
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=======================================================")
    print("   Faster-Whisper 模型下載工具")
    print("=======================================================")
    
    print("若您有 HuggingFace Token，可在此輸入以消除警告並提升速度。")
    token = input("請輸入 Token (若無請直接按 Enter 跳過): ").strip()
    
    if token:
        os.environ["HF_TOKEN"] = token
        print("[System] ✅ 已設定 Token！")
    else:
        print("[System] 未輸入 Token，將以訪客身份下載 (可能會出現黃字警告，請忽略)。")
    
    print("-" * 55)

    all_models = {
        "1": "small",
        "2": "medium",
        "3": "large-v2",
        "4": "large-v3"
    }
    
    while True:
        print("\n請選擇要下載的模型：")
        print("1. small     (輕量，速度快)")
        print("2. medium    (推薦，平衡點)")
        print("3. large-v2  (精準，舊版高階)")
        print("4. large-v3  (最強，最新版)")
        print("-" * 30)
        print("5. 下載全部  (批次下載 1~4)")
        print("Q. 離開")
        print("=======================================================")
        
        choice = input("請輸入選項: ").strip().lower()
        
        if choice == 'q':
            break
            
        if choice == '5':
            print("\n[System] 🚀 開始批次下載所有模型...")
            for key, model_name in all_models.items():
                print(f"\n>>> [{key}/4] 正在檢查/下載: {model_name}")
                try:
                    # 這裡修改了提示文字
                    print("[System] 下載中請耐心等待...\n")
                    path = download_model(model_name, cache_dir=models_dir)
                    clean_path = get_clean_path(path)
                    print(f"✅ {model_name} 準備就緒！")
                    print(f"位置: {clean_path}")
                except Exception as e:
                    print(f"❌ {model_name} 下載失敗: {e}")
            
            print("\n🎉 全部處理完畢！")
            input("按 Enter 鍵返回主選單...")
            
        else:
            model_name = all_models.get(choice)
            
            if model_name:
                print(f"\n[System] 準備下載/檢查模型: {model_name}")
                
                # 這裡修改了提示文字
                print("[System] 下載中請耐心等待...\n")
                
                try:
                    path = download_model(model_name, cache_dir=models_dir)
                    clean_path = get_clean_path(path)
                    
                    print(f"\n✅ 下載/檢查完成！")
                    print(f"模型位置: {clean_path}")
                except Exception as e:
                    print(f"\n❌ 下載失敗: {e}")
                
                input("\n按 Enter 鍵返回主選單...")
            else:
                pass

if __name__ == "__main__":
    main()