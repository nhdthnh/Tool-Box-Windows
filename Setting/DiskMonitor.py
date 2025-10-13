import platform 
import subprocess 
import os 
# Optional import for psutil
try:
    import psutil
except ImportError:
    psutil = None
import json
import datetime

def run_diskpart_and_extract_ltr():
    """
    Runs the diskpart command, sends 'list volume', and parses the output 
    to extract drive letters (Ltr) into a list.
    Only runs on Windows.
    
    Returns:
        list: List of drive letters (e.g., ['D', 'C']). Returns an empty list on error.
    """
    # Check OS before running Windows command
    if platform.system().lower() != "windows":
        print("[WARNING] diskpart functionality only works on Windows.")
        return []

    drive_letters = []
    
    try:
        # 1. Define command and input data
        diskpart_command = 'diskpart'
        # Send 'list volume' and 'exit' to close diskpart when done
        diskpart_input = "list volume\nexit\n"
        
        # 2. Run command and pass input
        print(f"--- Running command: {diskpart_command} and sending input: 'list volume' ---")
        
        proc = subprocess.run(
            diskpart_command,
            shell=True, 
            input=diskpart_input,
            capture_output=True,
            text=True,
            encoding='cp850', # Encoding for CMD output (important for special characters)
            check=True,
            timeout=10
        )
        
        # 3. Parse result and extract Ltr
        raw_output = proc.stdout
        lines = raw_output.splitlines()
        
        # Print raw output for inspection
        print("\n=======================================================")
        print("                 RAW DISKPART OUTPUT")
        print("=======================================================")
        print(raw_output)
        print("=======================================================\n")

        # Find header and position of the "Ltr" column
        header_idx = None
        start_line = 0
        for i, line in enumerate(lines):
            if 'Ltr' in line and 'Volume' in line:
                header_idx = line.find('Ltr')
                start_line = i + 1
                break

        # If header is found, skip separator line (---) and start reading data
        if header_idx is not None:
            for line in lines[start_line:]:
                # skip separator or empty lines
                if not line.strip() or set(line.strip()) <= set('-'):
                    continue

                # Get the part at the Ltr column position (use slice to prevent IndexError)
                segment = line[header_idx:header_idx+3] if header_idx < len(line) else ''
                ltr = segment.strip()

                # If the extracted part is a single letter, treat it as a drive letter
                if len(ltr) == 1 and ltr.isalpha():
                    drive_letters.append(ltr)
                else:
                    # fallback: search for single-character token in the line (added safety)
                    parts = line.split()
                    for tok in parts:
                        if len(tok) == 1 and tok.isalpha():
                            drive_letters.append(tok)
                            break
        else:
            # If header is not found, try a global token-based method
            for line in lines:
                parts = line.split()
                for tok in parts:
                    if len(tok) == 1 and tok.isalpha():
                        drive_letters.append(tok)
                        break

    except Exception as e:
        # If diskpart fails to run, or times out
        print(f"[ERROR] Could not run diskpart command or failed parsing: {e!r}")
        
    return drive_letters

def print_device_usage_for_letters(letters):
    """
    Receives a list of drive letters (['C','D',...']) -> prints DeviceID and % usage.
    Uses psutil if available, otherwise calls PowerShell to get Size/FreeSpace.
    """
    if not letters:
        print("[INFO] No drive letters to check.")
        return

    for l in letters:
        # Standardize the letter (e.g., 'C' or 'C:' -> 'C:')
        drive = l.strip().upper().rstrip(':')
        device = f"{drive}:"
        mount = f"{device}\\"

        # Try using psutil if imported successfully
        if psutil:
            try:
                usage = psutil.disk_usage(mount)
                total_gb = usage.total / (1024**3)
                used_gb = usage.used / (1024**3)
                percent = usage.percent
                print(f"{device} - Used {used_gb:.1f}GB / {total_gb:.1f}GB ({percent:.1f}%)")
                continue
            except Exception:
                # if psutil fails for this mount, fallback to PowerShell
                pass

        # Fallback: call PowerShell to get Size and FreeSpace
        try:
            ps_cmd = (
                "Get-WmiObject Win32_LogicalDisk -Filter \"DeviceID='{0}'\" "
                "| Select-Object Size,FreeSpace | ConvertTo-Json"
            ).format(device)
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                encoding='cp850',
                timeout=5
            )
            out = proc.stdout.strip()
            if not out:
                print(f"[WARN] Failed to get information via PowerShell for {device}")
                continue

            data = json.loads(out)
            if isinstance(data, list):
                data = data[0] if data else {}

            size = int(data.get('Size', 0) or 0)
            free = int(data.get('FreeSpace', 0) or 0)

            if size <= 0:
                print(f"[WARN] Invalid Size for {device}: {size!r}")
                continue

            used = size - free
            percent = used / size * 100.0
            print(f"{device} - Used {used/1024**3:.1f}GB / {size/1024**3:.1f}GB ({percent:.1f}%)")

        except Exception as e:
            print(f"[ERROR] Could not retrieve information for {device}: {e!r}")

# --- PROGRAM EXECUTION ---
if __name__ == '__main__':
    print("--- RUNNING DISKPART COMMAND AND EXTRACTING DRIVE LETTERS ---")
    
    # Run function to get list of drive letters
    letters = run_diskpart_and_extract_ltr()
    print(f"\n✅ Extracted Drive Letters: {letters}")
    if letters:
        print_device_usage_for_letters(letters)
    else:
        print("\n❌ No valid drive letters found or extracted.")

    print("-------------------------------------------------------")