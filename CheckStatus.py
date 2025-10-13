import subprocess
import sys
import ctypes
import os

def is_admin():
    """Check whether the script is running with Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Ensure scripts that require admin are relaunched with elevation at start
if not is_admin():
    print("Requesting Administrator privileges...")
    try:
        # Relaunch the script with elevated privileges (this triggers UAC)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit(0)  # Exit the non-elevated instance
    except Exception as e:
        print(f"Unable to request Administrator privileges: {e}")
        sys.exit(1)
# -----------------------------------------------------------

def check_windows_license_status_no_popup():
    """
    Run slmgr /dli via cscript and print the output to the terminal (stdout).
    """
    # Command executed with cscript to force text output to stdout
    command = "cscript //Nologo C:\\Windows\\System32\\slmgr.vbs /dli"

    print("\n--- CHECKING WINDOWS ACTIVATION STATUS ---")
    print(f"Command: {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )

        print("\n--- SLMGR /DLI OUTPUT ---")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print("\n--- SLMGR EXECUTION ERROR ---")
        print(f"ERROR: Command failed (return code: {e.returncode}).")
        if e.stderr:
            print(f"Stderr:\n{e.stderr}")

    except Exception as e:
        print("\n--- UNEXPECTED ERROR ---")
        print(f"An unexpected error occurred: {e}")

def check_office_license_status():
    """
    Try common Office install paths to find and run ospp.vbs /dstatus.
    """
    print("\n--- CHECKING OFFICE ACTIVATION STATUS ---")

    # Common paths where OSPP (ospp.vbs) might be located
    office_paths = [
        os.path.normpath("C:/Program Files/Microsoft Office/Office16"),
        os.path.normpath("C:/Program Files/Microsoft Office/Office15"),
        os.path.normpath("C:/Program Files (x86)/Microsoft Office/Office16"),
        os.path.normpath("C:/Program Files (x86)/Microsoft Office/Office15"),
        os.path.normpath("C:/Program Files/Microsoft Office/Office16"),
        os.path.normpath("C:/Program Files/Microsoft Office 15/ClientX64")
    ]

    ospp_found = False

    for path in office_paths:
        ospp_vbs_path = os.path.join(path, "ospp.vbs")

        if os.path.exists(ospp_vbs_path):
            ospp_found = True
            print(f"\n[Found at]: {path}")

            command = f'cscript //Nologo "{ospp_vbs_path}" /dstatus'
            print(f"Command: {command}")

            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=False  # allow continuing even if Office activation returns error
                )

                print("\n--- OSPP /DSTATUS OUTPUT ---")
                print(result.stdout)
                return

            except Exception as e:
                print(f"[ERROR RUNNING OSPP]: Error with this path: {e}. Trying next path.")
                continue

    if not ospp_found:
        print("\n--- FINISHED ---")
        print("Could not find 'ospp.vbs' in common Office installation directories.")
        print("Office may not be installed or may be in a custom folder.")

# End of file