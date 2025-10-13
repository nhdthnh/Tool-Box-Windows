import winreg # Requires pip install pywin32
import subprocess
import platform
import re

# --- GENERAL SUPPORT FUNCTION (CRITICAL) ---

def execute_system_command(command, command_name, admin_required=True):
    """Executes a system command and returns the success status and result string."""
    if platform.system().lower() != "windows":
        return False, f"Error: {command_name} is only supported on Windows."
        
    print(f"\n--- Executing: {command_name}...")
    # Use 'cp850' encoding for Windows console compatibility
    encoding_type = 'cp850' 
    
    try:
        # Run command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding=encoding_type,
            check=True,
            timeout=15 
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.strip() or e.stdout.strip()
        # Explicitly checking for privilege errors
        if admin_required and ("access is denied" in error_output.lower() or "administrator" in error_output.lower()):
            return False, f"ERROR {command_name}: Requires Administrator privileges."
        return False, f"SYSTEM ERROR {command_name}: {error_output}"
    except Exception as e:
        return False, f"UNKNOWN ERROR {command_name}: {e}"

# --- GET STATUS FUNCTION (FIXED) ---

def get_netsh_global_status():
  """Retrieves the current status of global TCP settings using netsh."""
  command = ['netsh', 'int', 'tcp', 'show', 'global']
  success, output = execute_system_command(command, "Get Global TCP Status", admin_required=False)
  
  status = {}
  if success:
    # Capture whole status strings after ":", trim spaces
    def find_status(label):
      pattern = rf"{label}\s*:\s*([^\r\n]+)"
      match = re.search(pattern, output, re.IGNORECASE)
      if match:
        return match.group(1).strip().lower()
      else:
        return 'unknown'

    status['Autotuning'] = find_status("Receive Window Auto-Tuning Level")
    status['Chimney'] = find_status("Chimney Offload State")
    status['RSS'] = find_status("Receive Side Scaling State")

  else:
    status['Autotuning'] = 'unknown'
    status['Chimney'] = 'unknown'
    status['RSS'] = 'unknown'

  return status


# --- OPTIMIZATION FUNCTIONS (TOGGLE LOGIC) ---

def toggle_autotuning_level():
    """Toggles the Window Scaling (TCP Window Size) & Auto Tuning state."""
    current_status = get_netsh_global_status().get('Autotuning', 'unknown')
    
    if current_status == 'normal':
        level = 'disabled'
        action_name = "DISABLE Window Scaling/Auto Tuning"
    elif current_status == 'disabled':
        level = 'normal'
        action_name = "ENABLE Window Scaling/Auto Tuning"
    else:
        return False, f"Status unknown ({current_status}). Skipping toggle."

    command = ['netsh', 'int', 'tcp', 'set', 'global', f'autotuninglevel={level}']
    return execute_system_command(command, action_name)

def toggle_rss_multicore():
    """Toggles the RSS Multi-Core state."""
    current_status = get_netsh_global_status().get('RSS', 'unknown')
    
    if current_status == 'enabled':
        state = 'disabled'
        action_name = "DISABLE RSS Multi-Core"
    elif current_status == 'disabled':
        state = 'enabled'
        action_name = "ENABLE RSS Multi-Core"
    else:
        return False, f"Status unknown ({current_status}). Skipping toggle."
        
    command = ['netsh', 'interface', 'tcp', 'set', 'global', f'rss={state}']
    return execute_system_command(command, action_name)

def toggle_tcp_chimney():
  current_status = get_netsh_global_status().get('Chimney', 'unknown')

  # Treat 'enabled' and 'automatic' as enabled states
  if current_status in ('enabled', 'automatic'):
    state = 'disabled'
    action_name = "DISABLE TCP Chimney Offload"
  elif current_status == 'disabled':
    state = 'automatic' # Recommended enable state
    action_name = "ENABLE TCP Chimney Offload (set to 'automatic')"
  else:
    return False, f"Status unknown ({current_status}). Skipping toggle."

  command = ['netsh', 'int', 'tcp', 'set', 'global', f'chimney={state}']
  return execute_system_command(command, action_name)


# --- NAGLE ALGORITHM (REGISTRY) FUNCTIONS ---

