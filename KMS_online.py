# ...existing code...
import subprocess
import sys
import platform
import ctypes
import os

# ====================================================================
# SYSTEM / GVLK KEY SUPPORT
# ====================================================================

# Mapping table for common Windows GVLK keys
GVLK_MAP = {
    # Volume License GVLK keys for common editions
    "PRO": "W269N-WFGWX-YVC9B-4J6C9-T83GX",           # Windows Pro
    "ENTERPRISE": "NPPR9-FWDCX-D2C8J-H872K-2YT43",    # Windows Enterprise
    "EDUCATION": "YN9G6-BBYCL-L4W7Q-KMTJR-3XJB2",      # Windows Education
    "STANDARD": "WCMDV-M8FGF-R69K2-XQGQD-2C9GW",      # Windows Server Standard
}

# Helper functions: is_admin, run_as_admin, execute_kms_command_skms_ckms
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if sys.platform != 'win32':
        return False
    python_exe = sys.executable
    script = os.path.abspath(sys.argv[0])
    args = f'"{script}"'
    ps_command = (
        'Start-Process '
        '-FilePath "' + python_exe + '" '
        '-ArgumentList ' + args + ' '
        '-Verb RunAs'
    )
    try:
        subprocess.Popen(
            ['powershell', '-Command', ps_command],
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return True
    except Exception as e:
        print(f"Error trying to relaunch as Admin: {e}")
        return False

def execute_kms_command_skms_ckms(command, success_message="Completed.", timeout_sec=10):
    print(f"   -> Executing: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='utf-8', check=False, timeout=timeout_sec)
        output = result.stdout.strip()
        if "successfully" in output.lower() or result.returncode == 0:
            print(f"   [RESULT]: SUCCESS! {success_message}")
            return True
        else:
            print(f"   [EXECUTION ERROR]: NOT SUCCESSFUL. Output: {output}")
            return False
    except subprocess.TimeoutExpired:
        print(f"   [ERROR]: Command canceled due to timeout ({timeout_sec} seconds).")
        return False
    except Exception as e:
        print(f"   [SYSTEM ERROR]: Unable to execute command: {e}")
        return False

def get_windows_gvl_key():
    """Auto-detect Windows edition via systeminfo and return a matching GVLK key."""
    try:
        systeminfo_command = 'systeminfo | findstr /B /C:"OS Name"'
        result = subprocess.run(systeminfo_command, shell=True, capture_output=True, text=True, encoding='utf-8')
        os_info = result.stdout.strip().split(':')
        
        if len(os_info) < 2:
            print("   ⚠️ Unable to read OS name from systeminfo.")
            return None
            
        # Full OS name (e.g., MICROSOFT WINDOWS 11 PRO)
        full_version = os_info[1].strip().upper()
        
        print(f"   -> Detected Windows edition: {full_version.title()}")
        
        # Try to match known keywords in the full version string
        for version_name, gvl_key in GVLK_MAP.items():
            if version_name in full_version:
                return gvl_key
                
        if "HOME" in full_version or "CORE" in full_version or "SINGLE LANGUAGE" in full_version:
            print("   ⚠️ NOTE: Home/Core/Single Language editions are not supported for KMS activation.")
            print("   Please upgrade to Pro/Enterprise to proceed.")
            return None
        
        print("   ⚠️ No matching GVLK key found for this edition in the mapping.")
        return None
        
    except Exception as e:
        print(f"   [AUTO-DETECT ERROR]: Unable to read Windows edition: {e}")
        return None

# ====================================================================
# ACTIVATION FUNCTIONS
# ====================================================================

kms_servers = [
    # Servers list (prioritized)
    "win.xdyxm11235.com",
    "s1.kms.cx",
    "kms.000606.xyz",
    "kms.03k.org",
    "kms.shuax.com",
    "kms.loli-best",
    "kms.loli-beer",
    "kms.sgtsoft.com",
    "kms.moeyuuko.top",
    "kms.digiboy.ir",
    "kms.kursktu.com",
    "kms.lucyinfo.top",
    "kms.sixyin.com",
    "kms-default.cangshui.net",
    "kms.moerats.com",
    "kms.ben-zhutop",
    "kms.akams.cn",
    "kms8.mspguides.com",
    "kms.kmszs123.cn",
    "kms.bigeo.cn",
    "kms.litbear.cn",
    "kms.ddddg.cn",
    "win.freekms.cn",
    "hq1.chinancce.com", "54.223.212.31", "kms.cnlic.com",
    "kms.chinancce.com", "kms.ddns.net", "franklv.ddns.net", "k.zpale.com",
    "m.zpale.com", "mvg.zpale.com", "kensol263.imwork.net:1688",
    "xykz.f3322.org", "kms789.com", "dimanyakms.sytes.net:1688",
    "kms.03k.org:1688"
]

def activate_windows(servers):
    """Activate Windows (Auto-detect GVLK -> /ipk -> /skms -> /ato)."""
    print("\n--- STARTING WINDOWS ACTIVATION ---")

    # STEP 1: Install detected GVLK if possible
    detected_gvl_key = get_windows_gvl_key()
    
    if detected_gvl_key:
        print("\n--- Step 1: Installing auto-detected GVLK ---")
        print(f"   -> Selected GVLK: {detected_gvl_key}")
        ipk_command = f"cscript //nologo /B %windir%\\system32\\slmgr.vbs /ipk {detected_gvl_key}"
        execute_kms_command_skms_ckms(ipk_command, success_message="GVLK installed.", timeout_sec=20)
    else:
        print("\n--- Step 1: COULD NOT INSTALL GVLK ---")
        print("   ⚠️ Windows can only be activated if a GVLK is already installed.")

    # STEP 2: Try servers
    success_flag = False
    for server in servers:
        print(f"\n--- Step 2: Trying server: {server} ---")
        
        skms_command = f"cscript //nologo /B %windir%\\system32\\slmgr.vbs /skms {server}"
        if execute_kms_command_skms_ckms(skms_command, success_message="KMS server set.", timeout_sec=10):
            
            ato_command = f"cscript //nologo %windir%\\system32\\slmgr.vbs /ato"
            print(f"   -> Executing: {ato_command} (waiting for activation result...)")
            
            try:
                ato_result = subprocess.run(ato_command, shell=True, capture_output=True, text=True, encoding='utf-8', check=False, timeout=5)
                output = ato_result.stdout.strip()
                
                if "successfully" in output.lower():
                    print(f"\n🎉 ACTIVATION SUCCESSFUL! Server: {server}")
                    print(f"   Full output:\n{output}")
                    success_flag = True
                    break
                elif "0xC004F074" in output or "0xC004F069" in output:
                    print(f"\n   [SERVER ERROR]: Activation failed (server rejected / wrong key). Full output:\n{output}")
                    
                    print("\n--- Clearing faulty server (/ckms) ---")
                    ckms_command = f"cscript //nologo /B %windir%\\system32\\slmgr.vbs /ckms"
                    execute_kms_command_skms_ckms(ckms_command, success_message="KMS server cleared.", timeout_sec=5)
                    continue 
                else:
                    print(f"\n   [OTHER ERROR]: Activation failed. Output:\n{output}")
                    continue
                    
            except subprocess.TimeoutExpired:
                print(f"   [ERROR]: /ato command timed out (5 seconds).")
                continue
            except Exception as e:
                print(f"   [SYSTEM ERROR]: Unable to run ATO command: {e}")
                continue
                
    if not success_flag:
        print("\n⚠️ Tried all servers but none activated Windows successfully.")
        return False
    else:
        print("\n--- Windows activation process finished ---")
        return True

# Helper to find Office path
def get_office_path():
    """Find Office installation folder (Office16 or Office15)."""
    office_versions = ['Office16', 'Office15']
    
    for version in office_versions:
        path_x64 = os.path.join(os.environ.get('ProgramFiles', ''), 'Microsoft Office', version)
        path_x86 = os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'Microsoft Office', version)

        if os.path.exists(os.path.join(path_x64, 'OSPP.VBS')):
            return path_x64
        elif os.path.exists(os.path.join(path_x86, 'OSPP.VBS')):
            return path_x86
            
    return None

def activate_office(servers):
    """Activate Office using ospp.vbs /sethst and /act with a 10s timeout."""
    print("\n--- STARTING OFFICE ACTIVATION ---")
    
    office_dir = get_office_path()
    if not office_dir:
        print("❌ ERROR: Office installation folder not found (Office15/Office16).")
        return False

    print(f"   -> Found Office at: {office_dir}")
    
    success_flag = False
    for server in servers:
        print(f"\n--- Trying server: {server} ---")
        
        sethst_command = f'cscript //nologo /B "{office_dir}\\OSPP.VBS" /sethst:{server}'
        if execute_kms_command_skms_ckms(sethst_command, success_message="KMS host set.", timeout_sec=5):
            
            act_command = f'cscript //nologo /B "{office_dir}\\OSPP.VBS" /act'
            if execute_kms_command_skms_ckms(act_command, success_message="Activation succeeded.", timeout_sec=5):
                print("\n🎉 OFFICE ACTIVATION SUCCESSFUL! Valid server found.")
                success_flag = True
                break
            
    if not success_flag:
        print("\n⚠️ Tried all servers but none activated Office successfully.")
        return False
    else:
        print("\n--- Office activation process finished ---")
        return True

def main_menu():
    if platform.system() != "Windows":
        print("⚠️ This tool only runs on Windows.")
        sys.exit(1)
        
    if not is_admin():
        print("⚠️ Administrator privileges are required to run this tool.")
        print("Trying to relaunch the script with elevated privileges...")
        if run_as_admin():
            sys.exit(0)
        else:
            sys.exit(1)
            
    while True:
        print("\n=============================================")
        print(" KMS ACTIVATION TOOL (WINDOWS / OFFICE)")
        print("=============================================")
        print("1. Activate Windows (Auto GVLK -> /skms & /ato)")
        print("2. Activate Office (ospp /sethst & /act)")
        print("3. Exit")
        
        choice = input("Enter your choice (1, 2, 3): ")
        
        if choice == '1':
            activate_windows(kms_servers)
        elif choice == '2':
            activate_office(kms_servers)
        elif choice == '3':
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid selection. Please enter 1, 2 or 3.")
            
    input("\nPress Enter to finish...")

# End of file
# ...existing code...