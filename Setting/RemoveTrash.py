import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sys
import ctypes
import os
import subprocess

# --- ADMINISTRATOR PRIVILEGE CHECK AND ELEVATION (MANDATORY FOR SYSTEM CLEANUP) ---
def is_admin():
  """Checks if the script is currently running with Administrator privileges."""
  try:
    return ctypes.windll.shell32.IsUserAnAdmin()
  except:
    return False

if not is_admin():
  try:
    # Re-run the script with Administrator privileges
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit(0)
  except Exception:
    messagebox.showerror("Error", "Program requires Administrator privileges to clean system folders. The program will exit.")
    sys.exit(1)
# ----------------------------------------------------------------------------------

# --- POWERSHELL/CMD EXECUTION HELPERS ---
def execute_powershell(command: str):
  """Executes a PowerShell command."""
  try:
    result = subprocess.run(
      ["powershell", "-Command", command],
      capture_output=True, text=True, check=True,
      creationflags=subprocess.CREATE_NO_WINDOW
    )
    return True, result.stdout.strip()
  except subprocess.CalledProcessError as e:
    error_output = e.stderr.strip() if e.stderr else f"Exit Code: {e.returncode}"
    return False, error_output
  except Exception as e:
    return False, str(e)

def execute_cmd(command: str):
  """Executes a CMD command."""
  try:
    result = subprocess.run(
      command,
      shell=True,
      capture_output=True, text=True, check=True,
      creationflags=subprocess.CREATE_NO_WINDOW
    )
    return True, result.stdout.strip()
  except subprocess.CalledProcessError as e:
    error_output = e.stderr.strip() if e.stderr else f"Exit Code: {e.returncode}"
    return False, error_output
  except Exception as e:
    return False, str(e)

class CleanupApp:
  def __init__(self, master):
    self.master = master
    master.title("SYSTEM CLEANUP UTILITY")
    master.geometry("550x550")
    master.configure(bg="#F0F0F0") # Light background

    # --- Setup Light Mode Style ---
    style = ttk.Style()
    style.theme_create("light_theme", parent="alt", settings={
      "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0], "background": "#F0F0F0"}},
      "TNotebook.Tab": {"configure": {"padding": [15, 5], "background": "#E0E0E0", "foreground": "black"},
               "map": {"background": [("selected", "#3498DB")], "foreground": [("selected", "white")]}},
      "TFrame": {"configure": {"background": "#FFFFFF"}},
    })
    style.theme_use("light_theme")
   
    # --- NOTEBOOK (TABS) ---
    self.notebook = ttk.Notebook(master)
    self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
   
    self.cleanup_vars = {} # Dictionary to store all BooleanVars

    # Create Tabs
    self.create_basic_tab()
    self.create_advanced_tab()
    self.create_apps_tab()
   
    # --- Start Cleanup Button ---
    tk.Button(master, text="START CLEANUP",
         command=self.start_cleanup_routine, bg="#3498DB", fg="white",
         font=("Arial", 11, "bold"), height=2)\
         .pack(pady=(5, 15), padx=20, fill="x")


