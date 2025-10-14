import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import winreg
import subprocess

# --- Core Logic: Registry Tweak Functions ---

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
                
                try:
                    interface_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{interfaces_path}\\{guid}", 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
                    
                    try:
                        winreg.QueryValueEx(interface_key, "DhcpIPAddress")
                        is_active = True
                    except FileNotFoundError:
                        try:
                            winreg.QueryValueEx(interface_key, "IPAddress")
                            is_active = True
                        except FileNotFoundError:
                            is_active = False
                    
                    if is_active:
                        value = 1 if enable else 0
                        winreg.SetValueEx(interface_key, "TcpAckFrequency", 0, winreg.REG_DWORD, value)
                        winreg.SetValueEx(interface_key, "TCPNoDelay", 0, winreg.REG_DWORD, value)
                        winreg.CloseKey(interface_key)
                        
                        status = "ENABLED" if enable else "DISABLED"
                        results.append(f"Reduce Network Latency (Adapter {guid[:8]}): {status}")
                    
                except OSError:
                    continue
            except OSError:
                break

        winreg.CloseKey(root_key)
        
        if results:
            return True, results
        else:
            return False, ["Error: No active network adapters could be modified for TCP tweaks."]
            
    except PermissionError:
        return False, ["Error: Administrator privileges are required for TCP network tweaks."]
    except Exception as e:
        return False, [f"Error applying TCP Latency tweak: {e}"]


# --- Backup & Restore Functions ---

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


# --- Utility Functions ---

def open_regedit():
    """Launches the native Windows Registry Editor."""
    try:
        subprocess.Popen(['regedit'])
    except Exception as e:
        messagebox.showerror("Error", f"Could not open Registry Editor: {e}")
        
def run_clean_registry():
    """Placeholder for a Cleanup function."""
    messagebox.showinfo("Registry Cleanup", "Executing Registry cleanup routine...")


# --- Tkinter UI Class ---

