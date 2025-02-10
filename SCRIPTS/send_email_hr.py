import ssl
import json
import re
import google.generativeai as genai
from email.message import EmailMessage
import smtplib
from pymongo import MongoClient
import tkinter as tk
from tkinter import filedialog, messagebox
import os


class JobDescriptionProcessor:
    def __init__(self, api_key, mongo_uri, db_name, collection_name):
        genai.configure(api_key=api_key)
        self.instruction = (
            """
            Extract the following information from this job description:
            - Skills
            - Experience
            - Education
            - Department: Categorize the job post based on the following departments:
            ACCOUNTANT, ADVOCATE, AGRICULTURE, APPAREL, ARTS, AUTOMOBILE, AVIATION,
            BANKING, BPO, BUSINESS-DEVELOPMENT, CHEF, CONSTRUCTION, CONSULTANT, DESIGNER,
            DIGITAL-MEDIA, ENGINEERING, FINANCE, FITNESS, HEALTHCARE, HR, INFORMATION-TECHNOLOGY,
            PUBLIC-RELATIONS, SALES, TEACHER.

            Ensure you return this information even if it isn't explicitly mentioned.
            Return the data in JSON format with fields as keys.

            Job Description:
            {job_text}
            """
        )
        self.model = genai.GenerativeModel("models/gemini-1.5-flash", system_instruction=self.instruction)

        # MongoDB setup
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def generate_job_info(self, job_description):
        """Generate structured information from the job description text."""
        response = self.model.generate_content(f'{job_description}')

        # Extract JSON format from response
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, response.text, re.DOTALL)

        if matches:
            clean_response_text = matches[0]  # Take the first match if multiple found
            try:
                json_response = json.loads(clean_response_text)
                return json_response
            except json.JSONDecodeError:
                print("Error decoding JSON response from the model.")
        else:
            print("No valid JSON found in the response.")
        return None

    def save_to_mongodb(self, data):
        """Save job data to MongoDB."""
        try:
            result = self.collection.insert_one(data)
            data['_id'] = str(result.inserted_id)  # Store the string ID in the data
            print("Job description saved successfully to MongoDB.")
        except Exception as e:
            print(f"Error saving job description to MongoDB: {e}")


def send_email_with_job_info(email_sender, email_password, email_receivers, job_description, processor):
    """Send email with job description and extract relevant details for MongoDB."""
    job_title = job_description.get("Job Title", "Job Opening")
    subject = f'Looking for a {job_title}'
    body = job_description.get("Job Description", "")

    # Send email
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = ", ".join(email_receivers)
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receivers, em.as_string())
        print("Email sent successfully.")

    # Process job description text and save it
    extracted_data = processor.generate_job_info(body)
    if extracted_data:
        extracted_data.update(job_description)  # Include all job data
        processor.save_to_mongodb(extracted_data)


def load_job_post(file_path):
    """Load job description from a file."""
    with open(file_path, "r") as file:
        content = file.read()
    return content


def run_gui(api_key, mongo_uri, db_name, collection_name, email_sender, email_password):
    """Run the GUI for sending job descriptions."""

    def submit():
        directory_path = filedialog.askdirectory(title="Select Job Post Directory")
        if not directory_path:
            messagebox.showwarning("Input Error", "Please select a job post directory.")
            return

        email_receivers = email_input.get("1.0", tk.END).strip().split(",")

        if not email_receivers:
            messagebox.showwarning("Input Error", "Please enter the email addresses.")
            return

        for filename in os.listdir(directory_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(directory_path, filename)
                job_description_text = load_job_post(file_path)

                job_description = {
                    "Job Title": re.search(r"Job Title:\s*(.*)", job_description_text).group(1),
                    "Job Description": job_description_text
                }

                send_email_with_job_info(email_sender, email_password, email_receivers, job_description, processor)

        response = messagebox.askyesno("Success", "Emails sent successfully! Do you want to send more emails?")
        if response:
            email_input.delete("1.0", tk.END)
        else:
            root.quit()

    # Initialize processor
    processor = JobDescriptionProcessor(api_key, mongo_uri, db_name, collection_name)

    # Set up the GUI
    root = tk.Tk()
    root.title("Job Description Email Sender")

    tk.Label(root, text="Email Addresses (comma-separated):").pack()
    email_input = tk.Text(root, height=2, width=50)
    email_input.pack()

    submit_button = tk.Button(root, text="Send Job Posts", command=submit)
    submit_button.pack()

    root.mainloop()


def main():
    api_key = "AIzaSyBi18Mq5DYWKAqXESc4FVTnuX3j_kSDFNw"
    mongo_uri = "mongodb+srv://angrym21:RHVbIpuGrbIIPriS@cluster0.a76hu.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    db_name = "ATS"
    collection_name = "job_descriptions"
    email_sender = 'angrym21@gmail.com'
    email_password = 'zysg szis hdvq kbzo'
    job_file_path = rf"C:\Users\omarw\Desktop\scripts\job_post_examples\job_post_examples"

    # Run the GUI application
    run_gui(api_key, mongo_uri, db_name, collection_name, email_sender, email_password)


main()
