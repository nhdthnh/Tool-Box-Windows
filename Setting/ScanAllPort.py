import subprocess
import re
import threading
from queue import Queue
import time
import platform
import sys
import socket

# --- CONFIGURATION ---
# Note: For netstat parsing, a high thread count isn't strictly necessary 
# but is kept here for multi-threading practice.
THREAD_COUNT = 5 
TIMEOUT = 0.5

# Global variables
netstat_info = [] # Stores final (Port, State, Foreign_Address, Service) tuples
print_lock = threading.Lock()
q = Queue() 

# --- CORE FUNCTION: RUN NETSTAT AND PARSE OUTPUT ---

def get_local_netstat_info():
    """
    Runs 'netstat -an' on Windows and parses lines containing 'LISTEN' or 'ESTABLISHED'.
    Returns a list of dictionaries: [{'port': 80, 'state': 'LISTENING', 'foreign': '0.0.0.0:0'}, ...]
    """
    if platform.system().lower() != "windows":
        print("This command works effectively only on Windows.")
        return []

    # Use 'cp850' encoding common in Windows console
    command = ['netstat', '-an']
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='cp850',
            check=True,
            timeout=15
        )
        output = result.stdout
    except Exception as e:
        print(f"[ERROR] Could not run netstat. Details: {e}")
        return []

    parsed_data = []
    # Regex to find TCP lines, extract Local Address (IP:Port), Foreign Address, and State
    regex = re.compile(r"TCP\s+(?P<local_ip>[\d\.\:]+):(?P<port>\d+)\s+(?P<foreign_addr>[\d\.\:]+:\d+)\s+(?P<state>\w+)")

    for line in output.splitlines():
        match = regex.search(line)
        if match:
            state = match.group('state')
            # Only interested in LISTEN and ESTABLISHED states
            if state in ["LISTENING", "ESTABLISHED"]:
                try:
                    port = int(match.group('port'))
                    data = {
                        'port': port,
                        'state': state,
                        'local_ip': match.group('local_ip'),
                        'foreign_addr': match.group('foreign_addr')
                    }
                    parsed_data.append(data)
                except ValueError:
                    continue # Skip if port is not a number

    return parsed_data

# --- WORKER FUNCTION (SIMPLIFIED) ---

def worker():
    """Worker function to process items from the Queue."""
    global netstat_info
    while True:
        data = q.get()
        if data is None:
            q.task_done()
            break
            
        port = data['port']
        state = data['state']
        
        try:
            # Attempt to get the service name (will succeed for standard ports)
            service = socket.getservbyport(port, "tcp")
        except OSError:
            service = "Unknown"
                
        # Add the service info to the parsed data
        data['service'] = service
        
        with print_lock:
            # Display the result directly
            print(f"[{state:<11}] {data['local_ip']}:{port:<5} -> {data['foreign_addr']:<20} (Service: {service})")
            
        netstat_info.append(data)
        q.task_done()

# --- MAIN ORCHESTRATION FUNCTION ---

def start_local_netstat_analysis():
    """Orchestrates the netstat execution and analysis."""
    
    global netstat_info, q
    netstat_info = [] 
    
    print(f"\n--- STARTING LOCAL NETSTAT ANALYSIS ---")
    
    # 1. Run netstat and parse
    raw_data = get_local_netstat_info()
    if not raw_data:
        print("\n[ERROR] No TCP connections found or netstat could not be executed.")
        return

    print(f"Found {len(raw_data)} TCP connections (LISTEN/ESTABLISHED). Analyzing services...")
    print("-" * 80)
    
    start_time = time.time()
    
    # 2. Populate the Queue
    for item in raw_data:
        q.put(item)
        
    threads = []
    # 3. Initialize and start worker threads
    for i in range(THREAD_COUNT):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)
        
    # 4. Wait for all tasks to complete
    q.join()
    
    # 5. Shut down worker threads
    for i in range(THREAD_COUNT):
        q.put(None)
    for t in threads:
        t.join() 
        
    end_time = time.time()
    
    # --- SUMMARY DISPLAY ---
    print("=" * 80)
    print("ANALYSIS COMPLETE.".center(80))
    print(f"Total Time: {end_time - start_time:.2f} seconds")
    print(f"Total Connections Analyzed: {len(netstat_info)}")
    
# ---
if __name__ == '__main__':
    start_local_netstat_analysis()