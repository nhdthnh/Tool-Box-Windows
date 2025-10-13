import subprocess
import sys

def configure_wuauserv(start_type: str) -> bool:
    """
    Configures the Start Type for the Windows Update service (wuauserv).
    
    Args:
        start_type (str): The desired start type ('auto' or 'disabled').
        
    Returns:
        bool: True if configuration succeeds, False if it fails.
    """
    # The SC CONFIG command is used to change the service start type
    # Syntax: sc config <service_name> start= <start_type> (Note the space after start=)
    command = f'sc config wuauserv start= {start_type}'
    
    print(f"[{start_type.upper()}] Executing command: {command}")
    
    try:
        # Execute the CMD command
        # NOTE: The Python script MUST be run with Administrator privileges
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True # Raise exception if the command returns a non-zero exit code
        )
        
        # Check the output content for the SC command's success message
        if "SUCCESS" in result.stdout.upper():
            print(f"wuauserv configuration successful: start={start_type.upper()}")
            
            # Start or stop the service immediately after configuration
            if start_type.lower() == 'auto':
                # Enable and start the service
                subprocess.run('net start wuauserv', shell=True, capture_output=True, text=True)
                print("Attempted to start the wuauserv service.")
            elif start_type.lower() == 'disabled':
                # Stop the service
                subprocess.run('net stop wuauserv', shell=True, capture_output=True, text=True)
                print("Attempted to stop the wuauserv service.")
                
            return True
        else:
            print(f"Configuration failed. Output: {result.stdout.strip()}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"!!! ERROR while executing command !!!")
        print(f"Error (Stderr): {e.stderr.strip()}")
        print("\n* Common Issue: The Python script needs to be run with **Administrator** privileges.")
        return False
    except Exception as ex:
        print(f"An unknown error occurred: {ex}")
        return False

# --- SPECIFIC WINDOWS UPDATE ON/OFF FUNCTIONS ---

def enable_windows_update():
    """Enables Windows Update (wuauserv) by setting start= auto."""
    print("--- ENABLE WINDOWS UPDATE ---")
    return configure_wuauserv('auto')

def disable_windows_update():
    """Disables Windows Update (wuauserv) by setting start= disabled."""
    print("--- DISABLE WINDOWS UPDATE ---")
    return configure_wuauserv('disabled')


# --- TESTING ---

# if __name__ == '__main__':
#     # Example: Disable Windows Update
#     # disable_windows_update()
    
#     # Example: Enable Windows Update
#     # enable_windows_update()
    
#     # Run both for testing
#     # print("--- TESTING DISABLE ---")
#     # disable_windows_update()
    
#     # print("\n" + "="*50 + "\n")
    
#     print("--- TESTING ENABLE ---")
#     enable_windows_update()
    
#     print("\nCheck the status in Services (services.msc) to verify.")