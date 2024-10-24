# main_script.py

import subprocess

def run_get_email_info():
    # Running the other Python file
    subprocess.run(["python", "get_email_info.py"])  # Use "python" if on Windows


def send_email():
    # Running the other Python file
    subprocess.run(["python", "send_email.py"])  # Use "python" if on Windows


if __name__ == "__main__":
    #run_get_email_info()
    send_email()