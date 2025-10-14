import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import winreg
import subprocess

# --- Core Logic: Registry Tweak Functions (Unchanged) ---

def set_registry_value(hkey, key_path, value_name, data, data_type=winreg.REG_DWORD):
    """General function to set a single Registry value."""
    try:
        key = winreg.CreateKey(hkey, key_path)
        winreg.SetValueEx(key, value_name, 0, data_type, data)
        winreg.CloseKey(key)
        return True
    except PermissionError:
        messagebox.showerror("Permission Error", "Requires Administrator privileges to modify Registry.")
        return False
    except Exception as e:
        messagebox.showerror("Registry Error", f"Cannot change value at '{key_path}': {e}")
        return False

def set_indexing_tweak(disable: bool):
    """Toggle Windows Search Indexing (Disable=1, Enable=0)."""
    key_path = r"SOFTWARE\Policies\Microsoft\Windows\Windows Search"
    value_name = "PreventIndexOnClients"
    data = 1 if disable else 0
    return set_registry_value(winreg.HKEY_LOCAL_MACHINE, key_path, value_name, data)

def set_telemetry_tweak(disable: bool):
    """Toggle Windows Telemetry (Disable=0, Enable=1)."""
    key_path = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
    value_name = "AllowTelemetry"
    data = 0 if disable else 1
    return set_registry_value(winreg.HKEY_LOCAL_MACHINE, key_path, value_name, data)

def set_tcp_latency_tweak(enable: bool):
    """
    Toggles TCP Latency reduction by setting TcpAckFrequency=1 and TCPNoDelay=1
    in the active network interface registry key.
    """
    results = []
    interfaces_path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
    
    try:
        root_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, interfaces_path, 0, winreg.KEY_READ)
        i = 0
        while True:
            try:
                guid = winreg.EnumKey(root_key, i)
                i += 1
                
                # Check for existing IPAddress/DhcpIPAddress to assume active adapter
                try:
                    interface_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{interfaces_path}\\{guid}", 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
                    
                    # Check for an IP address value (simple heuristic for active adapter)
                    try:
                        winreg.QueryValueEx(interface_key, "DhcpIPAddress")
                        is_active = True
                    except FileNotFoundError:
                        try:
                            winreg.QueryValueEx(interface_key, "IPAddress")
                            is_active = True
                        except FileNotFoundError:
                            is_active = False # Not the correct key
                    
                    if is_active:
                        value = 1 if enable else 0
                        
                        # 1. TcpAckFrequency (DWORD)
                        winreg.SetValueEx(interface_key, "TcpAckFrequency", 0, winreg.REG_DWORD, value)
                        # 2. TCPNoDelay (DWORD)
                        winreg.SetValueEx(interface_key, "TCPNoDelay", 0, winreg.REG_DWORD, value)
                        
                        winreg.CloseKey(interface_key)
                        
                        status = "ENABLED" if enable else "DISABLED"
                        results.append(f"Reduce Network Latency (Adapter {guid[:8]}): {status}")
                    
                except OSError:
                    continue # Skip keys we can't open/modify
            except OSError:
                break # Reached the end of subkeys

        winreg.CloseKey(root_key)
        
        if results:
            return True, results
        else:
            return False, ["Error: No active network adapters could be modified for TCP tweaks."]
            
    except PermissionError:
        return False, ["Error: Administrator privileges are required for TCP network tweaks."]
    except Exception as e:
        return False, [f"Error applying TCP Latency tweak: {e}"]


# --- Core Logic: Backup & Restore Functions (Unchanged) ---

def backup_registry_key():
    """Saves a specified Registry Key to a binary file (.dat) using winreg.SaveKey."""
    key_input = simpledialog.askstring("Input", "Enter the Registry Key path to backup (e.g., SOFTWARE\\MyKey):")
    if not key_input: return

    file_path = filedialog.asksaveasfilename(defaultextension=".dat",
                                             filetypes=[("Registry Backup Files", "*.dat")],
                                             title="Save Registry Backup File")
    if not file_path: return

    try:
        key_handle = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_input, 0, winreg.KEY_BACKUP | winreg.KEY_READ)
        winreg.SaveKey(key_handle, file_path)
        winreg.CloseKey(key_handle)
        messagebox.showinfo("Success", f"Key '{key_input}' successfully backed up to:\n{file_path}")
    except PermissionError:
        messagebox.showerror("Permission Error", "Administrator rights needed for this operation.")
    except FileNotFoundError:
        messagebox.showerror("Error", f"Registry Key not found:\n{key_input}")
    except Exception as e:
        messagebox.showerror("Error", f"Backup failed: {e}")

