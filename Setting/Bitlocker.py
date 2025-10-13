import platform 
import subprocess ,os,re
def run_diskpart_and_extract_ltr():
    """
    Chạy lệnh diskpart, gửi lệnh 'list volume', và phân tích output 
    để trích xuất các ký tự ổ đĩa (Ltr) thành một mảng.
    Chỉ chạy trên Windows.
    
    Returns:
        list: Danh sách các ký tự ổ đĩa (VD: ['D', 'C']). Trả về list rỗng nếu lỗi.
    """
    # Kiểm tra hệ điều hành trước khi chạy lệnh Windows
    if platform.system().lower() != "windows":
        return []

    drive_letters = []
    
    try:
        # 1. Định nghĩa lệnh và dữ liệu input
        diskpart_command = 'diskpart'
        # Gửi lệnh 'list volume' và 'exit' để đóng diskpart sau khi hoàn thành
        diskpart_input = "list volume\nexit\n"
        
        
        proc = subprocess.run(
            diskpart_command,
            shell=True, 
            input=diskpart_input,
            capture_output=True,
            text=True,
            encoding='cp850', # Encoding cho output từ CMD (quan trọng để đọc ký tự tiếng Việt/đặc biệt)
            check=True,
            timeout=10
        )
        
        # 3. Phân tích kết quả và trích xuất Ltr
        raw_output = proc.stdout
        lines = raw_output.splitlines()
    
        # Tìm header và vị trí cột "Ltr"
        header_idx = None
        start_line = 0
        for i, line in enumerate(lines):
            if 'Ltr' in line and 'Volume' in line:
                header_idx = line.find('Ltr')
                start_line = i + 1
                break

        # Nếu tìm thấy header, bỏ qua dòng phân cách (---) và bắt đầu đọc dữ liệu
        if header_idx is not None:
            for line in lines[start_line:]:
                # bỏ qua dòng phân cách hoặc rỗng
                if not line.strip() or set(line.strip()) <= set('-'):
                    continue

                # Lấy phần nằm tại vị trí cột Ltr (dùng slice để tránh IndexError)
                segment = line[header_idx:header_idx+3] if header_idx < len(line) else ''
                ltr = segment.strip()

                # Nếu phần trích ra là một chữ cái đơn, coi đó là drive letter
                if len(ltr) == 1 and ltr.isalpha():
                    drive_letters.append(ltr)
                else:
                    # fallback: tìm token đơn ký tự trong dòng (thêm an toàn)
                    parts = line.split()
                    for tok in parts:
                        if len(tok) == 1 and tok.isalpha():
                            drive_letters.append(tok)
                            break
        else:
            # Nếu không tìm header, thử phương pháp token-based toàn cục
            for line in lines:
                parts = line.split()
                for tok in parts:
                    if len(tok) == 1 and tok.isalpha():
                        drive_letters.append(tok)
                        break

    except Exception as e:
        # Nếu diskpart không chạy, hoặc timeout
        print(f"[ERROR] Unable to run diskpart command or parsing error: {e!r}")
        
    return drive_letters