# ----------------------------------------------------------------------------------
# --- TAB CREATION METHODS ---
# ----------------------------------------------------------------------------------

  def create_checkbox(self, parent_frame, text, key, default_value=False):
    """Helper function to create a themed Checkbutton."""
    self.cleanup_vars[key] = tk.BooleanVar(value=default_value)
    chk = tk.Checkbutton(parent_frame, text=text, variable=self.cleanup_vars[key],
              anchor="w", bg="#FFFFFF", fg="black", selectcolor="#E0E0E0",
              font=("Arial", 10), activebackground="#BBBBBB", activeforeground="black")
    chk.pack(fill="x", pady=2, padx=5)
    return key

  def create_basic_tab(self):
    # --- BASIC TAB ---
    tab_basic = ttk.Frame(self.notebook, padding="10")
    self.notebook.add(tab_basic, text="Basic")
   
    # Basic Options List
    self.create_checkbox(tab_basic, "Windows Temp Folder (C:\\Windows\\Temp)", "win_temp", True)
    self.create_checkbox(tab_basic, "User Temp Folder (%TEMP%)", "user_temp", True)
    self.create_checkbox(tab_basic, "Prefetch Folder (%SystemRoot%\\Prefetch)", "prefetch", True)
    self.create_checkbox(tab_basic, "Recycle Bin (System-wide)", "recycle_bin", True)
    self.create_checkbox(tab_basic, "Crash Dumps Files", "crash_dumps")
    self.create_checkbox(tab_basic, "Recent Items (Jump Lists)", "recent_items")
    self.create_checkbox(tab_basic, "DNS Cache (ipconfig /flushdns)", "dns_cache")
    self.create_checkbox(tab_basic, "Clear Clipboard", "clear_clipboard")
    self.create_checkbox(tab_basic, "Thumbnail Cache", "thumbnail_cache")
    self.create_checkbox(tab_basic, "Clean Empty Downloads Folder", "empty_downloads_folder")
    self.create_checkbox(tab_basic, "Delete .tmp Files on Drive C:", "tmp_files_c")
    self.create_checkbox(tab_basic, "Delete .bak/.old Files on Drive C:", "bak_old_files_c")


  def create_advanced_tab(self):
    # --- ADVANCED TAB ---
    tab_advanced = ttk.Frame(self.notebook, padding="10")
    self.notebook.add(tab_advanced, text="Advanced")
   
    # Advanced Options List
    self.create_checkbox(tab_advanced, "Windows.old Folder (if exists - Dism Recommended)", "win_old_dism")
    self.create_checkbox(tab_advanced, "Windows Update Cache (SoftwareDistribution)", "win_update_cache")
    self.create_checkbox(tab_advanced, "Delivery Optimization Files", "delivery_opt_files")
    self.create_checkbox(tab_advanced, "Windows Error Reporting Files (WER)", "windows_error_reporting")
    self.create_checkbox(tab_advanced, "Remove Shadow Copies (Keep newest)", "shadow_copies")
    self.create_checkbox(tab_advanced, "Cleanup WinSXS (Component Store - Dism Recommended)", "winsxs_cleanup")
    self.create_checkbox(tab_advanced, "Delete System Log files (*.log)", "system_logs")
    self.create_checkbox(tab_advanced, "Clear Windows Event Logs", "event_logs")
    self.create_checkbox(tab_advanced, "Windows Defender Scan History", "defender_history")
    self.create_checkbox(tab_advanced, "Delete old Windows Installer Patches", "installer_patches")
    self.create_checkbox(tab_advanced, "Cleanup .NET Framework Cache", "dotnet_cache")
    self.create_checkbox(tab_advanced, "Rebuild Font Cache", "rebuild_font_cache")
    self.create_checkbox(tab_advanced, "Windows Update Error Logs", "update_error_logs")
    self.create_checkbox(tab_advanced, "Delete Orphan Startup Shortcuts", "orphan_shortcuts")

  def create_apps_tab(self):
    # --- BROWSERS & APPS TAB ---
    tab_apps = ttk.Frame(self.notebook, padding="10")
    self.notebook.add(tab_apps, text="Browsers & Apps")
   
    # Browsers & Apps Options List
    # NOTE: For simplicity, detailed app cache cleanup is often done by deleting the Cache folder for the user.
    self.create_checkbox(tab_apps, "DirectX Shader Cache", "dx_shader_cache")
    self.create_checkbox(tab_apps, "GPU Cache (NVIDIA, AMD)", "gpu_cache")
    self.create_checkbox(tab_apps, "Microsoft Store Cache", "ms_store_cache")
    self.create_checkbox(tab_apps, "Browser Cache (Chrome, Edge) - Common User Profile Cache", "browser_cache")
    self.create_checkbox(tab_apps, "Firefox Browser Cache", "firefox_cache")
    self.create_checkbox(tab_apps, "Discord Cache", "discord_cache")
    self.create_checkbox(tab_apps, "Telegram Desktop Cache", "telegram_cache")
    self.create_checkbox(tab_apps, "Zoom Cache", "zoom_cache")
    self.create_checkbox(tab_apps, "WhatsApp Desktop Cache", "whatsapp_cache")
    self.create_checkbox(tab_apps, "Adobe Cache (Common, Media, Acrobat)", "adobe_cache")
    self.create_checkbox(tab_apps, "Epic Games Launcher Cache", "epic_cache")
    self.create_checkbox(tab_apps, "Steam Download Cache", "steam_cache")
    self.create_checkbox(tab_apps, "Visual Studio Code Cache", "vscode_cache")
    self.create_checkbox(tab_apps, "Spotify Cache", "spotify_cache")


