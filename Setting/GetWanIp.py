import requests
import json
import socket

def get_wan_ip():
    """Retrieves the WAN (Public IP) address by querying an API service."""
    try:
        # Use a simple and reliable API to get the IP (e.g., ipify)
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        response.raise_for_status() # Check for HTTP errors
        data = response.json()
        return data.get('ip')
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not retrieve WAN IP. Check network connection. Details: {e}")
        return None

def detect_ip_location(ip_address):
    """
    Detects the Geolocation of an IP address using the ip-api.com service.
    
    Note: This API is free but limited to 45 requests per minute.
    """
    if not ip_address:
        return {"Error": "No IP address provided for lookup."}
        
    # ip-api.com endpoint, explicitly requesting the desired fields
    api_url = f'http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query'
    
    print(f"\nLooking up location for IP: {ip_address}...")

    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'success':
            return data
        else:
            return {"Error": f"Lookup failed. API message: {data.get('message', 'Unknown error')}"}

    except requests.exceptions.RequestException as e:
        return {"Error": f"Error: Could not connect to the geolocation service. Details: {e}"}

# --- Program Execution ---

def display_ip_wan():
    """
    Orchestrates the process of getting the WAN IP and displaying its location data.
    """
    # Step 1: Get WAN IP
    wan_ip = get_wan_ip()

    if wan_ip:
        print(f"Your WAN IP address is: {wan_ip}")
        
        # Step 2: Look up location
        location_data = detect_ip_location(wan_ip)
        
        # Step 3: Display results
        print("\n--- IP GEOLOCATION RESULT ---")
        
        if "Error" in location_data:
            print(f"Status: FAILED - {location_data['Error']}")
        else:
            print(f"Status: SUCCESS")
            print(f"Country:       {location_data.get('country')} ({location_data.get('countryCode')})")
            print(f"Region/City:   {location_data.get('regionName')}, {location_data.get('city')}")
            print(f"ISP:           {location_data.get('isp')}")
            print(f"Timezone:      {location_data.get('timezone')}")
            print(f"Coordinates:   Lat={location_data.get('lat')}, Lon={location_data.get('lon')}")
    else:
        print("Could not proceed with geolocation because the WAN IP could not be retrieved.")

if __name__ == "__main__":
    display_ip_wan()