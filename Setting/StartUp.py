import os
import time
import pyautogui

def open_task_manager_to_startup():
    """
    Mở Task Manager và chuyển sang tab Startup bằng cách sử dụng
    lệnh hệ thống và mô phỏng nhấn phím (pyautogui).
    """
    
    print("Bước 1: Mở Task Manager...")
    try:
        # Lệnh để mở Task Manager. 
        # taskmgr.exe được coi là lệnh hệ thống trên Windows.
        os.system('taskmgr')
        
        # Đợi một chút để Task Manager có thời gian khởi động
        time.sleep(1) 
        
        # Task Manager có 6 tab chính. Phím tắt để di chuyển giữa các tab là CTRL + TAB.
        # Chúng ta cần nhấn CTRL + TAB 3 lần để chuyển từ tab mặc định (Processes) 
        # sang tab Startup. (Processes -> Performance -> App history -> Startup)
        
        print("Bước 2: Chuyển đến tab Khởi động (Startup)...")
        
        # Nhấn CTRL + TAB (4 lần)
        # Lưu ý: Các phiên bản Windows khác nhau có thể có thứ tự tab khác nhau. 
        # Tab phổ biến nhất là Processes (0) -> Performance (1) -> App history (2) -> Startup (3).
        # Ta cần nhấn 3 lần nếu Task Manager đang mở ở Processes.
        # Nếu không chắc chắn, bạn có thể thử 3, 4, hoặc 5 lần.
        
        # Nhấn tổ hợp phím CTRL + TAB 3 lần
        for i in range(3):
            pyautogui.hotkey('ctrl', 'tab')
            time.sleep(0.1) # Khoảng nghỉ nhỏ giữa các lần nhấn
        
        print("Hoàn thành! Task Manager đã được mở tại tab Khởi động.")
        
    except Exception as e:
        print(f"Đã xảy ra lỗi trong quá trình thực thi: {e}")

# Thực thi hàm
open_task_manager_to_startup()