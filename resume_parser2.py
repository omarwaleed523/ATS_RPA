import google.generativeai as genai
import time
import os
import json
import re
from pdfminer.high_level import extract_text as extract_pdf_text
import docx2txt
from pymongo import MongoClient  # Import MongoClient
import sys

class Gemini:
    def __init__(self, api_key, mongo_uri, db_name):
        genai.configure(api_key=api_key)
        self.instruction = (
            """
            Extract the following information from this resume text:
            - Name
            - Email
            - Phone
            - Skills
            - Experience
            - Education

            Ensure you return emails and phone numbers even if they aren't explicitly labeled in the text.
            Return the data in JSON format with the fields as keys.

            Resume Text:
            {extracted_text}
            """
        )
        self.model = genai.GenerativeModel("models/gemini-1.5-flash", system_instruction=self.instruction)

        # MongoDB setup
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file."""
        try:
            return extract_pdf_text(pdf_path)
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return None

    def extract_text_from_docx(self, docx_path):
        """Extract text from a DOCX file using docx2txt."""
        try:
            txt = docx2txt.process(docx_path)
            if txt:
                return txt.replace('\t', ' ')  # Replace tabs with spaces
            return None
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return None

    def save_to_mongodb(self, job_title, data):
        """Save data to MongoDB in a collection named after the job title."""
        collection_name = job_title.replace(" ", "_").upper()  # Sanitize job title for MongoDB collection name
        collection = self.db[collection_name]
        try:
            collection.insert_one(data)  # Insert the JSON data into the collection
            print(f"Data saved successfully to MongoDB collection '{collection_name}'.")
        except Exception as e:
            print(f"Error saving data to MongoDB: {e}")

    def generate_response(self, extracted_text):
        """Generate response from the LLM based on the extracted text."""
        print(f"Extracted Text:\n{extracted_text}")
        response = self.model.generate_content(f'{extracted_text}')

        # Print the raw response
        print(f"Raw response from LLM: {response.text}")

        # Use regex to extract JSON from the response
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, response.text, re.DOTALL)

        if matches:
            clean_response_text = matches[0]  # Take the first match if multiple found
            print("Extracted JSON response:", clean_response_text)

            # Validate if the cleaned response is a proper JSON format
            try:
                json_response = json.loads(clean_response_text)
                print("Parsed JSON response:", json_response)

                # Validate presence of expected fields
                if "Email" not in json_response or "Phone" not in json_response:
                    print("Email or Phone not found in the response. Please check the LLM output.")
                    print(f"Complete response: {response.text}")

                return json_response  # Return JSON response for saving later
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
                print(f"Unexpected response format:\n{clean_response_text}")
        else:
            print("No valid JSON found in the response.")

        time.sleep(5)
        return None

    def process_resume(self, resume_path, job_title):
        """Process a resume based on its file type and save to MongoDB."""
        extracted_text = None
        if resume_path.endswith('.pdf'):
            extracted_text = self.extract_text_from_pdf(resume_path)
        elif resume_path.endswith('.docx'):
            extracted_text = self.extract_text_from_docx(resume_path)

        if extracted_text:
            json_response = self.generate_response(extracted_text)
            if json_response:  # Save JSON only if response is valid
                self.save_to_mongodb(job_title, json_response)  # Save to MongoDB
                print("Resume has been sent successfully.")
                os._exit(0)  # Forcefully close the process
        else:
            print("No text extracted from the resume.")
            return None


if __name__ == "__main__":
    api_key = "AIzaSyDhlz1NsYZ3ZjHQ4O71M115LaSxO1BvCsA"  # Replace with your actual API key
    mongo_uri = "mongodb+srv://omarwaleed5234:VuAXN91kEyFGzg7i@ats.7cukr.mongodb.net/?retryWrites=true&w=majority&appName=ATS"
    db_name = "ATS"  # Replace with your database name

    gemini_instance = Gemini(api_key, mongo_uri, db_name)

    # Example usage
    if len(sys.argv) == 3:
        selected_job_title = sys.argv[1]
        resume_file = sys.argv[2]
        start_time = time.time()  # Record the start time
        gemini_instance.process_resume(resume_file, selected_job_title)
        end_time = time.time()  # Record the end time

        runtime_seconds = end_time - start_time
        print(f"Runtime: {runtime_seconds:.2f} seconds")
    else:
        print("Usage: python resume_parser2.py <job_title> <resume_path>")
