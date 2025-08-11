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
#   4.  **Python Version Check & Decompiler Selection:** During extraction, the script intelligently
#       detects the Python version (e.g., 3.8, 3.11, 3.13) used to build the original `.exe`.
#       Based on this version, it automatically selects the appropriate decompiler:
#         - **Python 3.13:** Switches to `pycdc.exe` for modern bytecode support.
#         - **Other Versions:** Defaults to `decompyle3` for broad compatibility.
#
#   5.  **Decompilation:** The script iterates through every extracted `.pyc` file and uses the
#       selected decompiler to convert the Python bytecode back into human-readable source code.
#
#   6.  **Organization & Cleanup:** After decompilation, all recovered `.py` source files are
#       moved into a neatly organized folder under the `output` directory. The temporary
#       `_extracted` folder is then automatically deleted.
#
# -------------------------------------------------------------------------------------------------
#
#                                     ** Key Technologies Used **
#
#   -   **pyinstxtractor.py:** The core tool for unpacking PyInstaller archives.
#   -   **decompyle3:** A powerful Python decompiler for versions up to ~3.8.
#   -   **pycdc (pycdc.exe):** A C++ based decompiler for handling newer Python versions like 3.13.
#       (Must be placed in the 'Tools' subfolder).
#
# =================================================================================================

import subprocess
import sys
import os
import tkinter as tk
from tkinter import filedialog
import re
import shutil

# --- Configuration ---
DELETE_TEMP_FOLDER = True 
REQUIREMENTS_FILE = "requirements.txt"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
PYINST_PATH = os.path.join(os.path.dirname(__file__), "pyinstxtractor.py")

# NEU: Pfad zum speziellen Dekompilierer für Python 3.13
PYCDC_PATH = os.path.join(os.path.dirname(__file__), "Tools", "pycdc.exe")


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
    """
    Runs pyinstxtractor, detects Python version, and returns the extracted folder path and version.
    """
    print(f"[+] Extracting {os.path.basename(exe_path)}...")
    if not os.path.exists(PYINST_PATH):
        print(f"[ERROR] pyinstxtractor.py not found in the project folder.")
        return None, None

    try:
        result = subprocess.run(
            [sys.executable, PYINST_PATH, exe_path],
            capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore'
        )
        print(result.stdout)

        # Suchen nach der Python-Version (z.B. 3.13)
        match = re.search(r"Python version: (\d+\.\d+)", result.stdout)
        python_version = None
        if match:
            python_version = match.group(1)
            current_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            print(f"[INFO] EXE was built with Python {python_version}. You are using Python {current_version}.")
            if python_version != current_version:
                print(f"[WARNING] For best results, your local Python version should match the EXE's version!")
        else:
            print("[WARNING] Could not determine Python version from extraction log.")
        
        extracted_folder = os.path.basename(exe_path) + "_extracted"
        return extracted_folder, python_version

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] pyinstxtractor.py failed:\n{e.stderr}")
        return None, None

def decompile_and_move(extracted_dir, final_out_dir, python_version):
    """
    Decompiles all .pyc files using the appropriate decompiler based on Python version.
    """
    print(f"\n[+] Decompiling source files for Python {python_version or 'unknown'}...")
    if os.path.exists(final_out_dir):
        shutil.rmtree(final_out_dir)
    os.makedirs(final_out_dir)

    decompiler_path = ""
    is_pycdc = False

    # NEU: Logik zur Auswahl des Dekompilierers
    if python_version == "3.13":
        print("[INFO] Python 3.13 detected. Switching to pycdc decompiler.")
        decompiler_path = PYCDC_PATH
        is_pycdc = True
        if not os.path.exists(decompiler_path):
            print(f"[ERROR] Python 3.13 decompiler not found at: {decompiler_path}")
            print("[INFO] Please place 'pycdc.exe' in the 'Tools' subfolder.")
            return False
    else:
        print("[INFO] Using default 'decompyle3' decompiler.")
        scripts_dir = os.path.join(os.path.dirname(sys.executable), "Scripts")
        decompiler_path = os.path.join(scripts_dir, "decompyle3.exe")

    if not is_pycdc and not os.path.exists(decompiler_path):
        print(f"[ERROR] Default decompiler not found at: {decompiler_path}")
        return False

    original_cwd = os.getcwd()
    success_count, fail_count = 0, 0

    for root, _, files in os.walk(extracted_dir):
        for file in files:
            if file.endswith(".pyc"):
                src_path = os.path.join(root, file)
                # Zielpfad für die .py-Datei
                target_py_path = src_path.replace(".pyc", ".py")
                
                try:
                    # NEU: Angepasste Befehle für beide Dekompilierer
                    if is_pycdc:
                        # pycdc gibt den Code auf stdout aus, wir leiten ihn in eine Datei um
                        with open(target_py_path, 'w', encoding='utf-8') as f_out:
                            subprocess.run(
                                [decompiler_path, src_path],
                                check=True, stdout=f_out, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore'
                            )
                    else:
                        # decompyle3 erstellt die Datei selbst, wir müssen nur das Verzeichnis wechseln
                        os.chdir(root)
                        subprocess.run(
                            [decompiler_path, file],
                            check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore'
                        )
                        os.chdir(original_cwd)
                    
                    success_count += 1
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    # print(f"Failed on {file}: {e.stderr if hasattr(e, 'stderr') else e}") # Uncomment for debug
                    fail_count += 1
                finally:
                    if not is_pycdc:
                        os.chdir(original_cwd) # Nur für decompyle3 zurückwechseln

    print(f"[INFO] Decompilation finished: {success_count} succeeded, {fail_count} failed.")
    
    # Verschiebe alle erstellten .py Dateien
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
    if DELETE_TEMP_FOLDER and os.path.exists(folder_path):
        print("[+] Deleting temporary folder...")
        shutil.rmtree(folder_path)
        print("[+] Cleanup successful.")
    elif not DELETE_TEMP_FOLDER:
        print(f"\n[INFO] DEBUG MODE: Temporary folder was NOT deleted at: {os.path.abspath(folder_path)}")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    check_requirements()

    exe_file = select_exe()
    if not exe_file:
        print("[INFO] No file selected. Exiting.")
        sys.exit(0)

    # NEU: Empfange die Python-Version vom Extraktor
    extracted_folder, py_version = run_pyinstxtractor(exe_file)

    if extracted_folder and os.path.exists(extracted_folder):
        output_subfolder = os.path.join(OUTPUT_DIR, os.path.basename(exe_file).replace(".exe", "_source"))
        
        # NEU: Übergebe die Version an die Dekompilierungsfunktion
        if decompile_and_move(extracted_folder, output_subfolder, py_version):
            print(f"\n[+] SUCCESS! The source code is located in: {os.path.abspath(output_subfolder)}")
        else:
            print("\n[ERROR] Decompilation failed. Check logs for details.")
        
        cleanup(extracted_folder)
    else:
        print("[ERROR] Extraction failed.")

