#!/usr/bin/env python3
"""
A wrapper script around pip to install pip.
"""
import os
import sys
import subprocess
import tempfile
import shutil
from urllib.request import urlopen

def main():
    # Download get-pip.py
    print("Downloading get-pip.py...")
    with urlopen("https://bootstrap.pypa.io/get-pip.py") as response:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            shutil.copyfileobj(response, tmp_file)
            tmp_file.flush()
            os.chmod(tmp_file.name, 0o755)
            subprocess.check_call([sys.executable, tmp_file.name])
    print("pip has been installed successfully!")

if __name__ == "__main__":
    main() 