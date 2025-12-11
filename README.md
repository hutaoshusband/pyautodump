# PyAutoDump - Automated PyInstaller Extractor & Decompiler

`PyAutoDump` is an automated tool that builds upon the original **[pyinstxtractor](https://github.com/extremecoders-re/pyinstxtractor )**. While the original script extracts the contents of a PyInstaller executable, `PyAutoDump` automates the entire reverse-engineering workflow: **extraction, decompilation, and organization.**

This project handles the tedious manual steps, providing you with the final source code in a clean output folder.

## Core Technology

This tool uses the original `pyinstxtractor.py` script as its extraction engine. It supports all versions that `pyinstxtractor` does, including PyInstaller versions 2.0 through 6.x and beyond.

For decompilation, PyAutoDump intelligently selects between two decompilers:
-   **pycdc:** A C++ based decompiler for modern Python versions (3.9 and above), including Python 3.13+
-   **decompyle3:** A Python-based decompiler for older Python versions (< 3.9)

The key difference is the automation layer built on top.

## Features

-   **Fully Automated:** Runs the entire extraction and decompilation process with a single command.
-   **Automatic Dependency Installation:** Installs the `decompyle3` decompiler automatically from `requirements.txt`.
-   **User-Friendly File Selection:** Launches a native file dialog to select the target `.exe`, or accepts a file path as a command-line argument.
-   **Intelligent Decompiler Selection:** Automatically detects the Python version used to build the `.exe` and selects the appropriate decompiler:
    -   Uses `pycdc` for Python 3.9+ (including Python 3.13)
    -   Uses `decompyle3` for Python versions below 3.9
-   **Smart Version Check:** Warns you if your Python version doesn't match the one used to build the `.exe`.
-   **Clean Output:** Organizes all recovered source code into a dedicated `output` folder and deletes temporary files.

## Installation

### Via Git Clone

1.  Clone this repository to your local machine:

    ```bash
    git clone https://github.com/hutaoshusband/pyautodump.git
    cd pyautodump
    ```

2.  The tool will automatically install dependencies when you first run it. The `pycdc` decompiler binaries are already included in the `Tools` directory.

### Installation Log Example

Here's what you'll see when cloning the repository:

```
C:\Users\YourUser\Documents> git clone https://github.com/hutaoshusband/pyautodump.git
Cloning into 'pyautodump'...
remote: Enumerating objects: 15, done.
remote: Counting objects: 100% (15/15), done.
remote: Compressing objects: 100% (12/12), done.
remote: Total 15 (delta 2), reused 15 (delta 2), pack-reused 0
Receiving objects: 100% (15/15), 10.01 MiB | 5.23 MiB/s, done.
Resolving deltas: 100% (2/2), done.

C:\Users\YourUser\Documents> cd pyautodump

C:\Users\YourUser\Documents\pyautodump> dir
 Volume in drive C is Windows
 Directory of C:\Users\YourUser\Documents\pyautodump

MM/DD/YYYY  HH:MM AM    <DIR>          .
MM/DD/YYYY  HH:MM AM    <DIR>          ..
MM/DD/YYYY  HH:MM AM            35,149 LICENSE
MM/DD/YYYY  HH:MM AM             4,256 README.md
MM/DD/YYYY  HH:MM AM    <DIR>          Tests
MM/DD/YYYY  HH:MM AM    <DIR>          Tools
MM/DD/YYYY  HH:MM AM            12,750 main.py
MM/DD/YYYY  HH:MM AM            17,572 pyinstxtractor.py
MM/DD/YYYY  HH:MM AM                10 requirements.txt
               5 File(s)         69,737 bytes
               4 Dir(s)  123,456,789,012 bytes free
```

**Note:** The repository includes pre-compiled `pycdc` binaries for both Windows (`pycdc.exe`) and Linux (`pycdc`) in the `Tools` folder, so no additional compilation is required.

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

### Example 1: Python 3.13 executable (uses pycdc)

```
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
[INFO] EXE was built with Python 3.13. You are using Python 3.13.
[INFO] Python 3.13 detected. Switching to pycdc decompiler.

[+] Decompiling source files for Python 3.13...
[INFO] Decompilation finished: 361 succeeded, 0 failed.
[+] Deleting temporary folder...
[+] Cleanup successful.

[+] SUCCESS! The source code is located in: C:\Users\YourUser\Documents\pyautodump\output\YourApp_source
```

### Example 2: Python 3.8 executable (uses decompyle3)

```
X:\pyautodump> py -3.8 main.py
[+] Installing requirements...
[+] Requirements are up to date.
[+] Extracting OldApp.exe...
[+] Processing C:/Users/YourUser/Documents/pyautodump/OldApp.exe
[+] Pyinstaller version: 5.1
[+] Python version: 3.8
[+] Length of package: 12345678 bytes
[+] Found 156 files in CArchive
[+] Beginning extraction...please standby
[+] Possible entry point: main.pyc
[+] Found 234 files in PYZ archive
[+] Successfully extracted pyinstaller archive: C:/Users/YourUser/Documents/pyautodump/OldApp.exe
[INFO] EXE was built with Python 3.8. You are using Python 3.8.
[INFO] Python 3.8 detected. Using 'decompyle3' decompiler.

[+] Decompiling source files for Python 3.8...
[INFO] Decompilation finished: 234 succeeded, 0 failed.
[+] Deleting temporary folder...
[+] Cleanup successful.

[+] SUCCESS! The source code is located in: C:\Users\YourUser\Documents\pyautodump\output\OldApp_source
```

After the script finishes, the `output\YourApp_source` (or `output\OldApp_source`) directory will contain all the recovered `.py` files, ready for inspection. You no longer need to run a decompiler manually.

## See also

For more information on the extraction core, see the original project:

-   **[pyinstxtractor](https://github.com/extremecoders-re/pyinstxtractor )**: The original script this project is based on.

For dealing with encrypted executables, consider using:

-   **[pyinstxtractor-ng](https://github.com/pyinstxtractor/pyinstxtractor-ng )**: A standalone binary version of pyinstxtractor that supports encrypted archives.
