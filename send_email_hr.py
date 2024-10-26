import ssl
import json
import re
import google.generativeai as genai
from email.message import EmailMessage
import smtplib
from pymongo import MongoClient
import tkinter as tk
from tkinter import messagebox

class JobDescriptionProcessor:
    def __init__(self, api_key, mongo_uri, db_name, collection_name):
        genai.configure(api_key=api_key)
        self.instruction = (
            """
            Extract the following information from this job description:
            - Skills
            - Experience
            - Education

            Ensure you return this information even if they aren't explicitly mentioned in the email.
            Return the data in JSON format with the fields as keys.

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




def send_email_with_job_info(email_sender, email_password, email_receivers, job_description, job_title, processor):
    """Send email with job description and extract relevant details for MongoDB."""
    subject = f'Looking for a {job_title}'
    body = job_description

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
    extracted_data = processor.generate_job_info(job_description)
    if extracted_data:
        extracted_data['Job Title'] = job_title  # Include job title in the data
        extracted_data['Job Description'] = job_description  # Include the full job description
        processor.save_to_mongodb(extracted_data)



def run_gui(api_key, mongo_uri, db_name, collection_name, email_sender, email_password):
    """Run the GUI for sending job descriptions."""

    def submit():
        job_title = title_input.get().strip()
        job_description = job_desc_text.get("1.0", tk.END).strip()
        email_receivers = email_input.get("1.0", tk.END).strip().split(",")
        if not job_title or not job_description or not email_receivers:
            messagebox.showwarning("Input Error", "Please enter job title, job description, and email addresses.")
            return

        send_email_with_job_info(email_sender, email_password, email_receivers, job_description, job_title, processor)

        response = messagebox.askyesno("Success", "Email sent successfully! Do you want to send another email?")
        if response:
            title_input.delete(0, tk.END)
            job_desc_text.delete("1.0", tk.END)
            email_input.delete("1.0", tk.END)
        else:
            root.quit()

    # Initialize processor
    processor = JobDescriptionProcessor(api_key, mongo_uri, db_name, collection_name)

    # Set up the GUI
    root = tk.Tk()
    root.title("Job Description Email Sender")

    tk.Label(root, text="Job Title:").pack()
    title_input = tk.Entry(root, width=50)
    title_input.pack()

    tk.Label(root, text="Job Description:").pack()
    job_desc_text = tk.Text(root, height=10, width=50)
    job_desc_text.pack()

    tk.Label(root, text="Email Addresses (comma-separated):").pack()
    email_input = tk.Text(root, height=2, width=50)
    email_input.pack()

    submit_button = tk.Button(root, text="Send Email", command=submit)
    submit_button.pack()

    root.mainloop()


if __name__ == "__main__":
    api_key = "AIzaSyDhlz1NsYZ3ZjHQ4O71M115LaSxO1BvCsA"
    mongo_uri = "mongodb+srv://omarwaleed5234:VuAXN91kEyFGzg7i@ats.7cukr.mongodb.net/?retryWrites=true&w=majority&appName=ATS"
    db_name = "ATS"
    collection_name = "job_descriptions"
    email_sender = 'angrym21@gmail.com'
    email_password = 'zysg szis hdvq kbzo'

    # Run the GUI application
    run_gui(api_key, mongo_uri, db_name, collection_name, email_sender, email_password)
