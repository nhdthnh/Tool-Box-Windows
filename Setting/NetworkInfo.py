import subprocess
import re

def run_ipconfig_and_get_output():
    """Runs the ipconfig /all command and returns the output."""
    try:
        # Use 'cp850' encoding for Windows command line output
        result = subprocess.run(
            ['ipconfig', '/all'],
            capture_output=True,
            text=True,
            encoding='cp850',
            check=True
        )
        return result.stdout
    except Exception as e:
        print(f"Error: {e}")
        return None
        
def ipconfig():
    """
    Executes ipconfig /all and prints the raw output, or an error message.
    """
    output = run_ipconfig_and_get_output()
    if output:
        print("\n--- IPCONFIG /ALL RESULT ---")
        print(output)
    else:
        print("Could not retrieve network information.")

# --- Program Execution ---
if __name__ == "__main__":
    ipconfig()