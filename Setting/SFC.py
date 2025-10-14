import os
import string
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox


def run_command(command, title):
    """Run a system command and show a short preview of the output."""
    try:
        process = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = process.stdout or process.stderr
        messagebox.showinfo(title, output[:1500] + "\n\n(Truncated output)")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run command:\n\n{e}")


def get_available_drives():
    """Return a list of available drives on the system."""
    drives = []
    for letter in string.ascii_uppercase:
        if os.path.exists(f"{letter}:\\"):
            drives.append(f"{letter}:")
    return drives


def run_sfc_scan():
    """Run System File Checker (SFC /scannow)."""
    confirm = messagebox.askyesno("Confirm", "Run System File Checker (sfc /scannow)?")
    if confirm:
        run_command("sfc /scannow", "System File Checker (SFC)")
    else:
        messagebox.showinfo("Canceled", "SFC scan was canceled.")


def run_chkdsk():
    """Ask the user to select a drive and run CHKDSK /f /r."""
    drives = get_available_drives()
    if not drives:
        messagebox.showerror("Error", "No drives found on this system!")
        return

    # Create popup for drive selection
    drive_window = tk.Toplevel()
    drive_window.title("Select Drive for CHKDSK")
    drive_window.geometry("300x160")
    drive_window.resizable(False, False)

    tk.Label(drive_window, text="Select drive to check:", font=("Segoe UI", 11)).pack(pady=10)

    drive_var = tk.StringVar(value=drives[0])
    drive_dropdown = ttk.Combobox(drive_window, textvariable=drive_var, values=drives, state="readonly")
    drive_dropdown.pack(pady=5)

    def start_chkdsk():
        drive = drive_var.get()
        cmd = f"chkdsk {drive} /f /r"
        drive_window.destroy()
        run_command(cmd, f"Check Disk (CHKDSK) - {drive}")

    ttk.Button(drive_window, text="Run CHKDSK", command=start_chkdsk).pack(pady=15)

