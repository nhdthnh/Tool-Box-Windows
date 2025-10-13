import requests
import subprocess
import platform
import json

# --- IP Retrieval and Geolocation Functions (modified to get Timezone) ---

def get_wan_ip():
    """
    Retrieves the system's public (WAN) IP address using an external service.
    """
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        response.raise_for_status() 
        return response.json().get('ip')
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not retrieve WAN IP. {e}")
        return None

def detect_ip_location(ip_address):
    """
    Uses an external API to get location data, specifically the IANA timezone.
    """
    # Use API to get fields: status, message, timezone
    api_url = f'http://ip-api.com/json/{ip_address}?fields=status,message,timezone'
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'success':
            return data.get('timezone') # Returns IANA timezone name
        return None
    except requests.exceptions.RequestException:
        return None

# --- Timezone Mapping Table and Function ---

# NOTE: This mapping table is critical and must accurately match Windows Standard Names.
TIMEZONE_MAPPING = {
    "Asia/Ho_Chi_Minh": "SE Asia Standard Time",
    "Asia/Bangkok": "SE Asia Standard Time",
    "Asia/Jakarta": "SE Asia Standard Time",
    "Europe/London": "GMT Standard Time",
    "America/New_York": "Eastern Standard Time",
    "America/Los_Angeles": "Pacific Standard Time",
    "Asia/Tokyo": "Tokyo Standard Time",
    "Australia/Sydney": "AUS Eastern Standard Time",
    "Europe/Paris": "Central Europe Standard Time",
}

def map_iana_to_windows_tz(iana_name):
    """
    Maps an IANA timezone name to its corresponding Windows Standard Name.
    """
    return TIMEZONE_MAPPING.get(iana_name, None)

# --- Windows Timezone Setting Function ---

def set_timezone_windows(timezone_name):
    """
    Executes the tzutil command to set the timezone on a Windows system.
    """
    if platform.system() != "Windows":
        print("This command is only applicable to the Windows operating system.")
        return

    command = ['tzutil', '/s', timezone_name]
    print(f"\nExecuting command: {' '.join(command)}")

    try:
        # The tzutil /s command REQUIRES ADMINISTRATOR PRIVILEGES
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            creationflags=subprocess.CREATE_NO_WINDOW # Minimize the console window popping up
        )
        print(f"[✅ SUCCESS] Timezone successfully set to: {timezone_name}")
        
    except subprocess.CalledProcessError as e:
        print("\n--- EXECUTION ERROR ---")
        print(f"Command failed with return code {e.returncode}. Check the timezone name or **Administrator privileges**.")
        print(f"Standard Error (Stderr):\n{e.stderr.strip()}")
        
    except Exception as e:
        print(f"An unknown error occurred: {e}")

# --- Main Orchestration Function ---

def set_windows_timezone_by_ip():
    """
    Automated process: Get IP -> Geolocation -> Set Windows Timezone.
    """
    if platform.system() != "Windows":
        print("This feature only supports Windows.")
        return

    print("--- STARTING TIMEZONE SYNCHRONIZATION FROM WAN IP ---")
    
    # 1. Get WAN IP
    wan_ip = get_wan_ip()
    if not wan_ip:
        return

    # 2. Geolocation and get IANA timezone name
    iana_tz = detect_ip_location(wan_ip)
    if not iana_tz:
        print("Could not retrieve timezone information from the geolocation service.")
        return
        
    print(f"Found IANA Timezone: {iana_tz}")

    # 3. Map to Windows name
    windows_tz = map_iana_to_windows_tz(iana_tz)

    if not windows_tz:
        print(f"[❌ FAILED] Could not find a corresponding Windows timezone name for {iana_tz} in the mapping table.")
        return
        
    print(f"Corresponding Windows Timezone Name: {windows_tz}")

    # 4. Set Windows Timezone
    set_timezone_windows(windows_tz)

# --- Program Execution ---

if __name__ == "__main__":
    set_windows_timezone_by_ip()