def get_nagle_status_from_registry():
    """Checks Nagle Algorithm status (1=Disabled, 0=Enabled) across all interfaces."""
    REG_PATH = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
    NAGLE_VALUE_KEY = "TcpNoDelay"
    
    try:
        aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        aKey = winreg.OpenKey(aReg, REG_PATH)
        num_subkeys = winreg.QueryInfoKey(aKey)[0]
        
        # Check the status of the first interface found that has the key
        for i in range(num_subkeys):
            subkey_name = winreg.EnumKey(aKey, i)
            interface_path = f"{REG_PATH}\\{subkey_name}"
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, interface_path, 0, winreg.KEY_READ) as key:
                try:
                    # Reading the value: 1 means TcpNoDelay is ON (Nagle is OFF)
                    value, _ = winreg.QueryValueEx(key, NAGLE_VALUE_KEY)
                    return True, value # Return True and the DWORD value (1 or 0)
                except FileNotFoundError:
                    # Key might not exist, which usually means default behavior (Nagle is ON/0)
                    continue 
        
        return True, 0 # Default if key is not found anywhere: Nagle is ON (value 0)
    except PermissionError:
        return False, "Permission Denied: Run as Administrator to check Nagle status."
    except Exception as e:
        return False, f"Registry Read Error: {e}"

def toggle_nagle_algorithm():
    """Toggles the Nagle Algorithm (TcpNoDelay Registry key) state."""
    
    success, current_value = get_nagle_status_from_registry()
    
    if not success:
        return False, f"Failed to check current Nagle status: {current_value}"

    # current_value = 1 (Nagle Disabled) -> next_value = 0 (Nagle Enabled)
    # current_value = 0 (Nagle Enabled) -> next_value = 1 (Nagle Disabled)
    disable_nagle = not bool(current_value) 
    
    REG_PATH = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
    NAGLE_VALUE_KEY = "TcpNoDelay"
    value_to_set = 1 if disable_nagle else 0
    
    action = f"{'DISABLE' if disable_nagle else 'ENABLE'} Nagle Algorithm (Registry)"
    
    print(f"\n--- Current Nagle Status (TcpNoDelay={current_value}). Toggling to {value_to_set} ({action}) ---")
    
    try:
        aReg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        aKey = winreg.OpenKey(aReg, REG_PATH)
        num_subkeys = winreg.QueryInfoKey(aKey)[0]
        
        for i in range(num_subkeys):
            subkey_name = winreg.EnumKey(aKey, i)
            interface_path = f"{REG_PATH}\\{subkey_name}"
            
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, interface_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, NAGLE_VALUE_KEY, 0, winreg.REG_DWORD, value_to_set)
                
        return True, f"Success: {action} applied across all interfaces. (Requires restart)"
        
    except PermissionError:
        return False, f"ERROR {action}: The script must be run with Administrator privileges."
    except Exception as e:
        return False, f"SYSTEM ERROR {action}: {e}"

# --- MAIN TOGGLE FUNCTION ---

def toggle_all_network_optimizations():
    """
    Toggles the state of all network optimization settings based on current status.
    """
    results = []

    print("\n\n#####################################################")
    print("## STARTING NETWORK OPTIMIZATION TOGGLE SEQUENCE ##")
    print("#####################################################")
    
    # 1. Autotuning / Window Scaling
    success, msg = toggle_autotuning_level()
    results.append(f"Auto Tuning/Window Scaling: {'SUCCESS' if success else 'FAILED'} - {msg}")
    
    # 2. RSS Multi-Core
    success, msg = toggle_rss_multicore()
    results.append(f"RSS Multi-Core: {'SUCCESS' if success else 'FAILED'} - {msg}")
    
    # 3. TCP Chimney Offload
    success, msg = toggle_tcp_chimney()
    results.append(f"TCP Chimney Offload: {'SUCCESS' if success else 'FAILED'} - {msg}")
    
    # 4. Nagle Algorithm
    success, msg = toggle_nagle_algorithm()
    results.append(f"Nagle Algorithm: {'SUCCESS' if success else 'FAILED'} - {msg}")

    print("\n\n--- SUMMARY OF ALL ACTIONS ---")
    print("\n".join(results))
    print("----------------------------------------")
    print("\nNOTE: Nagle Algorithm change requires a **system restart** to take full effect.")


# --- Program Execution ---
if __name__ == "__main__":
    toggle_all_network_optimizations()