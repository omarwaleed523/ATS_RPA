import google.generativeai as genai
import time
import os
import json
import re
from pdfminer.high_level import extract_text as extract_pdf_text
import docx2txt
from pymongo import MongoClient
import hashlib


class Gemini:
    def __init__(self, api_key, mongo_uri, db_name, resume_dir):
        genai.configure(api_key=api_key)
        self.resume_dir = resume_dir
        self.instruction = (
            """
            Extract the following information from this resume text:
            - Name
            - Email
            - Phone
            - Skills
            - Experience
            - Education
            - Department: Categorize the resume based on the following departments:
              ACCOUNTANT, ADVOCATE, AGRICULTURE, APPAREL, ARTS, AUTOMOBILE, AVIATION, BANKING, BPO,
              BUSINESS-DEVELOPMENT, CHEF, CONSTRUCTION, CONSULTANT, DESIGNER, DIGITAL-MEDIA,
              ENGINEERING, FINANCE, FITNESS, HEALTHCARE, HR, INFORMATION-TECHNOLOGY, PUBLIC-RELATIONS,
              SALES, TEACHER.
              make sure categorize based on the related skills,education,and experiance with one of the 24 departmens mentioned

            Ensure you return names, emails, and phone numbers even if they aren't explicitly labeled in the text.
            If missing, use placeholders like 'John Doe', '0123456789', 'example@gmail.com'.
            Return the data in JSON format with these fields as keys.

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
        """Extract text from a DOCX file."""
        try:
            txt = docx2txt.process(docx_path)
            if txt:
                return txt.replace('\t', ' ')  # Replace tabs with spaces
            return None
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return None

    def save_to_mongodb(self, department, data):
        """Save data to MongoDB in a collection based on department."""
        collection_name = department.replace(" ", "_").upper()  # Sanitize department for collection name
        collection = self.db[collection_name]
        try:
            collection.insert_one(data)
            print(f"Data saved to MongoDB collection '{collection_name}'.")
        except Exception as e:
            print(f"Error saving data to MongoDB: {e}")

    def generate_response(self, extracted_text):
        """Generate response from LLM based on extracted text."""
        response = self.model.generate_content(f'{extracted_text}')

        # Extract JSON from the response
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, response.text, re.DOTALL)

        if matches:
            clean_response_text = matches[0]
            try:
                json_response = json.loads(clean_response_text)
                return json_response
            except json.JSONDecodeError:
                print("Error decoding JSON response from the model.")
        else:
            print("No valid JSON found in the response.")
        return None

    def process_resumes(self):
        """Process all resumes in the specified directory."""
        for filename in os.listdir(self.resume_dir):
            file_path = os.path.join(self.resume_dir, filename)
            if filename.endswith('.pdf'):
                extracted_text = self.extract_text_from_pdf(file_path)
            elif filename.endswith('.docx'):
                extracted_text = self.extract_text_from_docx(file_path)
            else:
                continue  # Skip non-PDF/DOCX files

            if extracted_text:
                json_response = self.generate_response(extracted_text)
                if json_response:
                    department = json_response.get("Department", "UNSPECIFIED")
                    json_response['resume_hash'] = hashlib.md5(extracted_text.encode()).hexdigest()  # Generate hash
                    self.save_to_mongodb(department, json_response)
                    print(f"Processed and saved: {filename}")
            else:
                print(f"Failed to extract text from: {filename}")


if __name__ == "__main__":
    api_key = "AIzaSyCIHEJQgSzmlzTMjGtfpJzu3IgVXW_R-qM"
    mongo_uri = "mongodb+srv://omarwaleed5234:VuAXN91kEyFGzg7i@ats.7cukr.mongodb.net/?retryWrites=true&w=majority&appName=ATS"
    db_name = "ATS"
    resume_dir = "C:\\Users\\omarw\\PycharmProjects\\RPA_ATS#\\Resumes\\test"

    gemini_instance = Gemini(api_key, mongo_uri, db_name, resume_dir)
    gemini_instance.process_resumes()
