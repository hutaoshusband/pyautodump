# PyAutoDump - Automated PyInstaller Extractor & Decompiler

`PyAutoDump` is an automated tool that builds upon the original **[pyinstxtractor](https://github.com/extremecoders-re/pyinstxtractor )**. While the original script extracts the contents of a PyInstaller executable, `PyAutoDump` automates the entire reverse-engineering workflow: **extraction, decompilation, and organization.**

This project handles the tedious manual steps, providing you with the final source code in a clean output folder.

## Core Technology

This tool uses the original `pyinstxtractor.py` script as its extraction engine. It supports all versions that `pyinstxtractor` does, including PyInstaller versions 2.0 through 6.x and beyond.

The key difference is the automation layer built on top.

## Features

-   **Fully Automated:** Runs the entire extraction and decompilation process with a single command.
-   **Automatic Dependency Installation:** Installs the `decompyle3` decompiler automatically from `requirements.txt`.
-   **User-Friendly File Selection:** Launches a native file dialog to select the target `.exe`.
-   **Intelligent Decompilation:** Automatically finds all `.pyc` files and decompiles them using `decompyle3`.
-   **Smart Version Check:** Warns you if your Python version doesn't match the one used to build the `.exe`.
-   **Clean Output:** Organizes all recovered source code into a dedicated `output` folder and deletes temporary files.

## Usage

To run the script, simply execute `main.py` with the appropriate Python interpreter. It is highly recommended to use the same Python version that was used to build the executable.

1.  Make sure `pyinstxtractor.py`, `main.py`, and `requirements.txt` are in the same directory.
2.  Run the script from your command line:

    ```bash
    # If the .exe was built with Python 3.13
    py -3.13 main.py

    # Or more generally
    python main.py
    ```

3.  A file dialog will appear. Select the `.exe` file you want to analyze.
4.  The script will handle the rest.

## Example Workflow

Here is what a typical run looks like in your console.



X:\pyautodump> py -3.13 main.py
[+] Installing requirements...
[+] Requirements are up to date.
[+] Extracting YourApp.exe...
[+] Processing C:/Users/YourUser/Documents/pyautodump/YourApp.exe
[+] Pyinstaller version: 6.5.0
[+] Python version: 3.13
[+] Length of package: 44906671 bytes
[+] Found 212 files in CArchive
[+] Beginning extraction...please standby
[+] Possible entry point: main.pyc
[+] Found 349 files in PYZ archive
[+] Successfully extracted pyinstaller archive: C:/Users/YourUser/Documents/pyautodump/YourApp.exe
[INFO] EXE requires Python 3.13. You are using Python 3.13.
[+] Decompiling and moving source files to output\YourApp_source...
[INFO] Decompilation finished: 361 succeeded, 0 failed.
[+] Deleting temporary folder...
[+] Cleanup successful.
[+] SUCCESS! The source code is located in: output\YourApp_source


After the script finishes, the `output\YourApp_source` directory will contain all the recovered `.py` files, ready for inspection. You no longer need to run a decompiler manually.

## See also

For more information on the extraction core, see the original project:

-   **[pyinstxtractor](https://github.com/extremecoders-re/pyinstxtractor )**: The original script this project is based on.

For dealing with encrypted executables, consider using:

-   **[pyinstxtractor-ng](https://github.com/pyinstxtractor/pyinstxtractor-ng )**: A standalone binary version of pyinstxtractor that supports encrypted archives.
