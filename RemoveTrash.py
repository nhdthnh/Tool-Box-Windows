import tkinter as tk
from tkinter import messagebox
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
        master.geometry("500x350")
        master.configure(bg="#f4f4f4")
        
        tk.Label(master, text="CLEANUP OPTIONS", font=("Arial", 14, "bold"), fg="#2C3E50", bg="#f4f4f4").pack(pady=10)

        cleanup_frame = tk.LabelFrame(master, text="Select items you want to clean up:", font=("Arial", 10, "italic"), padx=15, pady=10, bg="#EAF2F8")
        cleanup_frame.pack(padx=20, pady=5, fill="x")

        # --- List of Boolean variables for Checkboxes ---
        self.cleanup_vars = {
            "win_temp": tk.BooleanVar(value=True),
            "user_temp": tk.BooleanVar(value=True),
            "prefetch": tk.BooleanVar(value=True),
            "win_old": tk.BooleanVar(value=False), 
            "recycle_bin": tk.BooleanVar(value=True),
        }
        
        # --- List of cleanup options ---
        self.cleanup_options = [
            ("Windows Temp Folder (C:\\Windows\\Temp)", "win_temp"),
            ("User Temp Folder (%TEMP%)", "user_temp"),
            ("Prefetch Folder (%SystemRoot%\\Prefetch)", "prefetch"),
            ("Windows.old Folder (If exists - Dism Recommended)", "win_old"),
            ("Recycle Bin (System-wide)", "recycle_bin"),
        ]

        # Create Checkboxes
        for text, key in self.cleanup_options:
            chk = tk.Checkbutton(cleanup_frame, text=text, variable=self.cleanup_vars[key], 
                                 anchor="w", bg="#EAF2F8", font=("Arial", 10))
            chk.pack(fill="x", pady=2)
        
        # --- Start Cleanup Button ---
        tk.Button(master, text="START CLEANUP", 
                  command=self.start_cleanup, bg="#E74C3C", fg="white", 
                  font=("Arial", 11, "bold"), height=2)\
                  .pack(pady=20, padx=20, fill="x")

    def cleanup_path_contents(self, path_name: str, path: str) -> bool:
        """
        Cleans up the contents of a specific folder by deleting and recreating the folder.
        """
        
        if not os.path.exists(path):
            print(f"- Skip: Folder not found: {path_name} ({path})")
            return True 
            
        cmd_delete_dirs = f'RMDIR /S /Q "{path}"' 
        
        success_delete_dir, error_msg_dir = execute_cmd(cmd_delete_dirs)
        
        if success_delete_dir:
            try:
                os.makedirs(path, exist_ok=True)
                print(f"- [OK] Deleted contents and recreated: {path_name} ({path})")
                return True
            except Exception as e:
                print(f"- [Warning] Successfully deleted {path_name} contents, but failed to recreate folder. Error: {e}")
                return True 

        else:
            print(f"- [ERROR] Failed to delete content/folder of {path_name}. Details: {error_msg_dir}")
            return False

    def start_cleanup(self):
        """Performs the actual cleanup operations and prints results to Terminal."""
        
        selected_vars = [key for text, key in self.cleanup_options if self.cleanup_vars[key].get()]
        
        print("\n" + "="*70)
        print("STARTING REAL CLEANUP PROCESS...")
        
        if not selected_vars:
            print("- [No Selection] Please select at least one item.")
            messagebox.showwarning("Warning", "Please select at least one item to clean up.")
            print("="*70 + "\n")
            return

        success_count = 0
        
        # 1. Windows Temp Folder
        if "win_temp" in selected_vars:
            path = "C:\\Windows\\Temp"
            if self.cleanup_path_contents("Windows Temp Folder", path):
                success_count += 1
            
        # 2. User Temp Folder
        if "user_temp" in selected_vars:
            path = os.environ.get('TEMP')
            if path and self.cleanup_path_contents("User Temp Folder", path):
                success_count += 1
            
        # 3. Prefetch Folder (FIXED LOGIC - Use PowerShell for reliability)
        if "prefetch" in selected_vars:
            path = r"C:\\Windows\\Prefetch" 
            
            if not os.path.exists(path):
                print(f"- [Skip] Folder not found: Prefetch Folder ({path})")
            else:
                print(f"- [Cleaning] Prefetch Folder...")
                # Corrected command: Use PowerShell's Remove-Item for reliable deletion of contents within Prefetch
                cmd_delete = f'powershell.exe -Command "Remove-Item -Path \'{path}\\*\' -Recurse -Force -ErrorAction SilentlyContinue"'
                success, error_msg = execute_powershell(cmd_delete)

                if success:
                    print("- [OK] Successfully deleted contents of: Prefetch Folder")
                    success_count += 1
                else:
                    print(f"- [ERROR] Failed to delete Prefetch Folder. Details: {error_msg}")


        # 4. Recycle Bin (FIXED LOGIC - Filter drives to prevent errors)
        if "recycle_bin" in selected_vars:
            print(f"- [Deleting] Recycle Bin using PowerShell (Recommended)...")
            
            # Use PowerShell with filter to ignore drives without a letter (prevents 'InvalidData' error)
            cmd_ps = "Get-Volume | Where-Object {$_.DriveLetter} | ForEach-Object { Clear-RecycleBin -DriveLetter $_.DriveLetter -Force -ErrorAction SilentlyContinue }"
            success_ps, error_msg_ps = execute_powershell(cmd_ps)
            
            if success_ps:
                print("- [OK] Successfully deleted Recycle Bin using PowerShell.")
                success_count += 1
            else:
                # Fallback to CMD for C:\$Recycle.bin if PowerShell fails
                cmd_delete_user_bin = f'rd /s /q "{os.environ.get("SystemDrive")}\\$Recycle.bin"'
                print(f"- [Warning] PowerShell failed ({error_msg_ps}). Trying CMD for C:\\...")
                success_cmd, error_msg_cmd = execute_cmd(cmd_delete_user_bin)
                
                if success_cmd:
                    print("- [OK] Successfully deleted C:\\$Recycle.bin using CMD.")
                    success_count += 1
                else:
                    print(f"- [ERROR] Failed to delete Recycle Bin. Details: {error_msg_cmd}")

        # 5. Windows.old (Cleaned by Dism)
        if "win_old" in selected_vars:
            path = "C:\\Windows.old"
            
            if not os.path.exists(path):
                print(f"- [Skip] Folder not found: Windows.old.")
            else:
                print(f"- [Cleaning] {path} using Dism tool (Recommended)...")

                cmd = 'Dism /online /Cleanup-Image /StartComponentCleanup'
                success, error_msg = execute_cmd(cmd)
                
                if success:
                    print(f"- [OK] Completed Component Cleanup (deletes obsolete system files like Windows.old).")
                    success_count += 1
                else:
                    print(f"- [ERROR] Failed to delete Windows.old/Component Cleanup. Details: {error_msg}")

        
        # --- SUMMARY NOTIFICATION ---
        total_selected = len(selected_vars)
        if success_count == total_selected:
            messagebox.showinfo("Cleanup Completed", f"Successfully deleted {success_count}/{total_selected} selected items.")
        else:
            messagebox.showwarning("Cleanup Finished (With Errors)", f"Completed, but {total_selected - success_count} items failed or were not processed. Check console for details.")

        print(f"\nCLEANUP PROCESS FINISHED. (Success: {success_count}/{total_selected})")
        print("="*70 + "\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = CleanupApp(root)
    root.mainloop()