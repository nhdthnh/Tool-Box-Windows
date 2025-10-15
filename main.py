import tkinter as tk
from tkinter import messagebox, scrolledtext
import sys
import ctypes
import threading
import time
import platform
import subprocess
import os

# --- 1. DANH SÁCH KMS SERVERS VÀ HÀM GỌI ---
kms_servers = [
    "win.xdyxm11235.com", "s1.kms.cx", "kms.000606.xyz", "kms.03k.org", "kms.shuax.com", 
    "kms.loli-best", "kms.loli-beer", "kms.sgtsoft.com", "kms.moeyuuko.top", "kms.digiboy.ir", 
    "kms.kursktu.com", "kms.lucyinfo.top", "kms.sixyin.com", "kms-default.cangshui.net", 
    "kms.moerats.com", "kms.ben-zhutop", "kms.akams.cn", "kms8.mspguides.com", 
    "kms.kmszs123.cn", "kms.bigeo.cn", "kms.litbear.cn", "kms.ddddg.cn", "win.freekms.cn", 
    "hq1.chinancce.com", "54.223.212.31", "kms.cnlic.com", "kms.chinancce.com", 
    "kms.ddns.net", "franklv.ddns.net", "k.zpale.com", "m.zpale.com", "mvg.zpale.com", 
    "kensol263.imwork.net:1688", "xykz.f3322.org", "kms789.com", "dimanyakms.sytes.net:1688", 
    "kms.03k.org:1688" 
]
# -------------------------------------------------------------

# --- 2. IMPORT CÁC HÀM HỆ THỐNG ---
try:
    # --- CÁC HÀM CŨ ---
    from BackUpDriver import backup_drivers_cmd
    from CheckStatus import check_office_license_status, check_windows_license_status_no_popup
    from Remove import remove_office_key_advanced, remove_windows_key
    from KMS_online import activate_office, activate_windows
    from SystemInfo import get_system_info
    
    # --- CÁC HÀM MỚI BẠN YÊU CẦU ---
    from Setting.DiskMonitor import run_diskpart_and_extract_ltr, print_device_usage_for_letters
    from Setting.WindowsUpdate import enable_windows_update, disable_windows_update
    from Setting.Firewall import enable_firewall, disable_firewall, check_firewall_status, open_allow_app_through_firewall_ui_fix2_rundll
    from Setting.HanoiTime import set_windows_timezone_by_ip
    from Setting.GetWanIp import display_ip_wan
    from Setting.NetworkInfo import ipconfig
    from Setting.Ping import run_ping_test
    from Setting.RenewIP import release_flush_renew_network
    from Setting.ScanAllPort import start_local_netstat_analysis
    from Setting.my_speedtest_internet import format_speedtest_results
    from Setting.ThisPC import set_explorer_default_this_pc, remove_explorer_default_setting
    from Setting.StaticIP import static_ip_setting
    from Setting.Bitlocker import check_bitlocker, enable_bitlocker, disable_bitlocker
    from Setting.RemoveTrash import call_cleanup_routine
    from Setting.RestoreDriver import restore_drivers
    from Setting.SFC  import run_chkdsk, run_sfc_scan
    from Setting.Registry import main as main_registry
    from Setting.Menu import Menu 
    # Định nghĩa các hàm gọi với server list
    def activate_windows_with_servers():
        activate_windows(kms_servers)
    def activate_office_with_servers():
        activate_office(kms_servers)

