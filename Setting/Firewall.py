import subprocess
import sys

def manage_firewall_state(state: str) -> bool:
    """
    Turns Windows Defender Firewall ON or OFF for all profiles.
    
    Args:
        state (str): The desired state ('on' or 'off').
        
    Returns:
        bool: True if configuration was successful, False otherwise.
    """
    # The NETSH ADVFIREWALL command to set the state
    # Syntax: netsh advfirewall set allprofiles state <state>
    command = f'netsh advfirewall set allprofiles state {state}'
    
    action_english = "ENABLE" if state.lower() == 'on' else "DISABLE"
    print(f"[{action_english}] Executing command: {command}")
    
    try:
        # Execute the CMD command
        # Use shell=True to ensure the netsh command runs correctly
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True  # Will raise an exception if the command returns an error
        )
        
        # netsh commands often do not return explicit output on success,
        # so we check the return code and stderr (error stream)
        if result.returncode == 0 and not result.stderr:
            print(f"Firewall configuration successful: Firewall has been {action_english}D for all Profiles.")
            return True
        else:
            print(f"Configuration failed. Output: {result.stdout.strip()} | Error: {result.stderr.strip()}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"!!! ERROR while executing command !!!")
        print(f"Error (Stderr): {e.stderr.strip()}")
        print("\n* Common issue: The Python script needs to be run with **Administrator** privileges.")
        return False
    except Exception as ex:
        print(f"An unknown error occurred: {ex}")
        return False

# --- SPECIFIC FIREWALL TOGGLE FUNCTIONS ---

def enable_firewall():
    """Enables Windows Firewall for all profiles."""
    print("--- ENABLE WINDOWS FIREWALL ---")
    return manage_firewall_state('on')

def disable_firewall():
    """Disables Windows Firewall for all profiles."""
    print("--- DISABLE WINDOWS FIREWALL ---")
    return manage_firewall_state('off')


def check_firewall_status():
    """
    Checks and displays the current state of Windows Firewall 
    for all Profiles (Domain, Private, Public).
    """
    command = 'netsh advfirewall show allprofiles'
    
    print("--- CHECKING CURRENT FIREWALL STATUS ---")
    print(f"Executing command: {command}")
    
    try:
        # Execute the CMD command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        
        output = result.stdout
        
        # --- PARSING THE OUTPUT ---
        
        # Create a dictionary to store the status of each Profile
        status = {}
        current_profile = None 
        
        # Parse each output line to find the 'State'
        for line in output.splitlines():
            if "Profile Settings" in line:
                current_profile = line.strip().replace(":", "")
            elif "State" in line and current_profile:
                # Find the line containing "State" and extract the value (ON/OFF)
                # Need to handle potential extra spaces/characters
                try:
                    state_value = line.split("State")[1].strip().split()[0].upper().rstrip(':')
                except IndexError:
                    state_value = "UNKNOWN"
                
                status[current_profile] = state_value
                current_profile = None # Reset after finding state for the section
        
        # --- DISPLAY RESULTS ---
        print("\n=== SYSTEM FIREWALL STATUS ===")
        all_on = True
        all_off = True

        for profile, state in status.items():
            print(f"- {profile:<30}: {state}")
            if state == 'OFF':
                all_on = False
            elif state == 'ON':
                all_off = False

        print("=========================================")
        
        if all_on and not status: # Handle case where no profiles were found but no error occurred
             print("=> Conclusion: No firewall profile status found in output.")
        elif all_on:
            print("=> Conclusion: FIREWALL IS **ON** for ALL Profiles.")
        elif all_off:
            print("=> Conclusion: FIREWALL IS **OFF** for ALL Profiles.")
        else:
            print("=> Conclusion: FIREWALL is in a **MIXED STATE**.")

        return status

    except subprocess.CalledProcessError as e:
        print("!!! ERROR while executing NETSH command !!!")
        print(f"Error (Stderr): {e.stderr.strip()}")
        print("\n* Common issue: The Python script needs to be run with **Administrator** privileges.")
        return None
    except Exception as ex:
        print(f"An unknown error occurred: {ex}")
        return None