# ----------------------------------------------------------------------------------
# --- CLEANUP LOGIC METHODS ---
# ----------------------------------------------------------------------------------
  # Reusing existing successful logic functions, translated output strings
  def cleanup_path_contents(self, path_name: str, path: str) -> bool:
    """Cleans up the contents of a specific folder."""
    if not os.path.exists(path):
      print(f"- [SKIP] Folder not found: {path_name} ({path})")
      return True
     
    cmd_delete_dirs = f'RMDIR /S /Q "{path}"'
    success_delete_dir, error_msg_dir = execute_cmd(cmd_delete_dirs)
   
    if success_delete_dir:
      try:
        os.makedirs(path, exist_ok=True)
        print(f"- [OK] Deleted contents and recreated: {path_name}")
        return True
      except Exception as e:
        print(f"- [WARNING] Successfully deleted {path_name} contents, but failed to recreate folder. Error: {e}")
        return True
    else:
      print(f"- [ERROR] Failed to delete content/folder of {path_name}. Details: {error_msg_dir}")
      return False

  def cleanup_files_with_extension(self, path_name: str, base_path: str, extensions: list) -> bool:
    """Deletes files with specific extensions recursively in a base path."""
    print(f"- [DELETING] {path_name} files in: {base_path}")
    success_count = 0
    for ext in extensions:
      cmd = f'forfiles /p "{base_path}" /s /m "*{ext}" /c "cmd /c del /f /q @path"'
      success, _ = execute_cmd(cmd)
      if success:
        success_count += 1
     
    if success_count == len(extensions):
      print(f"- [OK] Successfully deleted {path_name} files ({', '.join(extensions)}).")
      return True
    else:
      print(f"- [ERROR] Errors occurred while deleting {path_name} files ({success_count}/{len(extensions)} types succeeded).")
      return False

  def execute_dism_cleanup(self, path_name: str, command: str) -> bool:
    """Executes a DISM command for cleanup."""
    print(f"- [RUNNING] Cleaning up {path_name} using DISM. This might take a while...")
    success, error_msg = execute_cmd(command)
    if success:
      print(f"- [OK] Completed {path_name} Cleanup via DISM.")
      return True
    else:
      print(f"- [ERROR] DISM failed for {path_name}. Details: {error_msg}")
      return False

  def cleanup_browser_cache_user(self) -> bool:
    """Cleans Chrome/Edge/Firefox cache folders for the current user."""
    user_profile = os.environ.get('USERPROFILE')
    cache_paths = [
      os.path.join(user_profile, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Cache'),
      os.path.join(user_profile, 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache'),
    ]
    all_success = True
    for path in cache_paths:
      if os.path.exists(path):
        # Delete content of the Cache folder
        if not self.cleanup_path_contents(f"Cache ({os.path.basename(os.path.dirname(os.path.dirname(path)))})", path):
          all_success = False
    return all_success

  def cleanup_app_cache_by_path(self, app_name, relative_path) -> bool:
    """Generic function to clean app cache based on AppData path."""
    user_profile = os.environ.get('USERPROFILE')
    path = os.path.join(user_profile, 'AppData', relative_path)
    # Try to clean a potential Cache/Temp folder inside the specified path
    cache_paths = [
      os.path.join(path, 'Cache'),
      os.path.join(path, 'cache'),
      os.path.join(path, 'temp'),
      os.path.join(path, 'Temp'),
      path # Try to clean the main directory as a last resort
    ]

    success = False
    for p in cache_paths:
      if os.path.exists(p):
        if self.cleanup_path_contents(f"{app_name} Cache", p):
          success = True
          break
     
    if not success:
      print(f"- [SKIP/ERROR] {app_name} Cache cleanup failed or path not found.")
     
    return success


# ----------------------------------------------------------------------------------
# --- MAIN CLEANUP ROUTINE ---
# ----------------------------------------------------------------------------------

  def start_cleanup_routine(self):
    """Performs the actual cleanup operations and prints results to Terminal."""
   
    selected_vars = [key for key, var in self.cleanup_vars.items() if var.get()]
   
    print("\n" + "="*70)
    print("STARTING CLEANUP PROCESS...")
   
    if not selected_vars:
      print("- [No Selection] Please select at least one item.")
      messagebox.showwarning("Warning", "Please select at least one item to clean up.")
      print("="*70 + "\n")
      return

    success_count = 0
    total_selected = len(selected_vars)
   
    # --- CLEANUP EXECUTION ---
    for key in selected_vars:
      result = False
     
      # BASIC TABS LOGIC
      if key == "win_temp":
        result = self.cleanup_path_contents("Windows Temp Folder", "C:\\Windows\\Temp")
      elif key == "user_temp":
        result = self.cleanup_path_contents("User Temp Folder", os.environ.get('TEMP'))
      elif key == "prefetch":
        path = r"C:\\Windows\\Prefetch"
        print(f"- [DELETING] Prefetch Folder contents...")
        cmd_delete = f'powershell.exe -Command "Remove-Item -Path \'{path}\\*\' -Recurse -Force -ErrorAction SilentlyContinue"'
        success, error_msg = execute_powershell(cmd_delete)
        result = success
        if not success: print(f"- [ERROR] Prefetch Folder. Details: {error_msg}")
      elif key == "recycle_bin":
        print(f"- [DELETING] Recycle Bin (System-wide)...")
        cmd_ps = "Get-Volume | Where-Object {$_.DriveLetter} | ForEach-Object { Clear-RecycleBin -DriveLetter $_.DriveLetter -Force -ErrorAction SilentlyContinue }"
        success_ps, error_msg_ps = execute_powershell(cmd_ps)
        result = success_ps
        if not success_ps: print(f"- [ERROR] Recycle Bin. Details: {error_msg_ps}")
      elif key == "crash_dumps":
        result = self.cleanup_files_with_extension("Crash Dumps (.dmp)", "C:\\", ['.dmp'])
      elif key == "dns_cache":
        success, error_msg = execute_cmd("ipconfig /flushdns")
        result = success
        if not success: print(f"- [ERROR] DNS Cache. Details: {error_msg}")
      elif key == "clear_clipboard":
        try:
          ctypes.windll.user32.OpenClipboard(None)
          ctypes.windll.user32.EmptyClipboard()
          ctypes.windll.user32.CloseClipboard()
          print("- [OK] Clipboard cleared successfully.")
          result = True
        except Exception as e:
          print(f"- [ERROR] Clearing Clipboard. Details: {e}")
          result = False
      elif key == "thumbnail_cache":
        print("- [DELETING] Thumbnail Cache...")
        cmd_ps = 'powershell.exe -Command "Get-ChildItem -Path $env:LOCALAPPDATA\\Microsoft\\Windows\\Explorer -Include thumbcache*.db -Recurse -Force -ErrorAction SilentlyContinue | Remove-Item -Force"'
        success, error_msg = execute_powershell(cmd_ps)
        result = success
        if not success: print(f"- [ERROR] Thumbnail Cache. Details: {error_msg}")
      elif key == "tmp_files_c":
        result = self.cleanup_files_with_extension(".tmp Files on C:", "C:\\", ['.tmp'])
      elif key == "bak_old_files_c":
        result = self.cleanup_files_with_extension(".bak/.old Files on C:", "C:\\", ['.bak', '.old'])

      # ADVANCED TABS LOGIC
      elif key == "win_old_dism" or key == "winsxs_cleanup":
        cmd_dism = 'Dism /online /Cleanup-Image /StartComponentCleanup'
        result = self.execute_dism_cleanup("Windows.old / Component Store (WinSXS)", cmd_dism)
      elif key == "win_update_cache":
        result = self.cleanup_path_contents("Windows Update Cache", "C:\\Windows\\SoftwareDistribution\\Download")
      elif key == "event_logs":
        print("- [DELETING] Windows Event Logs...")
        cmd_ps = 'Get-EventLog -LogName * | ForEach-Object { Clear-EventLog -LogName $_.Log }'
        success, error_msg = execute_powershell(cmd_ps)
        result = success
        if not success: print(f"- [ERROR] Event Logs. Details: {error_msg}")
      elif key == "shadow_copies":
        print("- [DELETING] Oldest Shadow Copies (Keeping newest)...")
        cmd = 'vssadmin delete shadows /for=c: /oldest'
        success, error_msg = execute_cmd(cmd)
        result = success
        if not success: print(f"- [ERROR] Shadow Copies. Details: {error_msg}")

      # APPS TABS LOGIC
      elif key == "dx_shader_cache":
        path = os.path.join(os.environ.get('LOCALAPPDATA'), 'D3DSCache')
        result = self.cleanup_path_contents("DirectX Shader Cache", path)
      elif key == "gpu_cache":
        path = os.path.join(os.environ.get('LOCALAPPDATA'), 'NVIDIA', 'DXCache')
        if not os.path.exists(path):
          path = os.path.join(os.environ.get('LOCALAPPDATA'), 'AMD', 'DxCache')
        result = self.cleanup_path_contents("GPU Cache", path)
      elif key == "ms_store_cache":
        # Command to reset MS Store cache
        success, error_msg = execute_cmd("wsreset.exe -silent")
        result = success
        if not success: print(f"- [ERROR] MS Store Cache. Details: {error_msg}")
      elif key == "browser_cache":
        result = self.cleanup_browser_cache_user()
      elif key == "discord_cache":
        result = self.cleanup_app_cache_by_path("Discord", "Roaming\\Discord")
      elif key == "telegram_cache":
        # Telegram often uses Local/Telegram Desktop/tdata/cache
        path = os.path.join(os.environ.get('LOCALAPPDATA'), 'Telegram Desktop', 'tdata', 'cache')
        result = self.cleanup_path_contents("Telegram Cache", path)
      elif key == "vscode_cache":
        # VS Code Cache is usually in Local/Programs/Microsoft VS Code/Cache
        path = os.path.join(os.environ.get('APPDATA'), 'Code', 'Cache')
        result = self.cleanup_path_contents("Visual Studio Code Cache", path)
      # All other remaining items use the general app cache cleanup logic (if known path)
      elif key == "firefox_cache":
        # Firefox cache is complex (in Profiles folder). We will use the common cache location for simplicity here.
        print(f"- [SKIP] Firefox Cache requires finding the specific Profile folder (Complex). Skipping.")
        continue

      else:
        print(f"- [SKIP] Item not yet implemented in detail: {key}")
        continue

      if result:
        success_count += 1
   
    # --- SUMMARY NOTIFICATION ---
    if success_count == total_selected:
      messagebox.showinfo("Cleanup Completed", f"Successfully cleaned {success_count}/{total_selected} selected items.")
    else:
      messagebox.showwarning("Cleanup Finished (With Errors/Skips)", f"Completed, but {total_selected - success_count} items failed or were skipped. Check console for details.")

    print(f"\nCLEANUP PROCESS FINISHED. (Success: {success_count}/{total_selected})")
    print("="*70 + "\n")


# External function call:
def call_cleanup_routine():
  """
  Runs the entire CleanupApp application with the GUI.
  """
  root = tk.Tk()
  app = CleanupApp(root)
  root.mainloop()

# Run the application when the script is executed
if __name__ == "__main__":
  call_cleanup_routine()