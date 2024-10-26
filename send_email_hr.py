import os
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

            Ensure you return these information even if they aren't explicitly mentioned in the email.
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

    def generate_job_info(self, job_description, job_title):
        """Generate structured information from the job description text."""
        response = self.model.generate_content(f'{job_description}')

        # Extract JSON format from response
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, response.text, re.DOTALL)

        if matches:
            clean_response_text = matches[0]  # Take the first match if multiple found
            try:
                json_response = json.loads(clean_response_text)
                json_response['Job Title'] = job_title  # Use the provided job title
                json_response['Job Description'] = job_description  # Include full job description
                return json_response
            except json.JSONDecodeError:
                print("Error decoding JSON response from the model.")
        else:
            print("No valid JSON found in the response.")
        return None

    def save_to_mongodb(self, data):
        """Save job data to MongoDB and return the document ID."""
        try:
            result = self.collection.insert_one(data)
            data['_id'] = str(result.inserted_id)  # Convert ObjectId to string and add it to the data
            print("Job description saved successfully to MongoDB.")
        except Exception as e:
            print(f"Error saving job description to MongoDB: {e}")
        return data  # Return data with added ID

    def save_json_file(self, data):
        """Save job data to a JSON file."""
        job_title = data['Job Title'].replace(" ", "_")  # Replace spaces for file name
        json_file_path = os.path.join("C:\\Users\\omarw\\PycharmProjects\\rpa_ats\\job_description_data",
                                      f"{job_title}.json")

        try:
            with open(json_file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            print(f"Job description saved successfully to {json_file_path}.")
        except Exception as e:
            print(f"Error saving job description to file: {e}")


def send_email_with_job_info(email_sender, email_password, email_receiver, job_description, processor, job_title):
    """Send email with job description and extract relevant details for MongoDB."""
    subject = 'New Job Description Posting'
    body = job_description

    # Send email
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
        print("Email sent successfully.")

    # Process job description text and save it
    extracted_data = processor.generate_job_info(job_description, job_title)
    if extracted_data:
        processor.save_to_mongodb(extracted_data)
        processor.save_json_file(extracted_data)


def create_gui(processor):
    """Create a simple GUI for inputting job descriptions and sending emails."""

    def send_job_description():
        job_title = job_title_entry.get()
        job_description = job_description_entry.get("1.0", "end").strip()
        recipients = recipients_entry.get().split(",")  # Split recipients by comma

        if job_title and job_description:
            for recipient in recipients:
                send_email_with_job_info(email_sender, email_password, recipient.strip(), job_description, processor,
                                         job_title)

            messagebox.showinfo("Success", "Email sent successfully.")
            job_title_entry.delete(0, tk.END)
            job_description_entry.delete("1.0", tk.END)
            recipients_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Please fill in all fields.")

    window = tk.Tk()
    window.title("Job Description Email Sender")

    tk.Label(window, text="Job Title:").pack()
    job_title_entry = tk.Entry(window)
    job_title_entry.pack()

    tk.Label(window, text="Job Description:").pack()
    job_description_entry = tk.Text(window, height=10)
    job_description_entry.pack()

    tk.Label(window, text="Recipients (comma-separated):").pack()
    recipients_entry = tk.Entry(window)
    recipients_entry.pack()

    tk.Button(window, text="Send Email", command=send_job_description).pack()

    window.mainloop()


if __name__ == "__main__":
    api_key = "AIzaSyDhlz1NsYZ3ZjHQ4O71M115LaSxO1BvCsA"
    mongo_uri = "mongodb+srv://omarwaleed5234:VuAXN91kEyFGzg7i@ats.7cukr.mongodb.net/?retryWrites=true&w=majority&appName=ATS"
    db_name = "ATS"
    collection_name = "job_descriptions"

    email_sender = 'angrym21@gmail.com'
    email_password = 'zysg szis hdvq kbzo'

    # Initialize processor and create GUI
    processor = JobDescriptionProcessor(api_key, mongo_uri, db_name, collection_name)
    create_gui(processor)