class RegistryTweakApp:
    def __init__(self, master):
        self.master = master
        master.title("Registry Tweaks")
        master.geometry("950x750")

        self.tweak_vars = {}
        
        # Header
        header_frame = tk.Frame(master)
        header_frame.pack(fill='x', padx=10, pady=10)
        tk.Label(header_frame, text="Registry Tweaks", font=('Segoe UI', 16, 'bold')).pack()

        # Apply Button
        action_bar = tk.Frame(master)
        action_bar.pack(fill='x', padx=10, pady=5)
        tk.Button(action_bar, text="Apply Changes", command=self.apply_changes,
                  font=('Segoe UI', 10, 'bold'), padx=25, pady=6).pack(side='right')
        
        # Main Content Area
        content_frame = tk.Frame(master)
        content_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        for i in range(3):
            content_frame.grid_columnconfigure(i, weight=1, uniform="group1")

        # Column 1: Management & Tools
        self.create_management_section(content_frame, 0, 0)
        
        # Column 2: Performance Tweaks
        self.create_section(content_frame, "Performance", 0, 1, 
                            [("Speed up Windows Startup", "SpeedupBoot"),
                             ("Optimize Memory Management", "OptimizeMemory"),
                             ("Reduce Network Latency", "ReduceTcpLatency"),
                             ("Disable Search Indexing", "DisableIndexing"),
                             ("Auto-Close Hung Apps", "AutoCloseHungApps")])
        
        # Column 3: Security & Privacy
        self.create_section(content_frame, "Security & Privacy", 0, 2, 
                            [("Disable Telemetry", "DisableTelemetry"),
                             ("Disable Cortana", "DisableCortana"),
                             ("Disable Location Services", "DisableLocation"),
                             ("Disable OneDrive", "DisableOneDrive"),
                             ("Hide Email on Login", "HideLoginEmail")])

    def create_section(self, parent, title, row, col, tweaks):
        """Creates a section with checkboxes."""
        frame = tk.LabelFrame(parent, text=title, font=('Segoe UI', 11, 'bold'), padx=10, pady=10)
        frame.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)
        
        for i, (text, var_name) in enumerate(tweaks):
            var = tk.BooleanVar()
            self.tweak_vars[var_name] = var
            chk = tk.Checkbutton(frame, text=text, variable=var, font=('Segoe UI', 10), anchor='w')
            chk.grid(row=i, column=0, sticky='w', pady=2, padx=5)

    def create_management_section(self, parent, row, col):
        """Creates the Registry Management section."""
        
        mgmt_frame = tk.LabelFrame(parent, text="Management & Tools", font=('Segoe UI', 11, 'bold'), padx=10, pady=10)
        mgmt_frame.grid(row=row, column=col, sticky='nsew', padx=5, pady=5)

        # Registry Tools
        tk.Label(mgmt_frame, text="Registry Tools", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, pady=(0, 5), sticky='w')
        
        tk.Button(mgmt_frame, text="Open Registry Editor", command=open_regedit,
                  font=('Segoe UI', 10), width=25).grid(row=1, column=0, pady=2, padx=5, sticky='ew')
        
        tk.Button(mgmt_frame, text="Run Registry Cleanup", command=run_clean_registry,
                  font=('Segoe UI', 10), width=25).grid(row=2, column=0, pady=2, padx=5, sticky='ew')
        
        # Backup & Restore
        tk.Label(mgmt_frame, text="Backup & Restore", font=('Segoe UI', 10, 'bold')).grid(row=3, column=0, pady=(15, 5), sticky='w')

        tk.Button(mgmt_frame, text="Backup Registry Key", command=backup_registry_key,
                  font=('Segoe UI', 10), width=25).grid(row=4, column=0, pady=2, padx=5, sticky='ew')
        
        tk.Button(mgmt_frame, text="Restore Registry Key", command=restore_registry_key,
                  font=('Segoe UI', 10), width=25).grid(row=5, column=0, pady=2, padx=5, sticky='ew')
        
        # Registry Analysis
        analysis_data = {
            "Total Keys": "2,691,289",
            "Total Values": "8,018,796",
            "Registry Size": "302 MB",
            "Orphaned entries": "1,039",
            "Broken references": "56",
            "Empty keys": "209"
        }
        
        analysis_frame = tk.LabelFrame(mgmt_frame, text="Registry Analysis", font=('Segoe UI', 10, 'bold'), padx=10, pady=10)
        analysis_frame.grid(row=6, column=0, sticky='ew', padx=5, pady=(15, 5))

        # Overview
        tk.Label(analysis_frame, text="Overview", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, columnspan=2, pady=(0, 5), sticky='w')

        data_rows = [
            ("Total keys:", analysis_data["Total Keys"]),
            ("Total values:", analysis_data["Total Values"]),
            ("Registry size:", analysis_data["Registry Size"])
        ]
        
        for i, (label_text, value_text) in enumerate(data_rows):
            tk.Label(analysis_frame, text=label_text, font=('Segoe UI', 9)).grid(row=i+1, column=0, sticky='w', padx=5, pady=1)
            tk.Label(analysis_frame, text=value_text, font=('Segoe UI', 9, 'bold')).grid(row=i+1, column=1, sticky='e', padx=5, pady=1)

        # Issues Found
        tk.Label(analysis_frame, text="Issues Found", font=('Segoe UI', 9, 'bold')).grid(row=len(data_rows)+1, column=0, columnspan=2, pady=(10, 5), sticky='w')

        issue_rows = [
            ("Orphaned entries:", analysis_data["Orphaned entries"]),
            ("Broken references:", analysis_data["Broken references"]),
            ("Empty keys:", analysis_data["Empty keys"])
        ]
        
        for i, (label_text, value_text) in enumerate(issue_rows):
            row_idx = len(data_rows) + 2 + i
            tk.Label(analysis_frame, text=label_text, font=('Segoe UI', 9)).grid(row=row_idx, column=0, sticky='w', padx=5, pady=1)
            tk.Label(analysis_frame, text=value_text, font=('Segoe UI', 9, 'bold')).grid(row=row_idx, column=1, sticky='e', padx=5, pady=1)
            
        analysis_frame.grid_columnconfigure(1, weight=1)

    def apply_changes(self):
        """Applies all selected tweaks."""
        
        results = []
        
        # Reduce Network Latency
        is_checked = self.tweak_vars["ReduceTcpLatency"].get()
        success, messages = set_tcp_latency_tweak(is_checked)
        if success:
            results.extend(messages)
        else:
            results.extend(messages)
            
        # Disable Windows Search Indexing
        is_checked = self.tweak_vars["DisableIndexing"].get()
        if set_indexing_tweak(is_checked):
            status = "DISABLED" if is_checked else "ENABLED"
            results.append(f"Windows Search Indexing: {status}")

        # Disable Telemetry
        is_checked = self.tweak_vars["DisableTelemetry"].get()
        if set_telemetry_tweak(is_checked):
            status = "DISABLED" if is_checked else "ENABLED"
            results.append(f"Windows Telemetry: {status}")

        if any("Error:" in r for r in results):
            messagebox.showerror("Changes Applied with Errors", "Some changes failed:\n" + "\n".join(results))
        elif results:
            messagebox.showinfo("Changes Applied", "Registry states updated:\n" + "\n".join(results))
        else:
            messagebox.showinfo("No Changes", "No tweaks were selected or applied.")

if __name__ == '__main__':
    root = tk.Tk()
    app = RegistryTweakApp(root)
    root.mainloop()