def restore_registry_key():
    """Restores a Registry Key from a binary (.dat) file using winreg.LoadKey."""
    file_path = filedialog.askopenfilename(defaultextension=".dat",
                                             filetypes=[("Registry Backup Files", "*.dat")],
                                             title="Select Backup File to Restore")
    if not file_path: return

    sub_key_name = simpledialog.askstring("Input", "Enter the NEW subkey name for the restore:")
    if not sub_key_name: return

    try:
        hkey = winreg.HKEY_LOCAL_MACHINE 
        winreg.LoadKey(hkey, sub_key_name, file_path)
        messagebox.showinfo("Success", f"Key restored successfully to:\nHKLM\\{sub_key_name}")
    except PermissionError:
        messagebox.showerror("Permission Error", "Administrator rights needed for this operation.")
    except Exception as e:
        messagebox.showerror("Error", f"Restore failed: {e}")

# --- Utility Functions (Unchanged) ---

def open_regedit():
    """Launches the native Windows Registry Editor."""
    try:
        subprocess.Popen(['regedit'])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open Registry Editor: {e}")
        
def run_clean_registry():
    """Placeholder for a Cleanup function."""
    messagebox.showinfo("Registry Cleanup", "Executing minimalist Registry cleanup routine...")


# --- Tkinter UI Class (Monochrome with Registry Analysis) ---

