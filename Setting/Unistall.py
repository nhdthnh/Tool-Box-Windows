import os

def open_uninstall_programs():
    """
    Directly opens the Control Panel to "Programs and Features" 
    (Add or Remove Programs).
    """
    try:
        # The command to directly open the "Programs and Features" window
        command = 'control appwiz.cpl'
        
        print(f"Executing command: {command}")
        
        # os.system executes the command in the operating system's shell
        os.system(command)
        
    except Exception as e:
        print(f"An error occurred while attempting to open the Control Panel: {e}")

# Call the function to open the window