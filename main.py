# main_script.py

import subprocess

def run_get_email_info():
    # Running the other Python file
    subprocess.run(["python", "get_email_info.py"])  # Use "python" if on Windows

if __name__ == "__main__":
    run_get_email_info()
