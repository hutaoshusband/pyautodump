# =================================================================================================
#
#                                       PyAutoDump
#
# =================================================================================================
#
# Author: HUTAOSHUSBAND
# Date: August 2025
#
# -------------------------------------------------------------------------------------------------
#
#                                       ** What This Code Does **
#
# This script is a Command-Line Interface (CLI) tool designed to fully automate the process of
# reverse-engineering Python executables (*.exe) created with PyInstaller. It streamlines the
# entire workflow from extraction to decompilation, providing the user with the recovered
# Python source code.
#
# The workflow is as follows:
#
#   1.  **Dependency Check:** It automatically checks for a `requirements.txt` file and installs
#       the necessary Python packages (`decompyle3`) using pip.
#
#   2.  **File Selection:** The script launches a native OS file selection dialog, allowing the
#       user to safely browse and select the target `.exe` file for analysis.
#
#   3.  **Extraction:** It uses the well-known `pyinstxtractor.py` script to unpack the contents
#       of the PyInstaller executable. This process extracts all bundled files, including the
#       compiled Python bytecode (`.pyc` files) and the main PYZ archive.
#
#   4.  **Python Version Check:** During extraction, the script intelligently detects the Python
#       version used to build the original `.exe` and warns the user if their current Python
#       version does not match, which is crucial for successful decompilation.
#
#   5.  **Decompilation:** The script iterates through every extracted `.pyc` file. It then uses
#       the `decompyle3` command-line tool to convert the Python bytecode back into human-readable
#       Python source code (`.py` files). This is done by changing the working directory for
#       each file to ensure maximum reliability.
#
#   6.  **Organization & Cleanup:** After decompilation, all recovered `.py` source files are
#       moved into a neatly organized folder under the `output` directory. The temporary
#       `_extracted` folder is then automatically deleted to keep the workspace clean. ## ONLY WITH THE COMMAND CLEANUP in the code, the logic is not being used.
#
# -------------------------------------------------------------------------------------------------
#
#                                     ** Key Technologies Used **
#
#   -   **pyinstxtractor.py:** The core tool for unpacking PyInstaller archives. It correctly
#       handles different PyInstaller versions and reconstructs the file structure.
#       (This script must be present in the same directory as `main.py`).
#
#   -   **decompyle3:** A powerful Python cross-version decompiler that translates `.pyc` bytecode
#       back into `.py` source code. It is installed automatically via `requirements.txt`.
#
#   -   **Standard Libraries:**
#       -   `subprocess`: To run external processes like `pyinstxtractor` and `decompyle3`.
#       -   `os`, `shutil`: For robust file and directory manipulation (creating folders,
#         moving files, cleaning up).
#       -   `tkinter`: Used specifically to launch the native OS file selection dialog.
#       -   `re`: For parsing the output of `pyinstxtractor` to find the Python version.
#
# =================================================================================================



import subprocess
import sys
import os
import tkinter as tk
from tkinter import filedialog
import re
import shutil


DELETE_TEMP_FOLDER = True 

PYINST_PATH = os.path.join(os.path.dirname(__file__), "pyinstxtractor.py")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
REQUIREMENTS_FILE = "requirements.txt"

def check_requirements():
    """Checks for requirements.txt and installs dependencies."""
    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"[ERROR] '{REQUIREMENTS_FILE}' not found. Please create it and add 'decompyle3'.")
        sys.exit(1)
    
    print("[+] Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[+] Requirements are up to date.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install requirements: {e}")
        sys.exit(1)

def select_exe():
    """Opens a file dialog to select the EXE file."""
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Select an EXE file to extract",
        filetypes=[("Executable files", "*.exe")]
    )

def run_pyinstxtractor(exe_path):
    """Runs pyinstxtractor and returns the path to the extracted folder."""
    print(f"[+] Extracting {os.path.basename(exe_path)}...")
    if not os.path.exists(PYINST_PATH):
        print(f"[ERROR] pyinstxtractor.py not found in the project folder.")
        return None

    try:
        result = subprocess.run(
            [sys.executable, PYINST_PATH, exe_path],
            capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore'
        )
        print(result.stdout)

        match = re.search(r"Python version: ([0-9]+\.[0-9]+)", result.stdout)
        if match:
            required_version = match.group(1)
            current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            print(f"[INFO] EXE requires Python {required_version}. You are using Python {current_version}.")
            if required_version != current_version:
                print(f"[WARNING] For best results, run this script using 'py -{required_version} main.py'!")
        
        return os.path.basename(exe_path) + "_extracted"

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] pyinstxtractor.py failed:\n{e.stderr}")
        return None

def decompile_and_move(extracted_dir, final_out_dir):
    """Decompiles all .pyc files and moves the result to the final directory."""
    print(f"\n[+] Decompiling and moving source files to {final_out_dir}...")
    if os.path.exists(final_out_dir):
        shutil.rmtree(final_out_dir)
    os.makedirs(final_out_dir)

    scripts_dir = os.path.join(os.path.dirname(sys.executable), "Scripts")
    decompiler_path = os.path.join(scripts_dir, "decompyle3.exe")

    if not os.path.exists(decompiler_path):
        print(f"[ERROR] Decompiler not found at: {decompiler_path}")
        return False

    original_cwd = os.getcwd()
    success_count, fail_count = 0, 0

    for root, _, files in os.walk(extracted_dir):
        for file in files:
            if file.endswith(".pyc"):
                src_path = os.path.join(root, file)
                try:
                    os.chdir(root)
                    
                    subprocess.run(
                        [decompiler_path, file],
                        check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore'
                    )
                    success_count += 1
                except subprocess.CalledProcessError:
                    fail_count += 1
                finally:
                    os.chdir(original_cwd)

    print(f"[INFO] Decompilation finished: {success_count} succeeded, {fail_count} failed.")
    
    for root, _, files in os.walk(extracted_dir):
        for file in files:
            if file.endswith(".py"):
                src_path = os.path.join(root, file)
                relative_path = os.path.relpath(src_path, extracted_dir)
                target_path = os.path.join(final_out_dir, relative_path)
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                shutil.move(src_path, target_path)

    return success_count > 0

def cleanup(folder_path):
    """Deletes the temporary extracted folder."""
    if DELETE_TEMP_FOLDER:
        print("[+] Deleting temporary folder...")
        shutil.rmtree(folder_path)
        print("[+] Cleanup successful.")
    else:
        print(f"\n[INFO] DEBUG MODE: Temporary folder was NOT deleted at: {os.path.abspath(folder_path)}")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    check_requirements()

    exe_file = select_exe()
    if not exe_file:
        print("[INFO] No file selected. Exiting.")
        sys.exit(0)

    extracted_folder = run_pyinstxtractor(exe_file)

    if extracted_folder and os.path.exists(extracted_folder):
        output_subfolder = os.path.join(OUTPUT_DIR, os.path.basename(exe_file).replace(".exe", "_source"))
        if decompile_and_move(extracted_folder, output_subfolder):
            print(f"\n[+] SUCCESS! The source code is located in: output/")
        else:
            print("\n[ERROR] Decompilation failed.")
        
 
    else:
        print("[ERROR] Extraction failed.")
