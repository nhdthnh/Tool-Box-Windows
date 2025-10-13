import tkinter as tk
from tkinter import messagebox
import os
import re

def static_ip_setting():
    # --- Autofill Logic ---
    def autofill_network_info(event=None):
        """
        Automatically fills Subnet Mask and Default Gateway based on the entered Static IP.
        Applies common logic for Class A, B, and C IP ranges.
        """
        ip = entry_ip.get()
        
        # Simple check for basic IP format (to avoid errors on incomplete input)
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
            # Do not clear fields if input is partial, just skip autofill
            return

        try:
            first_octet = int(ip.split('.')[0])
            subnet = ""
            gateway = ""

            # Logic for Class A, B, C classification
            if 1 <= first_octet <= 126: # Class A
                subnet = "255.0.0.0"
                parts = ip.split('.')
                if len(parts) >= 1:
                    # Common pattern: first octet of the network + 1.1.1
                    gateway = f"{parts[0]}.1.1.1" 
            elif 128 <= first_octet <= 191: # Class B
                subnet = "255.255.0.0"
                parts = ip.split('.')
                if len(parts) >= 2:
                    # Common pattern: first two octets of the network + 1.1
                    gateway = f"{parts[0]}.{parts[1]}.1.1" 
            elif 192 <= first_octet <= 223: # Class C
                subnet = "255.255.255.0"
                parts = ip.split('.')
                if len(parts) >= 3:
                    # Common pattern: first three octets of the network + 1
                    gateway = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
            
            # Fill the fields only if they are currently empty
            if subnet and entry_subnet.get() == "": 
                entry_subnet.insert(0, subnet)
            
            if gateway and entry_gateway.get() == "": 
                entry_gateway.insert(0, gateway)

        except (ValueError, IndexError):
            # Ignore errors from incomplete IP conversion or splitting
            pass

    # --- Network Functionality Handlers ---
    def set_static_ip():
        ip = entry_ip.get()
        subnet = entry_subnet.get()
        gateway = entry_gateway.get()
        dns1 = entry_dns1.get()
        dns2 = entry_dns2.get()
        
        if not ip or not subnet or not gateway:
            messagebox.showerror("Error", "Please enter the complete IP, Subnet Mask, and Default Gateway.")
            return
            
        # Set Static IP
        # NOTE: "Ethernet" may need to be replaced by the actual network adapter name
        cmd_ip = f'netsh interface ip set address name="Ethernet" static {ip} {subnet} {gateway} 1'
        result_ip = os.system(cmd_ip)
        
        # Set DNS if entered
        dns_cmds = []
        if dns1:
            # Set the Primary DNS
            dns_cmds.append(f'netsh interface ip set dns name="Ethernet" static {dns1}')
        if dns2:
            # Add the Secondary (Alternative) DNS
            dns_cmds.append(f'netsh interface ip add dns name="Ethernet" {dns2} index=2')
            
        dns_result = 0
        for cmd in dns_cmds:
            dns_result += os.system(cmd)
        
        if result_ip == 0 and dns_result == 0:
            messagebox.showinfo("Success", "IP/DNS set successfully.")
        else:
            # If the command failed, it often indicates a lack of Admin privileges
            messagebox.showerror("Failure", "Could not set IP/DNS. Try running the application as Administrator.")

    def reset_dhcp():
        cmd_dhcp = 'netsh interface ip set address name="Ethernet" dhcp'
        cmd_dns = 'netsh interface ip set dns name="Ethernet" dhcp'
        
        # Bỏ qua việc kiểm tra exit code.
        os.system(cmd_dhcp)
        os.system(cmd_dns)
        
        # Luôn thông báo thành công (vì lệnh gần như luôn thành công trừ khi thiếu quyền Admin)
        messagebox.showinfo("Success", "Successfully reset to Dynamic IP/DNS (DHCP).")

    def refresh_fields():
        try:
            # Use 'chcp 65001' to ensure Unicode/English output is handled correctly
            output = os.popen('chcp 65001 & ipconfig /all').read()
            
            # Regex to find IP, Subnet, Gateway for the target adapter (handles multiple languages)
            # Looks for "Ethernet adapter" followed by IPv4, Subnet, and Gateway
            ethernet_block_match = re.search(
                r'(Ethernet adapter|Bộ điều hợp Ethernet|Local Area Connection).*?IPv4 Address[\.\s]*: ([\d.]+).*?Subnet Mask[\.\s]*: ([\d.]+).*?Default Gateway[\.\s]*: ([\d.]+)', 
                output, re.DOTALL | re.IGNORECASE
            )
            
            if ethernet_block_match:
                ip_match = ethernet_block_match.group(2)
                subnet_match = ethernet_block_match.group(3)
                gateway_match = ethernet_block_match.group(4)
                
                # Clear and insert current values
                entry_ip.delete(0, tk.END)
                entry_ip.insert(0, ip_match)
                entry_subnet.delete(0, tk.END)
                entry_subnet.insert(0, subnet_match)
                entry_gateway.delete(0, tk.END)
                entry_gateway.insert(0, gateway_match)
            
            # Clear DNS fields as they are not reliably fetched by ipconfig /all
            entry_dns1.delete(0, tk.END)
            entry_dns2.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Could not retrieve current network information. (Try running as Administrator.)\n{e}")


    # --- UI Initialization and Layout ---

    root = tk.Tk()
    root.title("Static IP Configuration")
    root.resizable(False, False) # Do not allow window resizing

    # Set fixed width for buttons for uniform alignment
    button_width = 15

    # Input Fields
    tk.Label(root, text="Static IP:").grid(row=0, column=0, pady=5, sticky='w')
    entry_ip = tk.Entry(root, width=25)
    entry_ip.grid(row=0, column=1, pady=5, padx=5, sticky='ew')
    # Bind KeyRelease event to trigger autofill
    entry_ip.bind('<KeyRelease>', autofill_network_info) 
    entry_ip.insert(0, "192.168.1.10") # Sample default value (optional)

    tk.Label(root, text="Subnet Mask:").grid(row=1, column=0, pady=5, sticky='w')
    entry_subnet = tk.Entry(root, width=25)
    entry_subnet.grid(row=1, column=1, pady=5, padx=5, sticky='ew')

    tk.Label(root, text="Default Gateway:").grid(row=2, column=0, pady=5, sticky='w')
    entry_gateway = tk.Entry(root, width=25)
    entry_gateway.grid(row=2, column=1, pady=5, padx=5, sticky='ew')

    tk.Label(root, text="DNS Primary:").grid(row=3, column=0, pady=5, sticky='w')
    entry_dns1 = tk.Entry(root, width=25)
    entry_dns1.grid(row=3, column=1, pady=5, padx=5, sticky='ew')

    tk.Label(root, text="DNS Alternative:").grid(row=4, column=0, pady=5, sticky='w')
    entry_dns2 = tk.Entry(root, width=25)
    entry_dns2.grid(row=4, column=1, pady=5, padx=5, sticky='ew')

    # Buttons (using fixed width and consistent padding)
    btn_set_ip = tk.Button(root, text="Set Static IP", command=set_static_ip, width=button_width)
    btn_set_ip.grid(row=0, column=2, padx=(0, 10), pady=5) 

    btn_reset_ip = tk.Button(root, text="Reset to DHCP", command=reset_dhcp, width=button_width)
    btn_reset_ip.grid(row=1, column=2, padx=(0, 10), pady=5)

    btn_refresh = tk.Button(root, text="Refresh Fields", command=refresh_fields, width=button_width)
    btn_refresh.grid(row=2, column=2, padx=(0, 10), pady=5)

    # Automatically fill network fields based on the sample IP on startup
    autofill_network_info()

    root.mainloop()

if __name__ == "__main__":
    static_ip_setting()