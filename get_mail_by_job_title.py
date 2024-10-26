import imaplib
import email
import os
from email.header import decode_header
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import subprocess
import sys
from pymongo import MongoClient

# Gmail IMAP server settings
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

# Email account credentials
EMAIL_USER = 'omarwaleed5234@gmail.com'  # Change to your email
EMAIL_PASS = 'njwf acix mevh lkgi'  # Change to your app-specific password

# MongoDB configuration
mongo_uri = "mongodb+srv://omarwaleed5234:VuAXN91kEyFGzg7i@ats.7cukr.mongodb.net/?retryWrites=true&w=majority&appName=ATS"
db_name = "ATS"
collection_name = "job_descriptions"

def authenticate_gmail():
    """Connect to Gmail via IMAP and authenticate."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_USER, EMAIL_PASS)
    return mail

def fetch_job_titles():
    """Fetch job titles from the job_description collection in MongoDB."""
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    # Fetch job titles
    job_titles = []
    cursor = collection.find({}, {"Job Title": 1})  # Fetch only Job Title field
    for document in cursor:
        print(document)  # Print the entire document for debugging
        if "Job Title" in document:  # Check if the key exists
            job_titles.append(document["Job Title"])
        else:
            print("Job Title key not found in document:", document)  # Debugging output for missing key

    client.close()  # Close the MongoDB connection
    return list(set(job_titles))  # Return unique job titles

def send_resume(selected_job_title, resume_path):
    """Send the resume to MongoDB based on the selected job title."""
    if selected_job_title and resume_path:
        # Call the resume_parser2.py script with the selected job title and resume path
        try:
            subprocess.run([sys.executable, "resume_parser2.py", selected_job_title, resume_path])
            messagebox.showinfo("Success", "Resume sent successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
    else:
        messagebox.showwarning("Warning", "Please select a job title and resume.")

def select_resume():
    """Open a file dialog to select the resume file."""
    file_path = filedialog.askopenfilename(
        title="Select Resume",
        filetypes=(("PDF files", "*.pdf"), ("Word files", "*.docx"), ("All files", "*.*"))
    )
    if file_path:
        return file_path
    return None

def main():
    # Authenticate to Gmail
    mail = authenticate_gmail()

    # Select the mailbox (e.g., INBOX)
    try:
        mail.select("inbox")  # Select the mailbox you want to work with
    except Exception as e:
        messagebox.showerror("Error", f"Failed to select inbox: {e}")
        mail.logout()
        return

    # Fetch job titles from MongoDB
    job_titles = fetch_job_titles()

    # Create GUI
    global root, job_title_dropdown, resume_path  # Make these global to access in send_resume function
    root = tk.Tk()
    root.title("Resume Submission")

    # Set window size
    root.geometry("400x300")
    root.configure(bg="#f0f0f0")  # Light grey background

    # Create a frame for better layout
    frame = tk.Frame(root, bg="#f0f0f0")
    frame.pack(pady=20)

    # Create a label for job titles
    job_title_label = tk.Label(frame, text="Select Job Title:", bg="#f0f0f0", font=("Arial", 12))
    job_title_label.pack(pady=10)

    # Create a dropdown for job titles
    selected_job_title = tk.StringVar()
    job_title_dropdown = ttk.Combobox(frame, textvariable=selected_job_title, values=job_titles, state="readonly")
    job_title_dropdown.pack(pady=10)

    # Variable to hold the resume path
    resume_path = ""

    # Create a Button to select the resume
    resume_button = tk.Button(frame, text="Select Resume",
                              command=lambda: select_resume_button(),
                              bg="#2196F3", fg="white", font=("Arial", 12), relief="raised")
    resume_button.pack(pady=10)

    def select_resume_button():
        """Function to update the resume path after selection."""
        global resume_path  # Use the global variable
        selected_path = select_resume()
        if selected_path:
            resume_path = selected_path
            messagebox.showinfo("Selected Resume", f"Resume selected: {os.path.basename(resume_path)}")

    # Create a Button to process the selected job title
    process_button = tk.Button(frame, text="Send Resume",
                               command=lambda: send_resume(selected_job_title.get(), resume_path),
                               bg="#4CAF50", fg="white", font=("Arial", 12), relief="raised")
    process_button.pack(pady=20)

    # Start the GUI
    root.mainloop()

    # Close the connection and logout
    try:
        mail.close()  # Close the selected mailbox
    except Exception as e:
        print(f"Failed to close mailbox: {e}")  # Handle any exceptions during closing

    mail.logout()  # Logout from the IMAP server

if __name__ == "__main__":
    main()
