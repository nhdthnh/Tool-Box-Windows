import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def restore_drivers():
    # Open folder selection dialog
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select the folder containing your backed-up drivers (.inf)")

    if not folder_path:
        messagebox.showwarning("Warning", "No folder selected!")
        return

    # Check if the folder exists
    if not os.path.exists(folder_path):
        messagebox.showerror("Error", f"The folder does not exist:\n{folder_path}")
        return

    # Confirm action
    confirm = messagebox.askyesno("Confirm",
        f"Are you sure you want to restore drivers from this folder?\n\n{folder_path}"
    )
    if not confirm:
        return

    try:
        # Build pnputil command
        cmd = f'pnputil /add-driver "{folder_path}\\*.inf" /subdirs /install'
        print(f"Running: {cmd}")

        # Execute command and capture output
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        # Show output (truncated if too long)
        output = result.stdout or result.stderr
        messagebox.showinfo("Result", f"Driver installation completed.\n\n{output[:1000]}...")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while running the command:\n{e}")

if __name__ == "__main__":
    restore_drivers()
