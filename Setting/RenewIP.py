import subprocess
import platform

def run_network_command(command, command_name):
    """
    Executes a specific network command (e.g., ipconfig /release) and returns the result.

    Args:
        command (list): A list of command parts, e.g., ['ipconfig', '/release'].
        command_name (str): A friendly name for the command to display in the log.

    Returns:
        tuple: (bool, str) - The success status and the result message.
    """

    print(f"\n--- Executing: {command_name}...")

    # Determine encoding (important for handling command output on Windows)
    # Using 'utf-8' for general compatibility, though 'cp850' might be needed 
    # for non-English Windows consoles with default settings. Sticking to 'utf-8' 
    # is generally preferred for modern systems.
    encoding_type = 'utf-8'
    
    try:
        # Run the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding=encoding_type,
            check=True,  # Raise CalledProcessError if return code is non-zero
            timeout=10   # Set a timeout for the command
        )

        # Command succeeded
        return True, result.stdout.strip()

    except subprocess.CalledProcessError as e:
        # Command ran but returned an error code (e.g., Adapter not found)
        error_output = e.stdout.strip() + "\n" + e.stderr.strip()
        # Note: Added a warning that this often requires Administrator privileges.
        return False, f"SYSTEM ERROR ({command_name}): Check Administrator privileges.\n{error_output}"

    except FileNotFoundError:
        # Error: command itself was not found (e.g., ipconfig)
        return False, "ERROR: 'ipconfig' command not found. (Ensure it is in the system PATH)"

    except Exception as e:
        return False, f"UNKNOWN ERROR: {e}"

def release_flush_renew_network():
    """Performs the sequence of network commands: IP Release, DNS Flush, and IP Renew."""

    # SEQUENCE OF COMMANDS TO EXECUTE (Windows specific)
    commands_sequence = [
        (['ipconfig', '/release'], "RELEASE IP ADDRESS"),
        (['ipconfig', '/flushdns'], "FLUSH DNS CACHE"),
        (['ipconfig', '/renew'], "RENEW IP ADDRESS")
    ]
    
    # Check if the OS is Windows, as ipconfig flags are OS-specific
    if platform.system().lower() != "windows":
        print("This function is designed only for Windows systems (using ipconfig commands).")
        return
    
    all_success = True

    # --- Initial Log/Header ---
    print("=" * 60)
    print("STARTING IP AND DNS RECONFIGURATION PROCESS".center(60))
    print("NOTICE: This program REQUIRES Administrator privileges!".center(60))
    print("=" * 60)

    for command, name in commands_sequence:
        success, output = run_network_command(command, name)

        # Log the result of the current command
        if not success:
            all_success = False
            print(f"[{name}] FAILED.")
            print(output)
            # The failure is logged, but the loop continues to attempt the next steps
        else:
            print(f"[{name}] SUCCESS.")
            # Only display detailed output for RENEW to show the new IP
            if '/renew' in command:
                print("\n--- NEW IP RENEW RESULTS ---")
                print(output)

    # --- Final Log/Footer ---
    print("\n" + "=" * 60)
    if all_success:
        print("IP AND DNS RECONFIGURATION COMPLETED SUCCESSFULLY!")
    else:
        print("IP AND DNS RECONFIGURATION FINISHED (WITH ERRORS). Please check the log.")
    print("=" * 60)

# --- EXECUTION ---
if __name__ == '__main__':
    release_flush_renew_network()