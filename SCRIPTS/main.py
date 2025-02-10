# main_script.py
import subprocess
import sys
import time
from tkinter import messagebox

# Global variable to store the total runtime
total_runtime = 0

def measure_runtime(func):
    def wrapper(*args, **kwargs):
        global total_runtime
        start_time = time.time()  # Start time
        result = func(*args, **kwargs)  # Call the original function
        end_time = time.time()  # End time
        runtime = end_time - start_time
        total_runtime += runtime  # Add to the total runtime
        print(f"Runtime for {func.__name__}: {runtime:.2f} seconds")  # Print individual function runtime
        return result  # Return the result of the original function
    return wrapper


@measure_runtime
def send_email_hr():
    subprocess.run([sys.executable, "send_email_hr.py"])

@measure_runtime
def resume_parsing():
    subprocess.run([sys.executable, "resume_parsing.py"])

@measure_runtime
def resume_matching():
    subprocess.run([sys.executable, "resume_matching.py"])

@measure_runtime
def send_email_acceptance():
    subprocess.run([sys.executable, "send_email_acceptance.py"])

# Function to display the total runtime
def display_total_runtime():
    global total_runtime
    messagebox.showinfo("Total Runtime", f"Total runtime for all processes: {total_runtime:.2f} seconds")

def main():
    send_email_hr()
    resume_parsing()
    resume_matching()
    send_email_acceptance()
if __name__ == "__main__":
    main()
