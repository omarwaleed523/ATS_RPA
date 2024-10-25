import os
import pdfplumber
import docx
import spacy
import re
import json

# Load SpaCy language model for text processing
nlp = spacy.load('en_core_web_sm')


def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text


def extract_text_from_docx(file_path):
    """Extracts text from a DOCX file."""
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


def extract_contact_info(text):
    """Extract contact info like email, phone, etc. using regex."""
    email = re.findall(r'\S+@\S+', text)
    phone = re.findall(r'\(?\b[0-9]{3}\)?[-. ]?[0-9]{3}[-. ]?[0-9]{4}\b', text)

    return {
        "Email": email[0] if email else "",
        "Phone": phone[0] if phone else ""
    }


def preprocess_text(text):
    """Cleans and preprocesses the extracted text."""
    text = re.sub(r'\s+', ' ', text)
    doc = nlp(text.lower())
    cleaned_text = " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])
    return cleaned_text


def extract_resume_sections(text):
    """Extract specific sections like skills, education, and experience from the resume."""
    sections = {
        "Skills": "",
        "Experience": "",
        "Education": ""
    }

    # Use regex to find section headers and extract corresponding text
    skills_match = re.search(r'Skills[:\n\r]+(.*?)(Experience|Education|$)', text, re.IGNORECASE | re.DOTALL)
    experience_match = re.search(r'Experience[:\n\r]+(.*?)(Education|$)', text, re.IGNORECASE | re.DOTALL)
    education_match = re.search(r'Education[:\n\r]+(.*?)(Skills|Experience|$)', text, re.IGNORECASE | re.DOTALL)

    sections['Skills'] = skills_match.group(1).strip() if skills_match else ""
    sections['Experience'] = experience_match.group(1).strip() if experience_match else ""
    sections['Education'] = education_match.group(1).strip() if education_match else ""

    return sections


def extract_resume_data(file_path):
    """Extracts structured resume data for similarity analysis."""
    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Please use PDF or DOCX.")

    contact_info = extract_contact_info(text)
    sections = extract_resume_sections(text)

    return {
        "Name": "",  # Name extraction can be added using SpaCy
        "Email": contact_info["Email"],
        "Phone": contact_info["Phone"],
        "Skills": sections["Skills"],
        "Experience": sections["Experience"],
        "Education": sections["Education"]
    }


def save_to_json(data, folder_path, file_name):
    """Saves extracted data to a JSON file in a specified folder."""
    # Ensure the folder exists
    os.makedirs(folder_path, exist_ok=True)

    # Define full path for the JSON file
    output_path = os.path.join(folder_path, f"{file_name}.json")

    with open(output_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Resume data saved to {output_path}")


# Example usage
folder_path = "C:\\Users\\omarw\\PycharmProjects\\rpa_ats\\resumes_data"  # Replace with your folder path
file_path = "C:\\Users\\omarw\\PycharmProjects\\rpa_ats\\resume\\10554236.pdf"  # Replace with resume file path

# Extract and save resume data
resume_data = extract_resume_data(file_path)
file_name = os.path.splitext(os.path.basename(file_path))[0]  # Use the resume file name without extension
save_to_json(resume_data, folder_path, file_name)
