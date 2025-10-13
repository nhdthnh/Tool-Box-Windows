import tkinter as tk
from tkinter import filedialog
import subprocess
import os

# --- Đoạn Code Mới: Tự động yêu cầu quyền Administrator ---
import sys
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    # Nếu không phải Admin, yêu cầu Windows tự nâng quyền
    print("Requesting Administrator privileges...")
    try:
        # Chạy lại script với quyền Admin
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        # Thoát script hiện tại (phiên bản không có quyền Admin)
        sys.exit(0) 
    except Exception as e:
        print(f"Cannot request Administrator privileges: {e}")
        print("Please run this file with the 'Run as administrator' option.")
        sys.exit(1)
# -----------------------------------------------------------

def backup_drivers_cmd():
    """
    Hàm này mở hộp thoại để người dùng chọn thư mục
    và sau đó chạy lệnh DISM để sao lưu driver vào thư mục đó.
    """
    
    # ... (Các bước 1, 2, 3 giữ nguyên như code trước) ...
    
    # 1. Mở hộp thoại chọn thư mục
    root = tk.Tk()
    root.withdraw()
    
    folder_path = filedialog.askdirectory(
        title="Select folder for Driver Backup",
        initialdir="C:/"
    )
    
    if not folder_path:
        print("User canceled or did not select a folder. Backup process aborted.")
        return
    
    # 2. Chuẩn bị lệnh CMD (DISM)
    normalized_path = os.path.normpath(folder_path)
    try:
        if not os.path.exists(normalized_path):
            os.makedirs(normalized_path)
            print(f"Created new directory: {normalized_path}")
    except OSError as e:
        # Handle error if unable to create directory (e.g., due to lack of write permissions)
        print(f"ERROR: Unable to create destination directory '{normalized_path}'. Please check write permissions.")
        print(f"Error details: {e}")
        return
    cmd_command = f'dism /online /Export-Driver /Destination:{normalized_path}'
    
    print(f"Folder Selected: {normalized_path}")
    print(f"Executing Command: {cmd_command}")
    
    # 3. Thực thi lệnh CMD
    try:
        # Lệnh DISM sẽ được chạy thành công vì script đã được nâng quyền ở trên
        full_command = ['cmd.exe', '/c', cmd_command]
        
        result = subprocess.run(
            full_command, 
            capture_output=True, 
            text=True, 
            check=True
        )

        print(f"Success: {result.returncode}")
        print("Output:")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print("\n--- COMMAND EXECUTION ERROR ---")
        print(f"ERROR: Command failed to execute (Return code: {e.returncode}).")
        # Lỗi này có thể xảy ra do DISM thất bại (ví dụ: thiếu driver nào đó)
        print(f"(stderr):\n{e.stderr}")
        
    except Exception as e:
        print(f"\n--- OTHER ERROR ---")
        print(f"Đã xảy ra lỗi không xác định: {e}")

# Chạy hàm chính
if __name__ == "__main__":
    backup_drivers_cmd()