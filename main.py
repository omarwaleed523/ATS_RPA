# main_script.py
import subprocess
# Add this at the top of both main_script.py and resume_parser.py
import sys

def run_get_email_info():
    # Running the other Python file
    subprocess.run(["C:\\Users\\omarw\\PycharmProjects\\rpa_ats\\.venv\\Scripts\\python.exe", "get_email_info.py"])  # Use "python" if on Windows


def send_email():
    # Running the other Python file
    subprocess.run(["C:\\Users\\omarw\\PycharmProjects\\rpa_ats\\.venv\\Scripts\\python.exe", "send_email.py"])  # Use "python" if on Windows

def resume_parser():
    # Running the other Python file
    subprocess.run(["C:\\Users\\omarw\\PycharmProjects\\rpa_ats\\.venv\\Scripts\\python.exe", "resume_parser.py"])  # Use "python" if on Windows


if __name__ == "__main__":
    #run_get_email_info()
    #send_email()
    resume_parser()
