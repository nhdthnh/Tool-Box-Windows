import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import ctypes
import winreg
import subprocess

# --- 1. System/Registry Logic & Admin Check ---

HKEY = winreg.HKEY_CLASSES_ROOT

def is_admin():
    """Checks if the script is running with Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def restart_as_admin():
    """Restarts the current script with Administrator privileges."""
    script = os.path.abspath(sys.argv[0])
    # Ensure correct executable is used for restart
    executable = 'python.exe' if os.path.basename(sys.executable).lower() == 'pythonw.exe' else sys.executable
    params = ' '.join(sys.argv)
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
        sys.exit(0)
    except Exception as e:
        print(f"Could not restart as Administrator. Error: {e}", file=sys.stderr)
        sys.exit(1)

def restart_explorer():
    """Restarts the Windows Explorer process to apply changes immediately."""
    try:
        # 1. Kill explorer.exe
        subprocess.run(['taskkill', '/f', '/im', 'explorer.exe'], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        # 2. Start explorer.exe
        subprocess.Popen(['explorer.exe'], creationflags=subprocess.CREATE_NEW_CONSOLE)
        return True
    except Exception:
        return False


def registry_key_exists(key_path):
    """Checks if a registry key path exists."""
    try:
        key = winreg.OpenKey(HKEY, key_path, 0, winreg.KEY_READ)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

def add_registry_key(key_path, value_name, command=None):
    """Creates a key and command subkey."""
    try:
        key = winreg.CreateKey(HKEY, key_path)
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, value_name)
        winreg.CloseKey(key)

        if command:
            command_key = winreg.CreateKey(HKEY, f"{key_path}\\command")
            winreg.SetValueEx(command_key, "", 0, winreg.REG_SZ, command)
            winreg.CloseKey(command_key)
        
        return True
    except Exception:
        return False

def remove_registry_key(key_path):
    """Deletes a registry key and its subkeys recursively (if 'command' exists)."""
    try:
        try:
            winreg.DeleteKey(HKEY, f"{key_path}\\command")
        except FileNotFoundError:
            pass
        winreg.DeleteKey(HKEY, key_path)
        return True
    except FileNotFoundError:
        return True 
    except Exception:
        return False

# --- FULL REGISTRY CONFIGURATION MAPPING (27 Features) ---
# Each item now includes 'key_path' for Auto-Select logic.

REGISTRY_CONFIG = {
    # --- I. File & Folder Utilities (File Menu: HKEY_CLASSES_ROOT\*\shell)
    "copy_path": {"key_path": r"*\shell\01_CopyAsPath", "add": lambda: add_registry_key(r"*\shell\01_CopyAsPath", "Copy File Path", command='cmd.exe /c echo "%1" | clip'), "remove": lambda: remove_registry_key(r"*\shell\01_CopyAsPath")},
    "take_ownership": {"key_path": r"*\shell\02_TakeOwnership", "add": lambda: add_registry_key(r"*\shell\02_TakeOwnership", "Take Ownership", command='PowerShell -Command "Start-Process cmd -Verb runas -ArgumentList \'/c takeown /f \\\"%1\\\" /r /d y & icacls \\\"%1\\\" /grant administrators:F /t\'"'), "remove": lambda: remove_registry_key(r"*\shell\02_TakeOwnership")},
    "check_hash": {"key_path": r"*\shell\03_CheckHash", "add": lambda: add_registry_key(r"*\shell\03_CheckHash", "Check File Hash", command='PowerShell -Command "Get-FileHash -Path \\\"%1\\\" | Format-List | Out-GridView -Title \"File Hash\""'), "remove": lambda: remove_registry_key(r"*\shell\03_CheckHash")},
    "block_fw": {"key_path": r"*\shell\04_BlockInFirewall", "add": lambda: add_registry_key(r"*\shell\04_BlockInFirewall", "Block in Firewall", command='netsh advfirewall firewall add rule name="BlockedApp_%1" dir=out program="\"%1\"" action=block'), "remove": lambda: remove_registry_key(r"*\shell\04_BlockInFirewall")},
    "change_attr": {"key_path": r"*\shell\05_ChangeFileAttributes", "add": lambda: add_registry_key(r"*\shell\05_ChangeFileAttributes", "Change File Attributes", command='attrib -h -r -s "%1"'), "remove": lambda: remove_registry_key(r"*\shell\05_ChangeFileAttributes")},
    "defender_scan": {"key_path": r"*\shell\06_QuickScanDefender", "add": lambda: add_registry_key(r"*\shell\06_QuickScanDefender", "Quick Scan with Defender", command='"C:\\Program Files\\Windows Defender\\MpCmdRun.exe" -scan -scantype 3 -file "%1"'), "remove": lambda: remove_registry_key(r"*\shell\06_QuickScanDefender")},
    "copy_to_folder": {"key_path": r"*\shell\07_CopyToFolder", "add": lambda: add_registry_key(r"*\shell\07_CopyToFolder", "Copy To Folder...", command='PowerShell -Command "Start-Process cmd -Verb runas -ArgumentList \'/c start explorer /select,\"\%\%1\"\';"'), "remove": lambda: remove_registry_key(r"*\shell\07_CopyToFolder")},
    "move_to_folder": {"key_path": r"*\shell\08_MoveToFolder", "add": lambda: add_registry_key(r"*\shell\08_MoveToFolder", "Move To Folder...", command='PowerShell -Command "Start-Process cmd -Verb runas -ArgumentList \'/c start explorer /select,\"\%\%1\"\';"'), "remove": lambda: remove_registry_key(r"*\shell\08_MoveToFolder")},
    "open_npp": {"key_path": r"*\shell\09_OpenNotepad++", "add": lambda: add_registry_key(r"*\shell\09_OpenNotepad++", "Open with Notepad++", command='"C:\\Program Files\\Notepad++\\notepad++.exe" "%1"'), "remove": lambda: remove_registry_key(r"*\shell\09_OpenNotepad++")},
    "add_startup": {
        "key_path": r"*\shell\10_AddToStartup",
        "add": lambda: add_registry_key(
            r"*\shell\10_AddToStartup",
            "Add to Startup Folder",
            command='PowerShell -Command "Start-Process cmd -Verb runas -ArgumentList \'/c copy \\\"%1\\\" \\\"%USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\\\\';"'
        ),
        "remove": lambda: remove_registry_key(r"*\shell\10_AddToStartup")
    },
    
    "open_ps": {
        "key_path": r"Directory\Background\shell\13_OpenPSHere",
        "add": lambda: add_registry_key(
            r"Directory\Background\shell\13_OpenPSHere",
            "Open PowerShell Here",
            command='PowerShell.exe -NoExit -Command "Set-Location -Path \'%V\'"'
        ),
        "remove": lambda: remove_registry_key(r"Directory\Background\shell\13_OpenPSHere")
    },
    # Added Windows Terminal / Command Prompt entries
    "open_wst": {"key_path": r"Directory\Background\shell\WindowsTerminal", "add": lambda: add_registry_key(r"Directory\Background\shell\WindowsTerminal", "Open in Windows Terminal", command='wt.exe -d "%V"'), "remove": lambda: remove_registry_key(r"Directory\Background\shell\WindowsTerminal")},
    "open_cmd": {"key_path": r"Directory\Background\shell\CommandPromptHere", "add": lambda: add_registry_key(r"Directory\Background\shell\CommandPromptHere", "Open Command Prompt Here", command='cmd.exe /k cd /d "%V"'), "remove": lambda: remove_registry_key(r"Directory\Background\shell\CommandPromptHere")},
    "god_mode": {"key_path": r"Directory\Background\shell\14_GodMode", "add": lambda: add_registry_key(r"Directory\Background\shell\14_GodMode", "God Mode", command='explorer shell:::{ED7BA470-8E54-465E-825C-99712043E01C}'), "remove": lambda: remove_registry_key(r"Directory\Background\shell\14_GodMode")},
    "empty_clipboard": {"key_path": r"Directory\Background\shell\15_EmptyClipboard", "add": lambda: add_registry_key(r"Directory\Background\shell\15_EmptyClipboard", "Clean up Clipboard", command='PowerShell -Command "Clear-Clipboard"'), "remove": lambda: remove_registry_key(r"Directory\Background\shell\15_EmptyClipboard")},
    "compact_folder": {"key_path": r"Directory\Background\shell\16_CompactFolder", "add": lambda: add_registry_key(r"Directory\Background\shell\16_CompactFolder", "Compact Folder (NTFS)", command='compact /c /s /i /q "%V"'), "remove": lambda: remove_registry_key(r"Directory\Background\shell\16_CompactFolder")},
    "task_mgr": {"key_path": r"Directory\Background\shell\17_TaskManager", "add": lambda: add_registry_key(r"Directory\Background\shell\17_TaskManager", "Task Manager", command='taskmgr.exe'), "remove": lambda: remove_registry_key(r"Directory\Background\shell\17_TaskManager")},
    "control_panel": {"key_path": r"Directory\Background\shell\18_ControlPanel", "add": lambda: add_registry_key(r"Directory\Background\shell\18_ControlPanel", "Control Panel", command='control.exe'), "remove": lambda: remove_registry_key(r"Directory\Background\shell\18_ControlPanel")},
    "services_msc": {"key_path": r"Directory\Background\shell\19_Services", "add": lambda: add_registry_key(r"Directory\Background\shell\19_Services", "Services", command='services.msc'), "remove": lambda: remove_registry_key(r"Directory\Background\shell\19_Services")},
    
    # --- III. Menu Cleanup (Remove/Disable existing items)
    # The 'remove' functions for Cleanup items are placeholders for complex restoration, as restoring original system handlers is difficult.
    "remove_share": {"key_path": r"*\shellex\ContextMenuHandlers\Sharing", "add": lambda: remove_registry_key(r"*\shellex\ContextMenuHandlers\Sharing"), "remove": lambda: False},
    "remove_cast": {"key_path": r"*\shellex\ContextMenuHandlers\CastToDevice", "add": lambda: remove_registry_key(r"*\shellex\ContextMenuHandlers\CastToDevice"), "remove": lambda: False},
    "remove_paint3d": {"key_path": r"*\shell\3D Edit", "add": lambda: remove_registry_key(r"*\shell\3D Edit"), "remove": lambda: False},
    "remove_3dprint": {"key_path": r"*\shell\3D Print", "add": lambda: remove_registry_key(r"*\shell\3D Print"), "remove": lambda: False},
    "remove_photos": {"key_path": r"*\shell\EditWithPhotos", "add": lambda: remove_registry_key(r"*\shell\EditWithPhotos"), "remove": lambda: False},
    "remove_clipchamp": {"key_path": r"*\shell\EditWithClipchamp", "add": lambda: remove_registry_key(r"*\shell\EditWithClipchamp"), "remove": lambda: False},
    "remove_wst_menu": {"key_path": r"Directory\Background\shell\WindowsTerminal", "add": lambda: remove_registry_key(r"Directory\Background\shell\WindowsTerminal"), "remove": lambda: False},
    "remove_vlc": {"key_path": r"Directory\shell\AddToVLCPlaylist", "add": lambda: remove_registry_key(r"Directory\shell\AddToVLCPlaylist"), "remove": lambda: False},
    "remove_winrar": {"key_path": r"*\shell\WinRAR", "add": lambda: remove_registry_key(r"*\shell\WinRAR"), "remove": lambda: False},
}

# --- 2. GUI Application (Tkinter) ---

class ContextMenuConfigurator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Windows Context Menu Tool")
        self.resizable(False, False)
        
        style = ttk.Style(self)
        style.theme_use('default')
        style.configure('TCheckbutton', font=('Arial', 10), background='SystemButtonFace', foreground='black')
        style.configure('TFrame', background='SystemButtonFace')
        
        self.config_vars = {}
        self.create_widgets()

        if is_admin():
            self.load_current_registry_status()

    
    def load_current_registry_status(self):
        """Reads the Windows Registry and sets the state of the Checkbuttons (Auto-Select)."""
        for key, (var, name) in self.config_vars.items():
            config = REGISTRY_CONFIG.get(key)
            if not config or 'key_path' not in config:
                continue
            
            is_cleanup_item = key.startswith("remove_")
            key_exists = registry_key_exists(config['key_path'])
            
            if is_cleanup_item:
                # Cleanup: CHECKED = Key NOT EXISTS (Item is removed/disabled)
                if not key_exists:
                    var.set(True) 
                else:
                    var.set(False) 
            else:
                # Add Feature: CHECKED = Key EXISTS (Item is enabled/added)
                if key_exists:
                    var.set(True)
                else:
                    var.set(False)
                    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.pack(fill="both", expand=True)
        
        title_label = ttk.Label(main_frame, text="Windows Context Menu Configuration (Requires Administrator)", font=('Arial', 12, 'bold'))
        title_label.pack(pady=10)


        preset_frame = ttk.Frame(main_frame, padding="5 0 5 15")
        preset_frame.pack(fill="x")
        
        preset_label = ttk.Label(preset_frame, text="Quick Presets:", font=('Arial', 10, 'bold'))
        preset_label.pack(side="left", padx=5)
        
        btn_classic = ttk.Button(preset_frame, text="Set Classic Windows Menu", command=self.set_classic_menu_preset)
        btn_classic.pack(side="left", padx=5)
        
        btn_win11 = ttk.Button(preset_frame, text="Set Default Windows 11 Menu", command=self.set_default_win11_preset)
        btn_win11.pack(side="left", padx=5)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_columnconfigure(2, weight=1)

        # 1. File & Folder Utilities
        self.create_section(content_frame, "I. File & Folder Utilities", [
            ("Copy as Path", "copy_path"), ("Take Ownership", "take_ownership"), ("Check File Hash (SHA, MD5)", "check_hash"),
            ("Block in Firewall (for .exe)", "block_fw"), ("Change File Attributes", "change_attr"), ("Quick Scan with Microsoft Defender", "defender_scan"),
            ("Copy To Folder...", "copy_to_folder"), ("Move To Folder...", "move_to_folder"), ("Open with Notepad++", "open_npp"), ("Add to Startup Folder", "add_startup")
        ], row=0, col=0)
        
        # 2. System & Desktop Tools
        self.create_section(content_frame, "II. System & Desktop Tools", [
            ("Open Windows Terminal", "open_wst"), ("Open Command Prompt", "open_cmd"), ("Open PowerShell", "open_ps"),
            ("God Mode", "god_mode"), ("Clean up Clipboard", "empty_clipboard"), ("Compact Folder (NTFS)", "compact_folder"),
            ("Task Manager", "task_mgr"), ("Control Panel", "control_panel"), ("Services", "services_msc")
        ], row=0, col=1)

        # 3. Menu Cleanup
        # Note: defender_scan is tracked by its custom key 06_QuickScanDefender. If both Cleanup and Add are checked, the key is ADDED.
        self.create_section(content_frame, "III. Menu Cleanup (Disable/Remove)", [
            ("Remove 'Share'", "remove_share"), ("Remove 'Cast to device'", "remove_cast"), ("Remove 'Edit with Paint 3D'", "remove_paint3d"),
            ("Remove '3D Print'", "remove_3dprint"), ("Remove 'Edit with Photos'", "remove_photos"), ("Remove 'Edit with Clipchamp'", "remove_clipchamp"),
            ("Remove 'Open in Windows Terminal' (Default)", "remove_wst_menu"), ("Remove 'Scan with Microsoft Defender' (Default)", "defender_scan"),
            ("Remove 'Add to VLC playlist'", "remove_vlc"), ("Remove 'WinRAR' menu items", "remove_winrar")
        ], row=0, col=2)
        
        apply_button = ttk.Button(main_frame, text="REVIEW & APPLY CHANGES", command=self.apply_changes)
        apply_button.pack(pady=15, padx=10, fill="x")

    def create_section(self, parent_frame, title, items, row, col):
        """Creates a frame for a section and adds Checkbuttons."""
        section_frame = ttk.Frame(parent_frame, padding="5")
        section_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        title_label = ttk.Label(section_frame, text=title, font=('Arial', 10, 'bold'))
        title_label.pack(anchor="w", pady=(0, 5))
            
        for text, key in items:
            var = tk.BooleanVar(value=False)
            prefix = "Enable: " if not key.startswith("remove_") else "Remove: "

            check = ttk.Checkbutton(section_frame, text=f"{prefix}{text}", variable=var, onvalue=True, offvalue=False)
            check.pack(anchor="w", padx=5)
            self.config_vars[key] = (var, check)

    def apply_changes(self):
        """Handles the logic when the user presses Apply, executing changes and restarting explorer."""
        if not is_admin():
            print("Permission Error: Administrator privileges required to apply changes.", file=sys.stderr)
            return

        add_list = []
        remove_list = []
        
        for key, (var, name) in self.config_vars.items():
            is_checked = var.get()
            is_cleanup_item = key.startswith("remove_")

            if is_cleanup_item:
                # cleanup: only queue DELETE action when checkbox is CHECKED (user wants it removed)
                if is_checked:
                    add_list.append((key, name))
                else:
                    # UNCHECK: do nothing (restore not implemented)
                    pass
            else:
                if is_checked:
                    add_list.append((key, name))
                else:
                    remove_list.append((key, name))

        # Thực thi tất cả thay đổi 1 lần
        self.execute_registry_changes(add_list, remove_list)
        
        # Restart Explorer đúng 1 lần sau khi tất cả thay đổi đã được áp dụng
        if restart_explorer():
            print("Changes applied successfully! Windows Explorer has been restarted to apply updates.")
        else:
            print("Changes applied successfully, but could not automatically restart Explorer. Please restart Explorer manually or log off/on.")

    def execute_registry_changes(self, add_list, remove_list):
        """Executes registry operations based on the collected lists."""
        successful_adds = 0
        successful_removes = 0
        
        # 1. Execute ADD (Enable/Remove) actions
        for key, name in add_list:
            config = REGISTRY_CONFIG.get(key)
            if config and "add" in config and config["add"]():
                successful_adds += 1
        
        # 2. Execute REMOVE (Disable/Restore) actions
        for key, name in remove_list:
            config = REGISTRY_CONFIG.get(key)
            if config and "remove" in config and config["remove"]():
                successful_removes += 1
                
        print(f"Summary: {successful_adds} ADD actions executed, {successful_removes} REMOVE actions executed.")
        
    def set_classic_menu_preset(self):
        """Sets the menu to the Classic Windows Context Menu style."""
        if not is_admin():
            return
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32")
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)
            restart_explorer()
        except Exception as e:
            print(f"Could not set Classic preset: {e}", file=sys.stderr)

    def set_default_win11_preset(self):
        """Restores the menu to the Default Windows 11 Context Menu style."""
        if not is_admin():
            return
        try:
            key_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            except FileNotFoundError:
                pass
            restart_explorer()
        except Exception as e:
            print(f"Could not restore Default Win11 preset: {e}", file=sys.stderr)
        
def Menu():
    # --- TỰ KHỞI ĐỘNG LẠI (Self-Restart) ---
    if not is_admin():
        restart_as_admin() 
    else:
        app = ContextMenuConfigurator()
        app.mainloop()

if __name__ == "__main__":
    Menu()

def _escape_backup_name(key_path: str) -> str:
    return key_path.replace("\\", "||").replace("*", "_STAR_").replace(":", "_")

def _copy_registry_subtree(src_root, src_path, dst_root, dst_path):
    try:
        src = winreg.OpenKey(src_root, src_path, 0, winreg.KEY_READ)
    except FileNotFoundError:
        return False
    dst = winreg.CreateKey(dst_root, dst_path)
    # copy values
    try:
        i = 0
        while True:
            name, val, typ = winreg.EnumValue(src, i)
            winreg.SetValueEx(dst, name, 0, typ, val)
            i += 1
    except OSError:
        pass
    # copy subkeys recursively
    try:
        j = 0
        while True:
            sub = winreg.EnumKey(src, j)
            _copy_registry_subtree(src_root, f"{src_path}\\{sub}", dst_root, f"{dst_path}\\{sub}")
            j += 1
    except OSError:
        pass
    winreg.CloseKey(src)
    winreg.CloseKey(dst)
    return True

BACKUP_ROOT = (winreg.HKEY_CURRENT_USER, r"Software\ToolBox\RegistryBackups")

def backup_registry_key(key_path):
    """Copy key from HKEY_CLASSES_ROOT:key_path into HKCU backup location (keeps original), return True on success."""
    dst_root, dst_base = BACKUP_ROOT
    backup_name = _escape_backup_name(key_path)
    dst_path = f"{dst_base}\\{backup_name}"
    return _copy_registry_subtree(HKEY, key_path, dst_root, dst_path)

def backup_and_delete_registry_key(key_path):
    """Backup then delete original key. Returns True if delete succeeded (or key not present)."""
    try:
        backup_registry_key(key_path)
    except Exception:
        pass
    return remove_registry_key(key_path)

def backup_exists(key_path):
    dst_root, dst_base = BACKUP_ROOT
    backup_name = _escape_backup_name(key_path)
    try:
        winreg.OpenKey(dst_root, f"{dst_base}\\{backup_name}", 0, winreg.KEY_READ).Close()
        return True
    except Exception:
        return False

def restore_registry_key(key_path):
    """Restore key from HKCU backup back to HKEY_CLASSES_ROOT. Returns True on success."""
    dst_root, dst_base = BACKUP_ROOT
    backup_name = _escape_backup_name(key_path)
    backup_path = f"{dst_base}\\{backup_name}"
    # if backup missing, nothing to restore
    try:
        return _copy_registry_subtree(dst_root, backup_path, HKEY, key_path)
    except Exception:
        return False