except ImportError as e:
    # --- DUMMY FUNCTIONS ---
    print(f"Import error: {e}. Using dummy functions to avoid crash.")
    def _dummy_func(name):
        print(f"Function {name} is not available."); messagebox.showinfo("Result", f"Function {name} is not available.")

    # Dummy cho các hàm cũ
    def backup_drivers_cmd(): _dummy_func("Backup Driver")
    def check_windows_license_status_no_popup(): _dummy_func("Check Windows Status")
    def check_office_license_status(): _dummy_func("Check Office Status")
    def remove_windows_key(): _dummy_func("Remove Windows Key")
    def remove_office_key_advanced(): _dummy_func("Remove Office Key")
    def activate_windows_with_servers(): _dummy_func("Activate Windows")
    def activate_office_with_servers(): _dummy_func("Activate Office")
    def get_system_info(): _dummy_func("System Information")

    # Dummy cho các hàm mới
    def run_diskpart_and_extract_ltr(): _dummy_func("Disk Ltr")
    def print_device_usage_for_letters(ltr_list): _dummy_func("Disk Usage")
    def enable_windows_update(): _dummy_func("Enable Windows Update")
    def disable_windows_update(): _dummy_func("Disable Windows Update")
    def enable_firewall(): _dummy_func("Enable Firewall")
    def disable_firewall(): _dummy_func("Disable Firewall")
    def set_timezone_windows(): _dummy_func("Set Hanoi Time")
    def get_wan_ip(): _dummy_func("Get WAN IP")
    def ipconfig(): _dummy_func("Network Info")
    def run_ping_test(): _dummy_func("Ping Test")
    def release_flush_renew_network(): _dummy_func("Renew IP")
    def start_local_netstat_analysis(): _dummy_func("Port Scan")
    def format_speedtest_results(): _dummy_func("Speed Test")
    def set_explorer_default_this_pc(): _dummy_func("Set Explorer This PC")
    def remove_explorer_default_setting(): _dummy_func("Remove Explorer Setting")
    def static_ip_setting(): _dummy_func("Static IP Setting")
    def check_bitlocker(): _dummy_func("Check BitLocker")
    def enable_bitlocker(): _dummy_func("Enable BitLocker")
    def disable_bitlocker(): _dummy_func("Disable BitLocker")
    def call_cleanup_routine(): _dummy_func("Remove Trash Files")
    def restore_drivers(): _dummy_func("Restore Drivers")
    def run_sfc_scan(): _dummy_func("Run SFC Scan")
    def run_chkdsk(): _dummy_func("Run CHKDSK")
    def main_registry(): _dummy_func("Registry Editor")
    def Menu(): _dummy_func("Context Menu Editor")
# ------------------------------------


# --- LỚP CHUYỂN HƯỚNG CONSOLE ---
class ConsoleRedirect:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.last_char = '\n'
    def write(self, string):
        # Tránh các dòng trống liên tiếp
        if string == '\n' and self.last_char == '\n': return
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.last_char = string[-1] if string else self.last_char
    def flush(self):
        pass
# --------------------------------


