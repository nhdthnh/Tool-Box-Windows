import requests
import json
import socket

def get_wan_ip():
    """Lấy địa chỉ IP WAN (Public IP) bằng cách truy vấn một dịch vụ API."""
    try:
        # Sử dụng API đơn giản và đáng tin cậy để lấy IP (ví dụ: ipify)
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        response.raise_for_status() # Kiểm tra lỗi HTTP
        data = response.json()
        return data.get('ip')
    except requests.exceptions.RequestException as e:
        print(f"Lỗi: Không thể lấy IP WAN. Kiểm tra kết nối mạng. Chi tiết: {e}")
        return None

def detect_ip_location(ip_address):
    """
    Phát hiện vị trí (Geolocation) của IP bằng cách sử dụng dịch vụ ip-api.com.
    
    Lưu ý: API này miễn phí nhưng giới hạn 45 yêu cầu mỗi phút.
    """
    if not ip_address:
        return {"Error": "Không có địa chỉ IP để tra cứu."}
        
    # Endpoint của ip-api.com
    api_url = f'http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query'
    
    print(f"\nĐang tra cứu vị trí cho IP: {ip_address}...")

    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'success':
            return data
        else:
            return {"Error": f"Tra cứu thất bại. Thông báo API: {data.get('message', 'Không rõ lỗi')}"}

    except requests.exceptions.RequestException as e:
        return {"Error": f"Lỗi: Không thể kết nối tới dịch vụ định vị. Chi tiết: {e}"}

# --- Thực thi Chương trình ---

def main():
    # Bước 1: Lấy IP WAN
    wan_ip = get_wan_ip()

    if wan_ip:
        print(f"Địa chỉ IP WAN của bạn là: {wan_ip}")
        
        # Bước 2: Tra cứu vị trí
        location_data = detect_ip_location(wan_ip)
        
        # Bước 3: Hiển thị kết quả
        print("\n--- KẾT QUẢ ĐỊNH VỊ IP ---")
        
        if "Error" in location_data:
            print(f"Trạng thái: THẤT BẠI - {location_data['Error']}")
        else:
            print(f"Trạng thái: THÀNH CÔNG")
            print(f"Quốc gia:   {location_data.get('country')} ({location_data.get('countryCode')})")
            print(f"Vùng/Thành phố: {location_data.get('regionName')}, {location_data.get('city')}")
            print(f"Nhà cung cấp (ISP): {location_data.get('isp')}")
            print(f"Múi giờ:    {location_data.get('timezone')}")
            print(f"Tọa độ:     Lat={location_data.get('lat')}, Lon={location_data.get('lon')}")
    else:
        print("Không thể tiến hành định vị do không lấy được IP WAN.")

if __name__ == "__main__":
    main()