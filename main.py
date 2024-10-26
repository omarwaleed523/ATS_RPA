# main_script.py
import subprocess
import sys
import tkinter as tk
import time
from tkinter import messagebox

# Global variable to store the total runtime
total_runtime = 0

def measure_runtime(func):
    def wrapper():
        global total_runtime
        start_time = time.time()  # Start time
        func()
        end_time = time.time()  # End time
        runtime = end_time - start_time
        total_runtime += runtime  # Add to the total runtime
        print(f"Runtime for {func.__name__}: {runtime:.2f} seconds")
    return wrapper

@measure_runtime
def run_get_email_info():
    subprocess.run([sys.executable, "get_mail_by_job_title.py"])

@measure_runtime
def send_email_hr():
    subprocess.run([sys.executable, "send_email_hr.py"])

@measure_runtime
def resume_parser():
    subprocess.run([sys.executable, "resume_parser2.py"])

@measure_runtime
def resume_matching():
    subprocess.run([sys.executable, "resume_matching_llm_gemeni.py"])

@measure_runtime
def retrieve_rank():
    subprocess.run([sys.executable, "retrieve_rank.py"])

# Function to display the total runtime
def display_total_runtime():
    global total_runtime
    print(f"Total runtime for all processes: {total_runtime:.2f} seconds")
    messagebox.showinfo("Total Runtime", f"Total runtime for all processes: {total_runtime:.2f} seconds")

# Create the main GUI window
root = tk.Tk()
root.title("Job Application")

# Create a label
label = tk.Label(root, text="Select your role:")
label.pack(pady=10)

# Create buttons
job_recruiter_button = tk.Button(root, text="Job Recruiter", command=lambda: [
    send_email_hr(),
    display_total_runtime(),
    root.quit()  # Close the GUI
])
job_recruiter_button.pack(pady=5)

job_seeker_button = tk.Button(root, text="Job Seeker", command=lambda: [
    run_get_email_info(),
    resume_matching(),
    retrieve_rank(),
    display_total_runtime(),
    root.quit()  # Close the GUI
])
job_seeker_button.pack(pady=5)

# Run the GUI event loop
root.mainloop()