class SystemManagerApp:
    def __init__(self, master):
        self.master = master
        master.title("WINDOWS TOOLS - by NHU DINH THANH (VIETNAM)")
        master.resizable(False, False)

        # 1. Khung chứa các nút (Dùng để sắp xếp 3 cột Active/System/Network)
        main_button_frame = tk.Frame(master)
        main_button_frame.pack(pady=5)
        
        # 2. Định nghĩa 3 Frame cho 3 cột
        self.active_frame = self._create_bordered_frame(main_button_frame, "Active", 0, 0)
        self.system_frame = self._create_bordered_frame(main_button_frame, "System", 0, 1)
        self.network_frame = self._create_bordered_frame(main_button_frame, "Network", 0, 2)

        # 3. Định nghĩa cấu hình nút theo nhóm (Group, Text, Task_Func, Frame)
        buttons_config = [
            # Group Active (Active/Quản lý Key)
            {"text": "Status key win/office", "task": self.run_check_status_tasks, "frame": self.active_frame},
            {"text": "Delete key Win", "task": self.run_remove_key_tasks_window, "frame": self.active_frame},
            {"text": "Delete key Office", "task": self.run_remove_key_tasks_office, "frame": self.active_frame},
            {"text": "Active Windows", "task": self.run_activate_windows_tasks, "frame": self.active_frame},
            {"text": "Active Office", "task": self.run_activate_office_tasks, "frame": self.active_frame},

            # Group System (Hệ thống/Cài đặt)
            {"text": "Backup Driver", "task": self.run_backup_drivers_tasks, "frame": self.system_frame},
            {"text": "Restore Driver", "task": self.run_restore_drivers_tasks, "frame": self.system_frame},
            {"text": "System Info", "task": self.run_system_info_tasks, "frame": self.system_frame},
            {"text": "Set Timezone Location", "task": self.run_set_hanoi_time_task, "frame": self.system_frame},
            {"text": "Set Explorer This PC", "task": self.run_set_explorer_this_pc_task, "frame": self.system_frame},
            {"text": "Remove Explorer Default", "task": self.run_remove_explorer_default_task, "frame": self.system_frame},
            {"text": "Device Usage", "task": self.run_disk_monitor_task, "frame": self.system_frame},
            {"text": "Enable Windows Update", "task": self.run_enable_win_update_task, "frame": self.system_frame},
            {"text": "Disable Windows Update", "task": self.run_disable_win_update_task, "frame": self.system_frame},
            {"text": "Enable Firewall", "task": self.run_enable_firewall_task, "frame": self.system_frame},
            {"text": "Disable Firewall", "task": self.run_disable_firewall_task, "frame": self.system_frame},
            {"text": "Check Firewall Status", "task": self.run_check_firewall_task, "frame": self.system_frame},
            {"text": "Open Firewall", "task": self.run_open_allow_app_firewall_ui_task, "frame": self.system_frame},
            {"text": "Check BitLocker", "task": self.run_check_bitlocker_task, "frame": self.system_frame},
            {"text": "Enable BitLocker", "task": self.run_enable_bitlocker_task, "frame": self.system_frame},
            {"text": "Disable BitLocker", "task": self.run_disable_bitlocker_task, "frame": self.system_frame},
            {"text": "Remove Trash Files", "task": self.run_remove_trash_files_task, "frame": self.system_frame},
            {"text": "Run SFC Scan", "task": self.run_sfc_scan_task, "frame": self.system_frame},
            {"text": "Run CHKDSK", "task": self.run_chkdsk_task, "frame": self.system_frame},
            {"text": "Registry", "task": main_registry, "frame": self.system_frame },
            {"text": "Menu context", "task": self.run_menu_task, "frame": self.system_frame },
            # Group Network (Mạng)
            {"text": "Get WAN IP", "task": self.run_get_wan_ip_task, "frame": self.network_frame},
            {"text": "IPConfig", "task": self.run_ipconfig_task, "frame": self.network_frame},
            {"text": "Ping Test", "task": self.run_ping_test_task, "frame": self.network_frame},
            {"text": "Renew/Release IP", "task": self.run_renew_ip_task, "frame": self.network_frame},
            {"text": "Port Scanner", "task": self.run_port_scan_task, "frame": self.network_frame},
            {"text": "Speed Test", "task": self.run_speed_test_task, "frame": self.network_frame},
            {"text": "Static IP Setting", "task": self.run_static_ip_setting_task, "frame": self.network_frame},
        ]
        
        # 4. Tạo các nút trong từng Frame
        self._create_buttons(buttons_config)

        # 5. Khung Text để hiển thị Console        
        self.console_text = scrolledtext.ScrolledText(
            master, 
            wrap=tk.WORD, 
            width=100, # Tăng chiều rộng để phù hợp với màn hình lớn hơn
            height=15, 
            font=("Consolas", 9), 
            bg="#2e2e2e", 
            fg="#f0f0f0"
        )
        self.console_text.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)
        
        # CHUYỂN HƯỚNG OUTPUT
        self.original_stdout = sys.stdout
        sys.stdout = ConsoleRedirect(self.console_text)
        
        # In ra trạng thái quyền Admin
        admin_status = self._check_admin_status()
        print(f">>> Admin Privilege: {admin_status}. Please select a task. Output is here\n")
        
    def _create_bordered_frame(self, parent, title, row, col):
        # Hàm tạo Frame có viền và tiêu đề
        frame = tk.LabelFrame(
            parent, 
            text=title, 
            padx=10, 
            pady=5, 
            font=("Arial", 9, "bold")
        )
        frame.grid(row=row, column=col, padx=10, pady=5, sticky=tk.N)
        return frame

    def _create_buttons(self, config):
        # Hàm tạo và sắp xếp nút trong các Frame đã định nghĩa
        max_rows_per_col = 7  # số nút tối đa trên 1 cột trước khi wrap sang cột kế
        frame_positions = {}  # frame -> [current_row, current_col]
        
        for item in config:
            frame = item["frame"]
            text = item["text"]
            task_func = item["task"]
            
            # Khởi tạo vị trí cho frame nếu chưa có
            if frame not in frame_positions:
                frame_positions[frame] = [0, 0]
            
            row, col = frame_positions[frame]
            
            # đảm bảo cột hiện tại có thể giãn nở
            try:
                frame.columnconfigure(col, weight=1)
            except Exception:
                pass
            
            btn = tk.Button(
                frame, 
                text=text, 
                command=lambda tf=task_func: self.run_task_in_thread(tf), 
                font=("Arial", 8), 
                width=20, 
                height=1,
                bg="#fff"
            )
            btn.grid(row=row, column=col, padx=5, pady=2, sticky=tk.EW)
            
            # Cập nhật vị trí cho nút tiếp theo; nếu vượt max_rows_per_col -> wrap sang cột tiếp
            row += 1
            if row >= max_rows_per_col:
                row = 0
                col += 1
            frame_positions[frame] = [row, col]
            
    def _check_admin_status(self):
        # Hàm này được gọi trong __init__ để in trạng thái quyền Admin
        return "Active" if ctypes.windll.shell32.IsUserAnAdmin() else "Inactive"

    def __del__(self):
        # Đặt lại stdout khi ứng dụng đóng
        sys.stdout = self.original_stdout

    # --- HÀM CHẠY TÁC VỤ TRONG LUỒNG RIÊNG (Thread) ---
    def run_task_in_thread(self, task_func):
        if task_func:
            # 1. Delete Console
            try:
                self.console_text.delete('1.0', tk.END)
            except Exception:
                pass
            # Reset ConsoleRedirect's last_char so initial newlines are shown
            try:
                if isinstance(sys.stdout, ConsoleRedirect):
                    sys.stdout.last_char = '\n'
            except Exception:
                pass

            
            # 2. Vô hiệu hóa tất cả các nút trong button_frame (bao gồm 3 frame con)
            for frame in [self.active_frame, self.system_frame, self.network_frame]:
                for widget in frame.winfo_children():
                    if isinstance(widget, tk.Button):
                        widget.config(state=tk.DISABLED)
                            
            # 3. Chạy tác vụ trong luồng riêng
            thread = threading.Thread(target=self._execute_and_enable, args=(task_func,))
            thread.start()

    # Hàm thực thi và Active lại
    def _execute_and_enable(self, task_func):
        try:
            task_func()
        except Exception as e:
            # Xử lý lỗi trong thread
            print(f"\n[IMPORTANT ERROR] failed: {e}")
            messagebox.showerror("Task Error", f"Task encountered an unexpected error: {e}")
        finally:
            # Active lại tất cả các nút
            for frame in [self.active_frame, self.system_frame, self.network_frame]:
                for widget in frame.winfo_children():
                    if isinstance(widget, tk.Button):
                        widget.config(state=tk.NORMAL)

    # --- CÁC HÀM GỌI TÁC VỤ ĐƯỢC CHẠY TRONG THREAD (CŨ) ---
    def run_check_status_tasks(self):
        check_windows_license_status_no_popup()
        check_office_license_status()
    
    def run_remove_key_tasks_window(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete the Windows activation key?"):
            remove_windows_key()


    def run_remove_key_tasks_office(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete the Office activation key?"):
            remove_office_key_advanced()

    def run_activate_windows_tasks(self):
        activate_windows_with_servers()

    def run_activate_office_tasks(self):
        activate_office_with_servers()
        
    def run_system_info_tasks(self):
        get_system_info()
    
    def run_menu_task(self):
        Menu() 
        
    def run_backup_drivers_tasks(self):
        backup_drivers_cmd()
        
    # --- CÁC HÀM GỌI TÁC VỤ MỚI (NETWORK/DISK/SETTING) ---

    def run_speed_test_task(self):
        format_speedtest_results()

    def run_disk_monitor_task(self):
        ltr_list = run_diskpart_and_extract_ltr()
        if ltr_list:
            print_device_usage_for_letters(ltr_list)

    def run_enable_win_update_task(self):
        enable_windows_update()
    
    def run_restore_drivers_tasks(self):
        restore_drivers()

    def run_disable_win_update_task(self):
        disable_windows_update()

    def run_enable_firewall_task(self):
        enable_firewall()

    def run_disable_firewall_task(self):
        disable_firewall()

    def run_set_hanoi_time_task(self):
        set_windows_timezone_by_ip()

    def run_get_wan_ip_task(self):
        display_ip_wan()

        
    def run_ipconfig_task(self):
        ipconfig()
        
    def run_ping_test_task(self):
        run_ping_test()

    def run_renew_ip_task(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to perform the Release, Flush DNS, and Renew IP commands? (This may temporarily disrupt your network connection)"):
            release_flush_renew_network()

    def run_port_scan_task(self):
        start_local_netstat_analysis()
        
    def run_set_explorer_this_pc_task(self):
        set_explorer_default_this_pc()

    def run_remove_explorer_default_task(self):
        remove_explorer_default_setting()   
    
    def run_sfc_scan_task(self):
        run_sfc_scan()
    
    def run_chkdsk_task(self):
        run_chkdsk()
    def run_check_firewall_task(self):
        check_firewall_status()

    def run_open_allow_app_firewall_ui_task(self):
        open_allow_app_through_firewall_ui_fix2_rundll()

    def run_static_ip_setting_task(self):
        static_ip_setting()
    def run_check_bitlocker_task(self):
        check_bitlocker()
    def run_enable_bitlocker_task(self):
        # show prompt and call enable_bitlocker(device) in background
        self._prompt_drive_and_run("Enable BitLocker", enable_bitlocker)

    def run_disable_bitlocker_task(self):
        # show prompt and call disable_bitlocker(device) in background
        self._prompt_drive_and_run("Disable BitLocker", disable_bitlocker)
    def run_remove_trash_files_task(self):
        call_cleanup_routine()
    def run_registry_editor_task(self):
        main_registry()

    def _prompt_drive_and_run(self, title, action_func):
        """
        Hiển thị dialog nhỏ để nhập ký tự ổ (ví dụ: D) và khi OK sẽ gọi action_func("D:") trong luồng nền.
        """
        dlg = tk.Toplevel(self.master)
        dlg.title(title)
        dlg.resizable(False, False)
        dlg.grab_set()  # modal

        tk.Label(dlg, text="Input disk letter (Example: D):").grid(row=0, column=0, padx=8, pady=(8,4))
        entry = tk.Entry(dlg, width=6)
        entry.grid(row=0, column=1, padx=8, pady=(8,4))
        entry.focus_set()

        def on_ok():
            raw = entry.get().strip().upper().rstrip(':')
            if not raw or not raw.isalpha() or len(raw) != 1:
                messagebox.showwarning("Error", "Please enter a valid disk letter (A-Z).")
                return
            device = f"{raw}:"
            dlg.destroy()

            # disable buttons
            for frame in [self.active_frame, self.system_frame, self.network_frame]:
                for w in frame.winfo_children():
                    if isinstance(w, tk.Button):
                        w.config(state=tk.DISABLED)

            def worker(dev):
                try:
                    print(f"\n[START] {title} cho {dev} ...")
                    action_func(dev)
                    print(f"[OK] Complete: {title} for {dev}")
                except Exception as e:
                    print(f"[ERROR] {title} for {dev} failed: {e}")
                finally:
                    # re-enable buttons
                    for frame in [self.active_frame, self.system_frame, self.network_frame]:
                        for w in frame.winfo_children():
                            if isinstance(w, tk.Button):
                                w.config(state=tk.NORMAL)

            threading.Thread(target=worker, args=(device,), daemon=True).start()

        def on_cancel():
            dlg.destroy()

        btn_ok = tk.Button(dlg, text="OK", width=8, command=on_ok)
        btn_ok.grid(row=1, column=0, pady=8, padx=8)
        btn_cancel = tk.Button(dlg, text="Cancel", width=8, command=on_cancel)
        btn_cancel.grid(row=1, column=1, pady=8, padx=8)

        # bind Enter/Escape
        dlg.bind("<Return>", lambda e: on_ok())
        dlg.bind("<Escape>", lambda e: on_cancel())

# --- Status VÀ NÂNG QUYỀN ADMINISTRATOR ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    # Sử dụng logic nâng quyền đã có trong code gốc
    print("Requesting Administrator privileges...")
    try:
        # Chạy lại chương trình với quyền admin
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit(0)
    except Exception:
        messagebox.showerror("Access Error", "The program requires Administrator privileges to perform system tasks. The program will exit.")
        sys.exit(1)
# -------------------------------------------


# Chạy chương trình
if __name__ == "__main__":
    root = tk.Tk()
    app = SystemManagerApp(root)
    root.mainloop()