class RegistryTweakApp:
    def __init__(self, master):
        self.master = master
        master.title("Minimalist Registry Tweaks")
        master.geometry("1000x800") # Tăng chiều cao để chứa phần Analysis
        master.config(bg='white') 

        self.tweak_vars = {}
        
        # UI Colors (Strict Monochrome Palette)
        # Sử dụng 'SystemButtonFace' và 'SystemWindow' để thích ứng với theme mặc định của Windows
        self.BG_LIGHT = 'SystemWindow' # Thường là trắng
        self.BG_DARK = 'SystemButtonFace' # Thường là xám nhạt của nút
        self.FG_DARK = 'SystemWindowText' # Thường là đen
        self.FG_ACCENT = 'SystemWindowText'
        self.BUTTON_NORMAL = self.BG_DARK
        self.BUTTON_APPLY = 'black' # Nút nhấn chính có thể giữ màu đen

        # --- Header and Main Action Buttons ---
        header_frame = tk.Frame(master, bg=self.FG_ACCENT, height=40)
        header_frame.pack(fill='x')
        # Sử dụng màu chữ và nền đảo ngược cho thanh tiêu đề
        tk.Label(header_frame, text="REGISTRY TWEAKS", fg=self.BG_LIGHT, bg=self.FG_ACCENT,
                 font=('Segoe UI', 14, 'bold')).pack(pady=5)

        # Actions Bar
        action_bar = tk.Frame(master, bg=self.BG_DARK)
        action_bar.pack(fill='x', padx=10, pady=5)
        
        tk.Button(action_bar, text="APPLY CHANGES", command=self.apply_changes,
                  bg=self.BUTTON_APPLY, fg=self.BG_LIGHT, font=('Segoe UI', 10, 'bold'), 
                  relief='flat', padx=10).pack(side='right', padx=5)
        
        # --- Main Content Area (Grid for three columns) ---
        content_frame = tk.Frame(master, bg=self.BG_LIGHT)
        content_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        for i in range(3):
            content_frame.grid_columnconfigure(i, weight=1, uniform="group1")

        # 1. Management Section
        self.create_management_section(content_frame, 0, 0)
        
        # 2. Performance Section
        self.create_section(content_frame, "PERFORMANCE OPTIMIZATION", 0, 1, 
                            [("Speed up Windows Startup", "SpeedupBoot"),
                             ("Optimize Memory Management", "OptimizeMemory"),
                             ("Reduce Network Latency (TCP)", "ReduceTcpLatency"),
                             ("Disable Windows Search Indexing", "DisableIndexing"),
                             ("Auto-Close Hung Applications", "AutoCloseHungApps")])
        
        # 3. Security & Privacy Section
        self.create_section(content_frame, "SECURITY & PRIVACY", 0, 2, 
                            [("Disable Windows Telemetry", "DisableTelemetry"),
                             ("Disable Cortana Completely", "DisableCortana"),
                             ("Disable Location Services", "DisableLocation"),
                             ("Disable OneDrive (Policy)", "DisableOneDrive"),
                             ("Hide Email on Login Screen", "HideLoginEmail")])
        

    def create_section(self, parent, title, row, col, tweaks):
        """Creates a section (LabelFrame) with a list of Checkbuttons."""
        frame = tk.LabelFrame(parent, text=title, font=('Segoe UI', 12, 'bold'),
                              bg=self.BG_LIGHT, fg=self.FG_ACCENT, bd=1, padx=10, pady=5)
        frame.grid(row=row, column=col, sticky='nwes', padx=10, pady=10)
        
        for i, (text, var_name) in enumerate(tweaks):
            var = tk.BooleanVar()
            self.tweak_vars[var_name] = var
            # Xóa các tham số màu sắc ngoại lai trên Checkbutton
            chk = tk.Checkbutton(frame, text=text, variable=var, bg=self.BG_LIGHT, fg=self.FG_DARK,
                                 font=('Segoe UI', 10), anchor='w', relief='flat',
                                 activebackground=self.BG_LIGHT, highlightthickness=0)
            chk.grid(row=i, column=0, sticky='w', pady=3, padx=5)

    def create_management_section(self, parent, row, col):
        """Creates the full Registry Management, Backup/Restore, and Analysis section."""
        
        mgmt_frame = tk.LabelFrame(parent, text="REGISTRY MANAGEMENT", font=('Segoe UI', 12, 'bold'),
                                   bg=self.BG_LIGHT, fg=self.FG_ACCENT, bd=1, padx=10, pady=5)
        mgmt_frame.grid(row=row, column=col, sticky='nwes', padx=10, pady=10)

        # Registry Editor & Cleanup
        tk.Button(mgmt_frame, text="Open Registry Editor", command=open_regedit,
                  bg=self.BUTTON_NORMAL, fg=self.FG_DARK, font=('Segoe UI', 10), relief='flat', 
                  width=30).grid(row=0, column=0, pady=5, padx=5, sticky='w')
        
        tk.Button(mgmt_frame, text="Run Registry Cleanup", command=run_clean_registry,
                  bg=self.BUTTON_NORMAL, fg=self.FG_DARK, font=('Segoe UI', 10), relief='flat', 
                  width=30).grid(row=1, column=0, pady=5, padx=5, sticky='w')
        
        # Backup & Restore Actions
        tk.Label(mgmt_frame, text="-- Backup & Restore --", bg=self.BG_LIGHT, fg=self.FG_ACCENT,
                  font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, pady=10, sticky='w')

        tk.Button(mgmt_frame, text="Backup Registry Key", command=backup_registry_key,
                  bg=self.BUTTON_APPLY, fg=self.BG_LIGHT, font=('Segoe UI', 10, 'bold'), relief='flat', 
                  width=30).grid(row=3, column=0, pady=5, padx=5, sticky='w')
        
        tk.Button(mgmt_frame, text="Restore Key from File", command=restore_registry_key,
                  bg=self.BUTTON_APPLY, fg=self.BG_LIGHT, font=('Segoe UI', 10, 'bold'), relief='flat', 
                  width=30).grid(row=4, column=0, pady=5, padx=5, sticky='w')
        
        # ----------------------------------------------------------------------
        # NEW: Registry Analysis Section
        # ----------------------------------------------------------------------
        
        # Dữ liệu mẫu (Sample data from your image)
        analysis_data = {
            "Total Keys": "2,691,289",
            "Total Values": "8,018,796",
            "Registry Size": "302 MB",
            "Orphaned entries": "1,039",
            "Broken references": "56",
            "Empty keys": "209"
        }
        
        analysis_frame = tk.LabelFrame(mgmt_frame, text="REGISTRY ANALYSIS", font=('Segoe UI', 12, 'bold'),
                                     bg=self.BG_LIGHT, fg=self.FG_ACCENT, bd=1, padx=10, pady=5)
        analysis_frame.grid(row=5, column=0, sticky='nwes', padx=5, pady=(15, 5))

        # Hiển thị Tổng quan
        tk.Label(analysis_frame, text="-- Tổng quan --", bg=self.BG_LIGHT, fg=self.FG_ACCENT,
                  font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, columnspan=2, pady=5, sticky='w')

        # Dữ liệu Tổng quan
        data_rows = [("Tổng số keys:", analysis_data["Total Keys"]),
                     ("Tổng số values:", analysis_data["Total Values"]),
                     ("Kích thước Registry:", analysis_data["Registry Size"])]
        
        for i, (label_text, value_text) in enumerate(data_rows):
            tk.Label(analysis_frame, text=label_text, bg=self.BG_LIGHT, fg=self.FG_DARK, font=('Segoe UI', 10)).grid(row=i+1, column=0, sticky='w', padx=5)
            tk.Label(analysis_frame, text=value_text, bg=self.BG_LIGHT, fg=self.FG_DARK, font=('Segoe UI', 10, 'bold')).grid(row=i+1, column=1, sticky='e', padx=5)

        # Hiển thị Vấn đề tìm thấy
        tk.Label(analysis_frame, text="-- Vấn đề tìm thấy --", bg=self.BG_LIGHT, fg=self.FG_ACCENT,
                  font=('Segoe UI', 10, 'bold')).grid(row=len(data_rows)+1, column=0, columnspan=2, pady=(10, 5), sticky='w')

        # Dữ liệu Vấn đề
        issue_rows = [("Orphaned entries:", analysis_data["Orphaned entries"]),
                      ("Broken references:", analysis_data["Broken references"]),
                      ("Empty keys:", analysis_data["Empty keys"])]
        
        for i, (label_text, value_text) in enumerate(issue_rows):
            row_idx = len(data_rows) + 2 + i
            tk.Label(analysis_frame, text=label_text, bg=self.BG_LIGHT, fg=self.FG_DARK, font=('Segoe UI', 10)).grid(row=row_idx, column=0, sticky='w', padx=5)
            tk.Label(analysis_frame, text=value_text, bg=self.BG_LIGHT, fg=self.FG_DARK, font=('Segoe UI', 10, 'bold')).grid(row=row_idx, column=1, sticky='e', padx=5)
            
        analysis_frame.grid_columnconfigure(1, weight=1) # Cột giá trị sẽ mở rộng

        # ----------------------------------------------------------------------

    def apply_changes(self):
        """Applies all selected tweaks and provides explicit feedback on the final state."""
        
        results = []
        
        # --- Implemented Tweaks ---
        
        # 1. Reduce Network Latency (TCP)
        # Tweak is considered "ENABLED" when the checkbox is checked (set to value 1)
        is_checked = self.tweak_vars["ReduceTcpLatency"].get()
        success, messages = set_tcp_latency_tweak(is_checked)
        if success:
            results.extend(messages)
        else:
            # Add error message if the function failed
            results.extend(messages)
            
        # 2. Disable Windows Search Indexing
        # Tweak is considered "DISABLED" when the checkbox is checked (set to value 1)
        is_checked = self.tweak_vars["DisableIndexing"].get()
        if set_indexing_tweak(is_checked):
            # Report the final state: ENABLED if unchecked (False), DISABLED if checked (True)
            status = "DISABLED" if is_checked else "ENABLED"
            results.append(f"Windows Search Indexing: {status}")

        # 3. Disable Telemetry
        # Tweak is considered "DISABLED" when the checkbox is checked (set to value 0)
        is_checked = self.tweak_vars["DisableTelemetry"].get()
        if set_telemetry_tweak(is_checked):
            # Report the final state: DISABLED if checked (True), ENABLED if unchecked (False)
            status = "DISABLED" if is_checked else "ENABLED"
            results.append(f"Windows Telemetry: {status}")
            
        # --- End Implemented Tweaks ---

        if any("Error:" in r for r in results):
            # If any step failed (e.g., permission error), show error dialog.
            messagebox.showerror("Changes Applied with Errors", "Some changes failed. Check the following:\n" + "\n".join(results))
        elif results:
            # If successful, show confirmation with all results.
            messagebox.showinfo("Changes Applied Successfully", 
                                 "The following registry states have been set:\n" + "\n".join(results))
        else:
            messagebox.showinfo("No Changes Applied", "No implemented tweaks were selected or applied successfully.")

if __name__ == '__main__':
    root = tk.Tk()
    app = RegistryTweakApp(root)
    root.mainloop()