def check_bitlocker_status(drive_letters):
    """
    Thực thi lệnh 'manage-bde -status <drive>:' và phân tích kết quả 
    để lấy trạng thái BitLocker.
    
    Args:
        drive_letters (list): Danh sách các ký tự ổ đĩa cần kiểm tra (ví dụ: ['C', 'D']).
    """
    
    results = {}
    
    # Đảm bảo lệnh 'manage-bde' có sẵn (chỉ chạy trên Windows)
    if os.name != 'nt':
        print("The 'manage-bde' command is only available on Windows operating systems.")
        return
    for letter in drive_letters:
        drive = f"{letter}:"
        command = ['manage-bde', '-status', drive]
        
        print(f"\nVolume {drive}:")
        
        try:
            # Sử dụng subprocess.run để thực thi lệnh và bắt output
            # capture_output=True: lưu trữ stdout và stderr
            # text=True: chuyển output sang chuỗi (string)
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                check=False, # Không raise exception nếu lệnh thất bại (ví dụ: ổ đĩa không tồn tại)
                creationflags=subprocess.CREATE_NO_WINDOW # Không hiện cửa sổ console
            )
            
            output = result.stdout
            
            # --- Phân tích Output ---
            
            # 1. Tìm tên Volume (DATA)
            conversion_status = re.search(r'Conversion Status:\s+(.*)', output)
            conversion_status = conversion_status.group(1).strip() if conversion_status else "Error"
            
            # 2. Trích xuất trạng thái bảo vệ (Protection Status)
            protection_match = re.search(r'Protection Status:\s+(.*)', output)
            protection_status = protection_match.group(1).strip() if protection_match else "Error"

            # 3. Trích xuất phiên bản BitLocker (BitLocker Version)
            version_match = re.search(r'BitLocker Version:\s+(.*)', output)
            bitlocker_version = version_match.group(1).strip() if version_match else "N/A"
            
            # 4. Trích xuất phần trăm mã hóa (Percentage Encrypted)
            percent_match = re.search(r'Percentage Encrypted:\s+(.*)', output)
            percent_encrypted = percent_match.group(1).strip() if percent_match else "N/A"

            # Lưu kết quả
            results[letter] = {
                "Conversion Status": conversion_status,
                "Protection Status": protection_status,
                "BitLocker Version": bitlocker_version,
                "Percent Encrypted": percent_encrypted
            }
            print(f"  > Conversion Status: {conversion_status}")
            print(f"  > Protection Status: {protection_status}")
            print(f"  > BitLocker Version: {bitlocker_version}")
            print(f"  > % Encrypted: {percent_encrypted}")

        except FileNotFoundError:
            results[letter] = {"Error": "The 'manage-bde' command was not found."}
            print(f"  > Error: The 'manage-bde' command was not found.")
        except Exception as e:
            results[letter] = {"Error": str(e)}
            print(f"  > Unknown error: {e}")
    return results

# --- Ví dụ sử dụng ---

# Danh sách các ổ đĩa bạn muốn kiểm tra (điền các ký tự ổ đĩa của bạn vào đây)
drive_letters_to_check = run_diskpart_and_extract_ltr()

# Thực thi hàm
def check_bitlocker():
    bitlocker_results = check_bitlocker_status(drive_letters_to_check)

    # In kết quả tổng hợp
    for letter, data in bitlocker_results.items():
        if "Error" in data:
            print(f"Drive {letter}: ERROR ({data['Error']})")
        else:
            # Định dạng output để dễ đọc hơn
            status = data['Protection Status']
            if status == "Protection Off":
                display_status = f"Turned Off ({data['Percent Encrypted']})"
            elif status == "Protection On":
                display_status = f"Enabled - Encrypted ({data['Percent Encrypted']})"
            else:
                display_status = f"{status} ({data['Percent Encrypted']})"


# --- Hàm tiện ích hỏi xác nhận ---
def _get_confirmation(action_text, drive_letters):
    """Yêu cầu xác nhận từ người dùng.
    - Nếu có môi trường GUI, dùng tkinter.messagebox.askyesno.
    - Ngược lại fallback về input() trên console.
    Trả về True khi người dùng xác nhận, False khi từ chối hoặc lỗi.
    """
    drive_list = ", ".join([f"{d}:" for d in drive_letters])
    title = "Confirm BitLocker"
    msg = f"ARE YOU SURE you want to {action_text} BitLocker for the following drives: {drive_list}?"

    # Thử dùng GUI (tkinter.messagebox)
    try:
        import tkinter as tk
        from tkinter import messagebox

        root_created = False
        # Nếu chưa có root, tạo một root ẩn tạm thời để messagebox hoạt động
        if not getattr(tk, "_default_root", None):
            root = tk.Tk()
            root.withdraw()
            root_created = True

        answer = messagebox.askyesno(title, msg)

        # Nếu ta đã tạo root tạm, huỷ nó
        if root_created:
            try:
                root.destroy()
            except Exception:
                pass

        return bool(answer)
    except Exception:
        # Fallback: console input (y/n)
        try:
            resp = input(f"{msg} (y/n): ")
            return str(resp).strip().lower().startswith('y')
        except Exception:
            return False

