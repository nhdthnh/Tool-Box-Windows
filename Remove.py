import subprocess
import sys
import platform
import ctypes
import os
import re

# ====================================================================
# PHẦN HỖ TRỢ HỆ THỐNG (GIỮ NGUYÊN)
# ====================================================================

# (Giữ nguyên các hàm is_admin, run_as_admin, execute_silent_slmgr_command)
def is_admin():
    """Kiểm tra xem tập lệnh có đang chạy với quyền admin không."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """Chạy lại tập lệnh với quyền Administrator trên Windows."""
    if sys.platform != 'win32':
        return False
        
    python_exe = sys.executable
    script = os.path.abspath(sys.argv[0])
    
    args = f'"{script}"'
    ps_command = (
        'Start-Process '
        '-FilePath "' + python_exe + '" '
        '-ArgumentList ' + args + ' '
        '-Verb RunAs'
    )
    
    try:
        subprocess.Popen(
            ['powershell', '-Command', ps_command],
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True
    except Exception as e:
        print(f"Error occurred while trying to restart with Admin rights: {e}")
        return False

def execute_silent_slmgr_command(command_args):
    """Thực thi lệnh slmgr.vbs thông qua cscript ở chế độ silent (/B)."""
    full_command = f"cscript //nologo /B %windir%\\system32\\slmgr.vbs {command_args}"
    
    print(f"\n   -> Execute: slmgr {command_args}")
    
    try:
        result = subprocess.run(
            full_command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8', 
            check=False
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode == 0:
            print("   [RESULT]: Completed.")
            return True
        else:
            print(f"   [ERROR]: Command failed.")
            if output:
                print(f"   Output: {output}")
            if error:
                print(f"   Error: {error}")
            return False

    except Exception as e:
        print(f"   [SYSTEM ERROR]: Cannot execute command: {e}")
        return False
# ====================================================================
# CHỨC NĂNG XÓA KEY OFFICE ĐÃ TỐI ƯU HÓA
# ====================================================================

def remove_windows_key():
    """Xóa key kích hoạt Windows."""
    print("\n--- STARTING WINDOWS KEY REMOVAL ---")
    
    print("1. Remove Product Key (slmgr /upk)...")
    execute_silent_slmgr_command("/upk")
    
    print("2. Remove key cache and Registry (slmgr /cpky)...")
    execute_silent_slmgr_command("/cpky")
    
    print("\n✅ Complete. Windows product key has been removed.")


def remove_office_key_advanced():
    """Quét, kiểm tra trạng thái kích hoạt, và xóa tất cả các key Office."""
    
    print("\n--- STARTING OFFICE KEY REMOVAL ---")
    
    # Danh sách các phiên bản Office (thư mục) cần kiểm tra (Office16, Office15)
    office_versions = ['Office16', 'Office15'] 
    
    ospp_path = None
    
    # 1. TÌM THƯ MỤC CHỨA OSPP.VBS
    print("1. Searching for Office installation folder...")
    for version in office_versions:
        # Kiểm tra x64
        path_x64 = os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files'), 'Microsoft Office', version, 'OSPP.VBS')
        # Kiểm tra x86
        path_x86 = os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)'), 'Microsoft Office', version, 'OSPP.VBS')

        if os.path.exists(path_x64):
            ospp_path = path_x64
            break
        elif os.path.exists(path_x86):
            ospp_path = path_x86
            break

    if not ospp_path:
        print("❌ ERROR: OSPP.VBS file not found. Ensure Office (2013/2016/2019/365) is installed.")
        return

    print(f"   -> Found OSPP.VBS at: {ospp_path}")

    # 2. CHECK ACTIVATION STATUS (/dstatus)
    print("\n2. Checking Office activation status...")
    status_command = f'cscript //nologo "{ospp_path}" /dstatus'
    status_result = subprocess.run(status_command, shell=True, capture_output=True, text=True, encoding='utf-8', check=False)
    
    output_lines = status_result.stdout.splitlines()
    keys_found = []
    
    is_licensed = False
    
    # Quét output để tìm trạng thái cấp phép và các key
    for line in output_lines:
        # Kiểm tra trạng thái cấp phép
        if "LICENSE STATUS" in line:
            if "---LICENSED---" in line or "---GRACE---" in line:
                is_licensed = True
            print(f"   [Status]: {line.strip()}")

        # Lấy các mã 5 ký tự
        match = re.search(r'Last 5 characters of installed product key: (\w{5})', line)
        if match:
            keys_found.append(match.group(1))

    if not is_licensed:
        print("\n✅ Office key has been removed or is not activated. No need to proceed with removal.")
        # input("\nNhấn Enter để kết thúc...")
        sys.exit(1)

    # 3. PROCEED TO REMOVE KEY (ONLY IF ACTIVATED)
    if not keys_found:
        print("\n⚠️ Status is LICENSED but no Product Key ID found. Proceeding to remove common key...")
        key_to_delete = "ALL"
    else:
        print(f"\n3. Found {len(keys_found)} keys to remove: {', '.join(keys_found)}")

    deleted_count = 0
    keys_to_process = keys_found if keys_found else ["ALL"] # Nếu không tìm thấy PID thì thử lệnh ALL
    
    for key_id in keys_to_process:
        print(f"   -> Removing key: {key_id}...")
        
        # Tạo lệnh xóa key (Silent mode /B)
        command_key_id = key_id if key_id != "ALL" else "" # /unpkey: không cần tham số nếu muốn xóa tất cả (ALL)
        unpkey_command = f'cscript //nologo /B "{ospp_path}" /unpkey:{command_key_id}'
        
        unpkey_result = subprocess.run(unpkey_command, shell=True, capture_output=True, text=True, encoding='utf-8', check=False)
        
        if unpkey_result.returncode == 0:
            print(f"      [OK] Removed key {key_id} successfully.")
            deleted_count += 1
        else:
            print(f"      [ERROR] Failed to remove key {key_id}. Output: {unpkey_result.stdout.strip()}")

    # 4. NOTIFICATION AND STATUS CLEANING
    print("\n4. Notification and status cleaning:")
    if deleted_count > 0 or keys_to_process == ["ALL"]:
        print("   -> Re-running /dstatus to check:")
        subprocess.run(status_command, shell=True, capture_output=False, text=True, encoding='utf-8', check=False) # In ra console
        print("\n✅ Office key removal complete. Please **close Word/Excel** and **reopen** to check Unlicensed status.")
    else:
        print("\n⚠️ No keys were removed. Please check the Office installation process.")
    # input("\nNhấn Enter để kết thúc...")
    sys.exit(1)
# ====================================================================
# CHƯƠNG TRÌNH CHÍNH
# ====================================================================

# def main_menu():
#     """Hiển thị menu và xử lý lựa chọn của người dùng."""
    
#     # Kiểm tra Admin và chạy lại nếu cần
#     if platform.system() != "Windows":
#         print("⚠️ This tool only works on Windows operating system.")
#         sys.exit(1)
        
#     if not is_admin():
#         print("⚠️ Administrator privileges are required to run this tool.")
#         if run_as_admin():
#             sys.exit(0)
#         else:
#             # input("Nhấn Enter để thoát...")
#             sys.exit(1)
            
#     # Menu chính (chỉ chạy khi đã có Admin)
#     while True:
#         print("\n=============================================")
#         print("          TOOL REMOVE ACTIVATION KEY (WINDOWS/OFFICE)")
#         print("=============================================")
#         print("1. Xóa Key Windows (slmgr /upk & /cpky)")
#         print("2. Xóa Key Office (Kiểm tra trạng thái -> Quét và xóa)")
#         print("3. Thoát")
        
#         choice = input("Nhập lựa chọn của bạn (1, 2, 3): ")
        
#         if choice == '1':
#             remove_windows_key()
#         elif choice == '2':
#             remove_office_key_advanced()
#         elif choice == '3':
#             print("Đang thoát chương trình. Tạm biệt!")
#             break
#         else:
#             print("Lựa chọn không hợp lệ. Vui lòng nhập 1, 2 hoặc 3.")
            
#     input("\nNhấn Enter để kết thúc...")

# if __name__ == "__main__":
#     main_menu()