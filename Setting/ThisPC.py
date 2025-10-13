import subprocess

REG_KEY = r'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
REG_NAME = 'LaunchTo'

def execute_command(command_list: list, check_success=True, is_powershell=False) -> (int, str, str):
    """
    Executes a CMD/PowerShell command as a list, returning the return code, stdout, and stderr.
    
    Args:
        command_list: List of command components (e.g., ['REG', 'DELETE', ...])
        check_success: If True, explicitly prints errors if the return code is non-zero.
        is_powershell: If True, executes the command via powershell.exe.
    """
    if is_powershell:
        # Call PowerShell and pass the command string
        # Use ' '.join to expand the list into a single command string
        full_command = ['powershell.exe', '-Command', ' '.join(command_list)]
    else:
        full_command = command_list
        
    try:
        # Use shell=False (default) with the list for security
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            check=False 
        )
        
        # Check for more detailed errors
        if check_success and result.returncode != 0 and "successfully" not in result.stdout.lower():
            # Allow REG DELETE to return an error if the value doesn't exist (code 1)
            if not ('REG DELETE' in ' '.join(full_command) and result.returncode == 1): 
                print(f"!!! ERROR ({full_command[0]}) !!! Code: {result.returncode}")
                print(f"Error (Stderr): {result.stderr.strip()}")
            
        return result.returncode, result.stdout, result.stderr
        
    except FileNotFoundError:
        print(f"ERROR: Tool '{full_command[0]}' not found. Ensure it is in the PATH environment variable.")
        return -1, "", "Tool not found"
    except Exception as ex:
        print(f"UNKNOWN ERROR occurred during command execution: {ex}")
        return -2, "", str(ex)

def restart_explorer():
    """Restarts the explorer.exe process to apply Registry changes."""
    print("\n[EXPLORER] Restarting explorer.exe to apply changes...")
    try:
        # Use separate calls for reliability
        subprocess.run('TASKKILL /f /im explorer.exe', shell=True, check=True, capture_output=True)
        subprocess.run('START explorer.exe', shell=True, check=True, capture_output=True)
        print("[EXPLORER] Explorer has been restarted.")
    except Exception:
        # Fails silently if the process cannot be killed/started
        pass

def set_explorer_default_this_pc():
    """Sets File Explorer to default to This PC (LaunchTo=1)."""
    print(f"\n--- SETTING EXPLORER DEFAULT: THIS PC ---")
    
    # Command: REG ADD REG_KEY /v LaunchTo /t REG_DWORD /d 1 /f
    command = ['REG', 'ADD', REG_KEY, '/v', REG_NAME, '/t', 'REG_DWORD', '/d', '1', '/f']
    code, out, err = execute_command(command)
    
    if code == 0:
        print("Successfully set File Explorer default to THIS PC.")
        # restart_explorer() # Uncomment if immediate effect is needed
    else:
        print("!!! Registry setting failed.")

def remove_explorer_default_setting():
    """Deletes the LaunchTo value to revert File Explorer to the Windows default (Quick Access)."""
    print(f"\n--- REMOVING EXPLORER DEFAULT SETTING ---")
    
    # Use check_success=False because REG DELETE returns error code 1 if the value doesn't exist
    command = ['REG', 'DELETE', REG_KEY, '/v', REG_NAME, '/f']
    code, out, err = execute_command(command, check_success=False)
    
    # Error code 0 is success. Error code 1 means value not found (still achieves the goal)
    if code in [0, 1] or "successfully" in out.lower(): 
        print("Successfully deleted the LaunchTo Registry value (or value did not exist).")
        # restart_explorer() # Uncomment if immediate effect is needed
    else:
        print(f"!!! Error deleting Registry value.")

# set_explorer_default_this_pc()
# remove_explorer_default_setting()