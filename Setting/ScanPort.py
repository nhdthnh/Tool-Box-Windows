import socket

def scan_port_status(target_ip, port, timeout=1):
    """
    Kiểm tra trạng thái của một cổng TCP cụ thể.

    Args:
        target_ip (str): Địa chỉ IP hoặc tên miền.
        port (int): Số cổng cần kiểm tra.
        timeout (float): Thời gian chờ kết nối (giây).

    Returns:
        str: 'Open' nếu cổng mở, 'Closed' nếu cổng đóng hoặc lỗi.
    """
    try:
        # 1. Tạo một socket (AF_INET cho IPv4, SOCK_STREAM cho TCP)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # 2. Thiết lập timeout để tránh bị treo
        sock.settimeout(timeout)
        
        # 3. Cố gắng kết nối
        result = sock.connect_ex((target_ip, port))
        
        # 4. Kiểm tra kết quả
        if result == 0:
            return "Open"
        else:
            return "Closed" # Có thể là cổng bị chặn/đóng

    except socket.gaierror:
        return "Lỗi: Không tìm thấy địa chỉ (Hostname/IP không hợp lệ)"
    except socket.error as e:
        return f"Lỗi Socket: {e}"
    finally:
        # Đảm bảo đóng socket sau khi hoàn thành
        sock.close()

# --- CHẠY THỬ NGHIỆM ĐƠN LẺ ---
target = '113.161.75.195' # Một IP công khai an toàn cho việc thử nghiệm
port_to_check = 80
status = scan_port_status(target, port_to_check)
print(f"Cổng {port_to_check} trên {target} đang ở trạng thái: {status}")