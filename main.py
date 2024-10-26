# main_script.py
import subprocess
# Add this at the top of both main_script.py and resume_parser.py
import sys

def run_get_email_info():
    # Running the other Python file
    subprocess.run([sys.executable, "get_email_info.py"])  # Use "python" if on Windows


def send_email():
    # Running the other Python file
    subprocess.run([sys.executable, "send_email_hr.py"])  # Use "python" if on Windows

def resume_parser():
    # Running the other Python file
    subprocess.run([sys.executable, "resume_parser2.py"])  # Use "python" if on Windows


if __name__ == "__main__":
    #HR sends an Email
    send_email()
    #resume_parser()
    #run_get_email_info()
