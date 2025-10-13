import psutil
import platform
import socket
import datetime
import os
import wmi 
# ... (other imports) ...

def get_size(bytes, suffix="B"):
    """Convert bytes size into a human-readable format."""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def sanitize_output(data):
    """Clean string to remove unprintable/non-ASCII characters (fixes bad format char errors)."""
    if data is None:
        return "N/A"
    try:
        s = str(data).strip()
        # Remove non-ASCII characters to avoid system format errors
        return s.encode('ascii', errors='ignore').decode('ascii')
    except Exception:
        return "String Error (Sanitize Error)"

def get_system_info():
    """Retrieves all system information and returns it as a string of Item: Value."""
    info = []
    
    info.append("="*40 + " SYSTEM INFORMATION " + "="*40)

    # --- A. OS AND COMPUTER INFORMATION ---
    uname = platform.uname()
    
    info.append(f"Computer Name (Hostname): {sanitize_output(uname.node)}")
    info.append(f"Operating System: {sanitize_output(uname.system)} {sanitize_output(uname.release)} ({sanitize_output(uname.version)})")
    info.append(f"Architecture: {sanitize_output(uname.machine)}")
    
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.datetime.fromtimestamp(boot_time_timestamp)
    info.append(f"Boot Time: {bt.strftime('%Y/%m/%d %H:%M:%S')}")
    
    # --- B. CPU INFORMATION ---
    info.append("\n" + "--- CPU INFORMATION ---")
    info.append(f"Processor: {sanitize_output(uname.processor)}")
    info.append(f"Physical Cores: {psutil.cpu_count(logical=False)}")
    info.append(f"Logical Cores (Threads): {psutil.cpu_count(logical=True)}")
    try:
        info.append(f"Max Frequency: {psutil.cpu_freq().max:.2f} Mhz")
        info.append(f"Current CPU Usage: {psutil.cpu_percent(interval=1)}%")
    except:
        info.append(f"Frequency: Undeterminable")


    # --- C. RAM (MEMORY) INFORMATION ---
    info.append("\n" + "--- MEMORY INFORMATION (RAM) ---")
    svmem = psutil.virtual_memory()
    info.append(f"Total RAM: {get_size(svmem.total)}")
    info.append(f"Used/Total RAM: {get_size(svmem.used)} / {get_size(svmem.total)}")
    info.append(f"RAM Usage (%): {svmem.percent}%")
    
    # RAM Module Details (Windows Only)
    if platform.system() == "Windows":
        try:
            c = wmi.WMI()
            for i, memory in enumerate(c.Win32_PhysicalMemory()):
                manufacturer_safe = sanitize_output(memory.Manufacturer)
                serial_safe = sanitize_output(memory.SerialNumber)
                
                info.append(f"  RAM Module {i+1} Vendor: {manufacturer_safe} ({get_size(int(memory.Capacity))})")
                info.append(f"  RAM Module {i+1} Speed/Serial: {memory.Speed} MT/s | {serial_safe}")
                
        except Exception as e:
            info.append(f"Error loading RAM details (WMI): {e}")

    # --- D. STORAGE (DISK) INFORMATION ---
    info.append("\n" + "--- STORAGE INFORMATION ---")
    for partition in psutil.disk_partitions():
        mountpoint_safe = sanitize_output(partition.mountpoint)
        
        info.append(f"Drive {sanitize_output(partition.device)} [{sanitize_output(partition.fstype)}]:")
        
        try:
            usage = psutil.disk_usage(mountpoint_safe)
            info.append(f"  Total Capacity: {get_size(usage.total)}")
            info.append(f"  Used: {usage.percent}% ({get_size(usage.used)} / {get_size(usage.total)})")
            
        except (PermissionError, SystemError, FileNotFoundError) as e:
            info.append(f"  [READ ERROR]: Skipping special drive/partition.")
            continue
    
    # --- E. NETWORK INFORMATION ---
    info.append("\n" + "--- NETWORK INFORMATION ---")
    
    # List of keywords to exclude (case-insensitive)
    exclude_keywords = [
        "vmware", "vmnet", "loopback", "vEthernet", 
        "microsoft wi-fi direct virtual adapter", "túnel", 
        "tunnel", "bluetooth"
    ]
    
    if_addrs = psutil.net_if_addrs()
    
    for interface_name, interface_addresses in if_addrs.items():
        
        # Check if the interface name contains any keyword in the exclusion list
        is_virtual = any(keyword in interface_name.lower() for keyword in exclude_keywords)
        
        # Get interface status
        stats = psutil.net_if_stats().get(interface_name)
        
        # Only show if the network card is UP AND NOT VIRTUAL
        if stats and stats.isup and not is_virtual: 
            
            interface_name_safe = sanitize_output(interface_name)
            info.append(f"[Interface] {interface_name_safe} (UP):")
            
            # Get and print address details
            for address in interface_addresses:
                if str(address.family) == 'AddressFamily.AF_INET':
                    info.append(f"  IP Address: {address.address}")
                    info.append(f"  Subnet Mask: {address.netmask}")
                    # Broadcast IP (if available)
                    if address.broadcast:
                        info.append(f"  Broadcast IP: {address.broadcast}")
                        
                elif str(address.family) == 'AddressFamily.AF_PACKET':
                    info.append(f"  MAC Address: {address.address}")
                    # Broadcast MAC (if available)
                    if address.broadcast:
                        info.append(f"  Broadcast MAC: {address.broadcast}")

            
    # --- NET I/O STATISTICS ---
    net_io = psutil.net_io_counters()
    info.append("\n" + "--- NETWORK TRAFFIC (I/O) STATISTICS ---")
    info.append(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    info.append(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")
    
    # Print the compiled information
    print("\n".join(info))

# Example usage (added for completeness, as the original code didn't have __main__ block):
if __name__ == '__main__':
    get_system_info()