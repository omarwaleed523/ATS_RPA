# main_script.py
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

def run_get_email_info():
    # Running the other Python file
    subprocess.run([sys.executable, "get_mail_by_job_title.py"])  # Use "python" if on Windows

def send_email_hr():
    # Running the other Python file
    subprocess.run([sys.executable, "send_email_hr.py"])  # Use "python" if on Windows

def resume_parser():
    # Running the other Python file
    subprocess.run([sys.executable, "resume_parser2.py"])  # Use "python" if on Windows
def resume_matching():
    # Running the other Python file
    subprocess.run([sys.executable, "resume_matching_llm_gemeni.py"])  # Use "python" if on Windows
def retrieve_rank():
    # Running the other Python file
    subprocess.run([sys.executable, "retrieve_rank.py"])  # Use "python" if on Windows

# Create the main GUI window
root = tk.Tk()
root.title("Job Application")

# Create a label
label = tk.Label(root, text="Select your role:")
label.pack(pady=10)

# Create buttons
job_recruiter_button = tk.Button(root, text="Job Recruiter", command=lambda: [
    send_email_hr(),

    root.quit()  # Close the GUI
])
job_recruiter_button.pack(pady=5)

job_seeker_button = tk.Button(root, text="Job Seeker", command=lambda: [
    run_get_email_info(),
    resume_matching(),
    retrieve_rank(),
    root.quit()  # Close the GUI
])
job_seeker_button.pack(pady=5)

# Run the GUI event loop
root.mainloop()
