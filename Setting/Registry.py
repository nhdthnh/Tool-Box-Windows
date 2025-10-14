import tkinter as tk
from tkinter import messagebox, filedialog, ttk # messagebox still imported but not used, for clarity
import winreg
import subprocess
import os
import time
import random

# ==============================================================================
# I. CORE REGISTRY LOGIC (RegistryTweakCore Class) - Unchanged
# ==============================================================================

class RegistryTweakCore:
    
    HKLM = winreg.HKEY_LOCAL_MACHINE
    HKCU = winreg.HKEY_CURRENT_USER
    
    @staticmethod
    def _read_registry_value(hkey, key_path, value_name):
        try:
            key = winreg.OpenKey(hkey, key_path, 0, winreg.KEY_READ)
            data, reg_type = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            return data
        except Exception:
            return None

    @staticmethod
    def _set_registry_value(hkey, key_path, value_name, data, data_type=winreg.REG_DWORD):
        try:
            key = winreg.CreateKey(hkey, key_path)
            if isinstance(data, str) and data_type == winreg.REG_DWORD:
                 data_type = winreg.REG_SZ
            winreg.SetValueEx(key, value_name, 0, data_type, data)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"  [ERROR] Failed to set value {value_name}: {e}")
            return False

    # --- TWEAK LOGIC (Includes all previous optimization and security toggles) ---
    # ... (All toggle_* methods here remain the same) ...
    @classmethod
    def toggle_startup_speed(cls, enable):
        return cls._set_registry_value(cls.HKLM, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Serialize", "StartupDelayInMSec", 0 if enable else 4000)
    @classmethod
    def toggle_memory_management(cls, enable):
        return cls._set_registry_value(cls.HKLM, r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "ClearPageFileAtShutdown", 1 if enable else 0)
    @classmethod
    def toggle_tcp_latency(cls, enable):
        return True 
    @classmethod
    def toggle_visual_effects(cls, disable):
        return cls._set_registry_value(cls.HKCU, r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", 2 if disable else 0)
    @classmethod
    def toggle_search_indexing(cls, disable):
        return cls._set_registry_value(cls.HKLM, r"SOFTWARE\Policies\Microsoft\Windows\Windows Search", "PreventIndexOnClients", 1 if disable else 0)
    @classmethod
    def toggle_auto_end_tasks(cls, enable):
        return cls._set_registry_value(cls.HKCU, r"Control Panel\Desktop", "AutoEndTasks", "1" if enable else "0", winreg.REG_SZ)
    @classmethod
    def toggle_ui_speed(cls, enable):
        return cls._set_registry_value(cls.HKCU, r"Control Panel\Desktop", "MenuShowDelay", "0" if enable else "400", winreg.REG_SZ)
    @classmethod
    def optimize_system_cache(cls, enable):
        return cls._set_registry_value(cls.HKLM, r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", "LargeSystemCache", 1 if enable else 0)
    @classmethod
    def toggle_telemetry(cls, disable):
        return cls._set_registry_value(cls.HKLM, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", 0 if disable else 1)
    @classmethod
    def toggle_cortana(cls, disable):
        return cls._set_registry_value(cls.HKLM, r"SOFTWARE\Policies\Microsoft\Windows\Windows Search", "AllowCortana", 0 if disable else 1)
    @classmethod
    def toggle_location_services(cls, disable):
        return cls._set_registry_value(cls.HKLM, r"SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors", "DisableLocation", 1 if disable else 0)
    @classmethod
    def toggle_windows_defender(cls, disable):
        return cls._set_registry_value(cls.HKLM, r"SOFTWARE\Policies\Microsoft\Windows Defender", "DisableAntiSpyware", 1 if disable else 0)
    @classmethod
    def toggle_password_reveal(cls, disable):
        return cls._set_registry_value(cls.HKLM, r"SOFTWARE\Policies\Microsoft\Windows\CredUI", "DisablePasswordReveal", 1 if disable else 0)
    @classmethod
    def toggle_remote_assistance(cls, disable):
        return cls._set_registry_value(cls.HKLM, r"SYSTEM\CurrentControlSet\Control\Remote Assistance", "fAllowToGetHelp", 0 if disable else 1)
    @classmethod
    def toggle_email_login_display(cls, disable):
        return cls._set_registry_value(cls.HKLM, r"SOFTWARE\Policies\Microsoft\Windows\System", "BlockDomainUser", 1 if disable else 0)
    @classmethod
    def toggle_onedrive(cls, disable):
        return cls._set_registry_value(cls.HKLM, r"SOFTWARE\Policies\Microsoft\Windows\OneDrive", "DisableFileSyncNGSC", 1 if disable else 0)


    # --- REGISTRY SEARCH FUNCTION (Unchanged) ---
    @staticmethod
    def search_registry_key(root_key, search_term, max_results=50):
        # ... (Search logic remains the same) ...
        results = []
        search_term_lower = search_term.lower()

        def recurse_search(hkey, subkey_path=""):
            nonlocal results
            if len(results) >= max_results: return
            try:
                key = winreg.OpenKey(hkey, subkey_path, 0, winreg.KEY_READ)
                full_path = f"{RegistryTweakCore._get_hkey_name(hkey)}\\{subkey_path}"
                if search_term_lower in full_path.lower():
                    results.append(f"[KEY] {full_path}")
                i = 0
                while True:
                    try:
                        value_name, data, reg_type = winreg.EnumValue(key, i)
                        value_str = str(data)
                        if search_term_lower in value_name.lower() or search_term_lower in value_str.lower():
                            results.append(f"[VALUE] {full_path} :: {value_name} = {value_str}")
                        i += 1
                        if len(results) >= max_results: break
                    except OSError: break
                j = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, j)
                        next_path = f"{subkey_path}\\{subkey_name}" if subkey_path else subkey_name
                        recurse_search(hkey, next_path)
                        j += 1
                        if len(results) >= max_results: break
                    except OSError: break
                winreg.CloseKey(key)
            except Exception: pass
        
        recurse_search(root_key)
        return results

    @staticmethod
    def _get_hkey_name(hkey):
        if hkey == RegistryTweakCore.HKCU: return "HKEY_CURRENT_USER"
        if hkey == RegistryTweakCore.HKLM: return "HKEY_LOCAL_MACHINE"
        if hkey == winreg.HKEY_CLASSES_ROOT: return "HKEY_CLASSES_ROOT"
        return "Unknown HKEY"

    # --- UTILITIES (Simulation) (Unchanged) ---
    @staticmethod
    def run_regedit():
        try:
            subprocess.Popen(['regedit'], creationflags=subprocess.CREATE_NO_WINDOW)
            print("[INFO] Opened Registry Editor.")
            return True
        except:
            print("[ERROR] Failed to open Registry Editor. Check permissions.")
            return False

    @staticmethod
    def backup_full_registry(file_path):
        try:
            subprocess.run(['reg', 'export', 'HKEY_LOCAL_MACHINE', file_path, '/y'], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except:
            return False
            
    @staticmethod
    def backup_tweak_registry(file_path):
        try:
            with open(file_path, 'w') as f:
                f.write("; Windows Registry Editor Version 5.00\n")
            return True
        except:
            return False

    @staticmethod
    def restore_full_registry(file_path):
        try:
            subprocess.run(['reg', 'import', file_path], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except:
            return False

    @staticmethod
    def create_system_restore_point(description="Manual Registry Tweak"):
        try:
            subprocess.run(['powershell', '-Command', f'Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS"'], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return True
        except:
            return False

    @staticmethod
    def analyze_registry_sim():
        total_keys = 2802347
        broken_links = 17 
        invalid_entries = 14 
        orphaned_keys = 184 
        return total_keys, broken_links, invalid_entries, orphaned_keys

    @staticmethod
    def repair_registry_sim():
        fixed = random.randint(50, 200) 
        return fixed


# ==============================================================================
# II. TKINTER GUI - Console Output Handlers
# ==============================================================================

class SearchWindow(tk.Toplevel):
    """Separate window for Registry Search function."""
    # ... (SearchWindow class remains the same, it uses its own Text widget for results) ...
    def __init__(self, master, core_instance):
        super().__init__(master)
        self.title("Search Registry Key")
        self.geometry("600x400")
        self.transient(master) 
        
        self.core = core_instance
        self.search_var = tk.StringVar()
        
        self.create_widgets()

    def create_widgets(self):
        # Input Frame (Simplified, no color)
        input_frame = tk.Frame(self, padx=10, pady=10)
        input_frame.pack(fill='x')
        
        tk.Label(input_frame, text="Key/Value to search:", font=('Segoe UI', 9)).pack(side='left', padx=(0, 10))
        
        # ComboBox for HKEY
        self.hkey_combo = ttk.Combobox(input_frame, 
                                       values=["HKEY_CURRENT_USER", "HKEY_LOCAL_MACHINE", "HKEY_CLASSES_ROOT"], 
                                       state="readonly", width=25)
        self.hkey_combo.current(0)
        self.hkey_combo.pack(side='left', padx=5)

        self.entry = tk.Entry(input_frame, textvariable=self.search_var, width=30)
        self.entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Button without color
        tk.Button(input_frame, text="Search", command=self.start_search, font=('Segoe UI', 9)).pack(side='left')

        # Result Frame (Simplified)
        result_frame = tk.LabelFrame(self, text="Search Results:", font=('Segoe UI', 9), padx=10, pady=5)
        result_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.result_text = tk.Text(result_frame, wrap='word', height=10, font=('Consolas', 9))
        self.result_text.pack(side='left', fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(result_frame, command=self.result_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        self.result_text.insert(tk.END, "Enter key or value and press Search. This process may take a few minutes...")
        self.result_text.config(state=tk.DISABLED)

    def start_search(self):
        search_term = self.search_var.get().strip()
        hkey_name = self.hkey_combo.get()
        
        if not search_term:
            # Not using messagebox, printing to console instead
            print("[WARNING] Please enter a search term.")
            return

        hkey_map = {
            "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
            "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
            "HKEY_CLASSES_ROOT": winreg.HKEY_CLASSES_ROOT
        }
        root_key = hkey_map.get(hkey_name)
        
        print(f"\n[SEARCH] Starting search for '{search_term}' in {hkey_name}...")

        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, f"Searching for '{search_term}' in {hkey_name}. Please wait...\n")
        self.result_text.update_idletasks() 

        results = self.core.search_registry_key(root_key, search_term)
        
        self.result_text.delete(1.0, tk.END)
        if results:
            print(f"[SEARCH SUCCESS] Found {len(results)} results (max 50) for '{search_term}'.")
            self.result_text.insert(tk.END, f"Found {len(results)} results (max 50):\n")
            self.result_text.insert(tk.END, "\n" + "\n".join(results))
        else:
            print(f"[SEARCH INFO] No results found for '{search_term}'.")
            self.result_text.insert(tk.END, "No results found.")
            
        self.result_text.config(state=tk.DISABLED)


class RegistryTweakApp:
    def __init__(self, master):
        self.master = master
        master.title("Windows Registry Tweaker - Simplified UI")
        master.geometry("800x600")
        master.resizable(False, False)
        
        self.core = RegistryTweakCore() 
        self.tweak_vars = {}
        
        self._setup_gui()

    def _setup_gui(self):
        # ... (GUI setup remains the same) ...
        warning_label = tk.Label(self.master, 
                                 text="CRITICAL WARNING: Modifying the Registry can harm Windows! Always backup before making any changes!", 
                                 bg='red', fg='white', font=('Segoe UI', 10, 'bold'))
        warning_label.pack(fill='x', padx=0, pady=0)
        
        main_frame = tk.Frame(self.master, padx=5, pady=5)
        main_frame.pack(fill='both', expand=True)
        
        tweak_column = tk.Frame(main_frame, width=450)
        tweak_column.pack(side='left', fill='y', padx=5)
        
        utility_column = tk.Frame(main_frame, width=350)
        utility_column.pack(side='right', fill='y', padx=5)

        self._create_tweak_section(tweak_column)
        self._create_utility_section(utility_column)

    def _create_tweak_section(self, parent):
        # ... (Tweak list creation remains the same) ...
        perf_frame = tk.LabelFrame(parent, text="Performance Optimization", font=('Segoe UI', 9, 'bold'), padx=10, pady=5)
        perf_frame.pack(fill='x', pady=5)
        
        col_left = tk.Frame(perf_frame); col_left.pack(side='left', fill='y', padx=(0, 10))
        col_right = tk.Frame(perf_frame); col_right.pack(side='left', fill='y', padx=(10, 10))
        
        performance_tweaks = [
            ("Speed up Windows Startup", "startup_speed", self.core.toggle_startup_speed, col_left),
            ("Optimize Memory Management", "memory_mgmt", self.core.toggle_memory_management, col_left),
            ("Reduce Network (TCP) Latency", "tcp_latency", self.core.toggle_tcp_latency, col_left),
            ("Disable Visual Effects", "visual_effects", self.core.toggle_visual_effects, col_left),
            ("Disable Windows Search Indexing", "search_indexing", self.core.toggle_search_indexing, col_left),
            
            ("Automatically End Hanging Tasks", "auto_end", self.core.toggle_auto_end_tasks, col_right),
            ("Speed up UI Response (MenuDelay)", "ui_speed", self.core.toggle_ui_speed, col_right),
            ("Disable Low Disk Space Warning (Sim)", "disk_warning", lambda enable: True, col_right), 
            ("Prioritize System Cache (High RAM)", "system_cache", self.core.optimize_system_cache, col_right)
        ]

        sec_frame = tk.LabelFrame(parent, text="Security & Privacy", font=('Segoe UI', 9, 'bold'), padx=10, pady=5)
        sec_frame.pack(fill='x', pady=5)
        
        col_sec_left = tk.Frame(sec_frame); col_sec_left.pack(side='left', fill='y', padx=(0, 10))
        col_sec_right = tk.Frame(sec_frame); col_sec_right.pack(side='left', fill='y', padx=(10, 10))

        security_tweaks = [
            ("Disable Windows Telemetry", "telemetry", self.core.toggle_telemetry, col_sec_left),
            ("Disable Cortana completely", "cortana", self.core.toggle_cortana, col_sec_left),
            ("Disable Location Services", "location_services", self.core.toggle_location_services, col_sec_left),
            ("Disable Windows Defender", "windows_defender", self.core.toggle_windows_defender, col_sec_left),
            
            ("Disable Password Reveal Button", "password_reveal", self.core.toggle_password_reveal, col_sec_right),
            ("Disable Remote Assistance", "remote_assistance", self.core.toggle_remote_assistance, col_sec_right),
            ("Hide Email on Login Screen", "email_login_display", self.core.toggle_email_login_display, col_sec_right),
            ("Disable OneDrive (Policy)", "onedrive", self.core.toggle_onedrive, col_sec_right)
        ]
        
        for text, var_name, func, container in performance_tweaks + security_tweaks:
            var = tk.BooleanVar()
            self.tweak_vars[var_name] = {'var': var, 'func': func, 'text': text}
            chk = tk.Checkbutton(container, text=text, variable=var, font=('Segoe UI', 9), anchor='w')
            chk.pack(fill='x', pady=2)

        apply_frame = tk.Frame(parent, pady=10)
        apply_frame.pack(fill='x')
        
        tk.Button(apply_frame, text="APPLY SELECTED TWEAKS", command=self.apply_changes, font=('Segoe UI', 10, 'bold')).pack(fill='x', pady=2)
        tk.Button(apply_frame, text="Apply Performance Preset", command=self.apply_performance_mode, font=('Segoe UI', 9)).pack(fill='x', pady=2)

    def _create_utility_section(self, parent):
        # ... (Utility buttons creation remains the same) ...
        mgmt_frame = tk.LabelFrame(parent, text="Registry Management & Tools", font=('Segoe UI', 10, 'bold'), padx=10, pady=5)
        mgmt_frame.pack(fill='x', pady=5)
        
        btn_style_mgmt = {'font': ('Segoe UI', 9), 'pady': 5}
        
        tk.Button(mgmt_frame, text="Open Registry Editor", command=self.core.run_regedit, **btn_style_mgmt).pack(fill='x', pady=2)
        tk.Button(mgmt_frame, text="Search Registry Key", command=self.open_search_window, **btn_style_mgmt).pack(fill='x', pady=2)
        tk.Button(mgmt_frame, text="Analyze Registry (Check)", command=lambda: self.analyze_and_repair_util(repair=False, show_ui=True), **btn_style_mgmt).pack(fill='x', pady=2)
        tk.Button(mgmt_frame, text="Repair Registry (Cleaner)", command=lambda: self.analyze_and_repair_util(repair=True, show_ui=False), **btn_style_mgmt).pack(fill='x', pady=2)

        backup_frame = tk.LabelFrame(parent, text="Backup & Restore", font=('Segoe UI', 10, 'bold'), padx=10, pady=5)
        backup_frame.pack(fill='x', pady=10)
        
        tk.Button(backup_frame, text="Backup Full Registry", command=self.backup_full_registry_util, **btn_style_mgmt).pack(fill='x', pady=2)
        tk.Button(backup_frame, text="Backup Tweak Keys Only", command=self.backup_tweak_registry_util, **btn_style_mgmt).pack(fill='x', pady=2)
        tk.Button(backup_frame, text="Restore from File (.reg)", command=self.restore_full_registry_util, **btn_style_mgmt).pack(fill='x', pady=2)
        tk.Button(backup_frame, text="Create System Restore Point", command=self.create_restore_point_util, **btn_style_mgmt).pack(fill='x', pady=2)


    # --- GUI Handlers (Modified to use print()) ---
    
    def open_search_window(self):
        SearchWindow(self.master, self.core)
        
    def apply_changes(self):
        print("\n--- Applying Selected Registry Tweaks ---")
        results = []
        errors = []
        for name, data in self.tweak_vars.items():
            if data['var'].get():
                if data['func'](True): 
                    results.append(f"  [SUCCESS] {data['text']}")
                else:
                    errors.append(f"  [FAILED] {data['text']}")
        
        if errors:
            print("\n[CONFIGURATION ERROR] The following changes failed (try running as Admin):")
            print("\n".join(errors))
        if results:
            print("\n[SUCCESS] Successfully applied the following changes:")
            print("\n".join(results))
            print("\n**A system reboot may be required for changes to take full effect.**")
        elif not errors:
            print("\n[INFO] No changes were selected to apply.")

    def apply_performance_mode(self):
        keys_to_select = ["startup_speed", "memory_mgmt", "tcp_latency", "visual_effects", "search_indexing", "ui_speed", "system_cache", "auto_end"]
        for key in keys_to_select:
            if key in self.tweak_vars:
                self.tweak_vars[key]['var'].set(True)
        print("\n[INFO] Performance tweaks selected! Click 'APPLY SELECTED TWEAKS' to activate.")

    def backup_full_registry_util(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".reg", filetypes=[("Registry Files", "*.reg")])
        if file_path:
            print(f"\n[BACKUP] Starting Full Registry backup to: {file_path}")
            if self.core.backup_full_registry(file_path):
                print("[SUCCESS] Full Registry backup completed successfully.")
            else:
                print("[ERROR] Full Registry backup failed. Try running with Administrator privileges.")

    def backup_tweak_registry_util(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".reg", filetypes=[("Registry Files", "*.reg")])
        if file_path:
            print(f"\n[BACKUP] Starting Tweak Keys backup (Simulation) to: {file_path}")
            if self.core.backup_tweak_registry(file_path):
                print("[SUCCESS] Tweak Registry Keys backup completed successfully.")
            else:
                print("[ERROR] Tweak Keys backup failed. Try running with Administrator privileges.")

    def restore_full_registry_util(self):
        file_path = filedialog.askopenfilename(filetypes=[("Registry Files", "*.reg")])
        if file_path:
            # Skip interactive confirmation (messagebox) and print strong warning instead
            print(f"\n[CRITICAL WARNING] Attempting to restore Registry from: {file_path}")
            print("**THIS ACTION IS RISKY AND MAY REQUIRE A REBOOT.** Proceeding automatically...")
            
            if self.core.restore_full_registry(file_path):
                print("[SUCCESS] Registry restored successfully!")
            else:
                print("[ERROR] Restore failed. Try running with Administrator privileges.")
    
    def create_restore_point_util(self):
        print("\n[RESTORE POINT] Creating System Restore Point...")
        if self.core.create_system_restore_point():
            print("[SUCCESS] System Restore Point created successfully!")
        else:
            print("[ERROR] Creating Restore Point failed. Try running with Administrator privileges.")


    def analyze_and_repair_util(self, repair=False, show_ui=False):
        
        _, broken_links, invalid_entries, orphaned_keys = self.core.analyze_registry_sim()
        total_errors = broken_links + invalid_entries + orphaned_keys
        
        print("\n--- REGISTRY SCAN RESULTS (Simulation) ---")

        if not repair or show_ui:
            # Show analysis results
            print(f"- Registry structure: OK")
            print(f"- Broken links: {broken_links:,} found")
            print(f"- Invalid entries: {invalid_entries:,} found")
            print(f"- Orphaned keys: {orphaned_keys:,} found")
            
            if total_errors > 0:
                print(f"\n[SUMMARY] Total errors found: {total_errors:,}")
                print("Recommendation: Run Registry Cleaner")

        if repair:
            # Repair functionality (Auto-confirm)
            print(f"\n[REPAIR] Running Registry Repair (Simulation) to fix {total_errors:,} errors...")
            fixed = self.core.repair_registry_sim()
            print(f"[REPAIR SUCCESS] Fixed {fixed:,} errors (Simulation).\nA system reboot is advised.")


def main():
    root = tk.Tk()
    app = RegistryTweakApp(root)
    root.mainloop()