# --- Hàm BẬT BitLocker (manage-bde -on) ---
def enable_bitlocker(drive_letters):
    """
    Thực thi lệnh 'manage-bde -on X:' để bật mã hóa BitLocker.

    LƯU Ý QUAN TRỌNG: Script phải chạy với quyền Administrator.
    Lệnh -on chỉ bắt đầu mã hóa. Cần thiết lập Key Protector (mật khẩu, TPM, v.v.)
    bằng các lệnh manage-bde khác hoặc qua giao diện Windows sau đó.
    """
    action_text = "ENABLE"
    action_cmd = "-on"
    
    if os.name != 'nt':
        print(f"Error: The 'manage-bde' command is only available on Windows.")
        return

    if not _get_confirmation(action_text, drive_letters):
        print(f"Canceling {action_text} BitLocker operation.")
        return
        
    print(f"--- GET STARTED {action_text} BITLOCKER ---")

    for letter in drive_letters:
        drive = f"{letter}:"
        command = ['manage-bde', action_cmd, drive]
        
        print(f"\nExecuting command {action_cmd} for drive {drive}...")
        
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            output = result.stdout
            
            if "ERROR" in output.upper() or result.returncode != 0:
                print(f"  [❌ FAILED] An error occurred on drive {drive}.")
                print("  NOTE: Usually due to lack of Administrator privileges, drive already encrypted, or missing Key Protector.")
            else:
                print(f"  [✅ SUCCESS] Sent {action_text} BitLocker command to drive {drive}.")
                print("  * Check the status afterwards and set up a Key Protector!")

        except FileNotFoundError:
            print(f"  [❌ FAILED] Error: 'manage-bde' command not found.")
        except Exception as e:
            print(f"  [❌ FAILED] Unknown error: {e}")

    print("\n--- END ENABLE BITLOCKER OPERATION ---")


# --- Hàm TẮT BitLocker (manage-bde -off) ---
def disable_bitlocker(drive_letters):
    """
    Thực thi lệnh 'manage-bde -off X:' để tắt (giải mã) BitLocker.

    LƯU Ý: Script phải chạy với quyền Administrator.
    Quá trình giải mã diễn ra ngầm và có thể mất rất nhiều thời gian.
    """

    action_text = "DISABLE"
    action_cmd = "-off"
    
    if os.name != 'nt':
        print(f"Error: The 'manage-bde' command is only available on Windows.")
        return

    if not _get_confirmation(action_text, drive_letters):
        print(f"Canceling {action_text} BitLocker operation.")
        return

    print(f"--- GET STARTED {action_text} BITLOCKER ---")

    for letter in drive_letters:
        drive = f"{letter}:"
        command = ['manage-bde', action_cmd, drive]

        print(f"\nExecuting command {action_cmd} for drive {drive}...")

        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            output = result.stdout
            
            if "ERROR" in output.upper() or result.returncode != 0:
                print(f"  [❌ FAILED] An error occurred on drive {drive}.")
                print("  NOTE: Usually due to lack of Administrator privileges or drive not being encrypted.")
            else:
                print(f"  [✅ SUCCESS] Sent {action_text} BitLocker command to drive {drive}.")
                print("  The decryption process will run in the background. Use the '-status' command to monitor progress.")

        except FileNotFoundError:
            print(f"  [❌ FAILED] Error: 'manage-bde' command not found.")
        except Exception as e:
            print(f"  [❌ FAILED] Unknown error: {e}")

    print("\n--- END DISABLE BITLOCKER OPERATION ---")

# --- Ví dụ sử dụng ---

    # enable_bitloc