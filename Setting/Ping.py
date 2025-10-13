import subprocess
import platform

def run_ping_test_task(target_ip='8.8.8.8', count=4):
    """
    Executes a ping command to the target IP address.

    Args:
        target_ip (str): The target IP address or domain name to ping (default: 8.8.8.8).
        count (int): The number of pings to send (default: 4).

    Returns:
        str: The raw ping output or an error message.
    """
    # Determine the ping argument based on the operating system
    # '-c' for Linux/macOS, '-n' for Windows
    if platform.system().lower() == "windows":
        command = ['ping', '-n', str(count), target_ip]
        # Use a standard encoding for English output in Windows command prompt (default is often fine)
        encoding_type = 'utf-8' 
    else:
        command = ['ping', '-c', str(count), target_ip]
        encoding_type = 'utf-8'

    print(f"Running command: {' '.join(command)}...")

    try:
        # Execute the command and capture the output
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding=encoding_type,
            timeout=10  # Set a timeout for the command
        )
        
        # Check the return code
        if result.returncode == 0:
            # Ping succeeded
            return result.stdout
        else:
            # Ping failed (e.g., unreachable host)
            error_message = f"ERROR (Return Code {result.returncode}):\n{result.stdout.strip()}"
            if result.stderr:
                 error_message += f"\n{result.stderr.strip()}"
            return error_message

    except subprocess.TimeoutExpired:
        return "ERROR: Ping command timed out."
    except FileNotFoundError:
        return "ERROR: 'ping' command not found on the system (check your PATH environment variable)."
    except Exception as e:
        return f"UNKNOWN ERROR: {e}"

# Run the test
def run_ping_test():
    """Wrapper function to execute the ping test and print the output."""
    ping_output = run_ping_test_task()
    print("\n--- PING TEST RESULT ---")
    print(ping_output)

if __name__ == '__main__':
    run_ping_test()