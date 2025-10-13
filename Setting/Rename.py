import subprocess
import sys

# Đặt tên mới cho máy tính
def rename_pc(NEW_COMPUTER_NAME):
    # Lệnh PowerShell để đổi tên máy tính
    # LƯU Ý: Không dùng -Restart để tránh khởi động lại ngay lập tức
    powershell_command = f'Rename-Computer -NewName "{NEW_COMPUTER_NAME}"'

    # Cấu trúc gọi lệnh:
    # 1. 'powershell.exe': Gọi trình thông dịch PowerShell
    # 2. '-Command': Bảo PowerShell thực thi chuỗi lệnh tiếp theo
    try:
        print(f"Bắt đầu đổi tên máy tính sang: {NEW_COMPUTER_NAME}")
        
        # Thực thi lệnh PowerShell
        # shell=True giúp PowerShell xử lý chuỗi lệnh dễ dàng hơn
        result = subprocess.run(
            ['powershell.exe', '-Command', powershell_command],
            capture_output=True,
            text=True,
            check=True # Nếu lệnh trả về lỗi, sẽ raise exception
        )
        
        # Kiểm tra kết quả
        if result.returncode == 0:
            print("Đổi tên máy tính thành công (không khởi động lại ngay).")
            print(f"*** LƯU Ý QUAN TRỌNG: Máy tính CẦN phải được khởi động lại để tên mới ({NEW_COMPUTER_NAME}) có hiệu lực. ***")
        else:
            # Trường hợp hiếm gặp nếu check=True không bắt được
            print(f"Lệnh thực thi không thành công. Mã lỗi: {result.returncode}")

    except subprocess.CalledProcessError as e:
        # Xử lý lỗi nếu lệnh PowerShell thất bại (ví dụ: không có quyền Admin)
        print("!!! LỖI khi thực thi lệnh PowerShell !!!")
        print(f"Stdout (output): \n{e.stdout}")
        print(f"Stderr (error): \n{e.stderr}")
        print("\nCó thể bạn cần chạy script Python này với quyền **Administrator**.")

    except FileNotFoundError:
        print("Lỗi: Không tìm thấy 'powershell.exe'. Đảm bảo bạn đang chạy trên Windows.")

    except Exception as ex:
        print(f"Đã xảy ra lỗi không xác định: {ex}")