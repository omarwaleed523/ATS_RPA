import google.generativeai as genai
import json
import re
import subprocess  # To call the email script
from pymongo import MongoClient
import time  # Import time module for sleep functionality

class JobSimilarityMatcher:
    def __init__(self, api_key, mongo_uri, db_name):
        # Configure the generative AI model
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("models/gemini-1.5-flash")  # Initialize your model

        # Set up MongoDB client and database
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

    def get_job_descriptions(self):
        """Retrieve job descriptions from the collection."""
        return list(self.db.job_descriptions.find())

    def find_matching_collection(self, department):
        """Find a collection in the database that matches the department."""
        collection_name = department.replace(" ", "_").upper()
        return self.db[collection_name]

    def generate_similarity_score(self, job_description, resume):
        """Generate a similarity score between the job description and the resume."""
        instruction = (
            f"""
            You are an HR recruiter. Your task is to match a job description with a candidate's resume.
            Please evaluate the following based on the job description and resume content:

            Job Description:
            {job_description}

            Candidate's Resume:
            {resume}

            Please return a similarity score from 0 to 100 based on the relevance and finding of skills, experience, and education from job description in the resume.
            If there are strong matches, return a high score; if there are few or no matches, return a low score.
            Make sure the score is in the following format: "LLM Response: ## Similarity Score: 0-100".
            please reply only with Similarity Score: 0-100
            """
        )

        # Sleep for a short duration before making the API call
        time.sleep(4)

        response = self.model.generate_content(instruction)

        # Print the full LLM response for debugging
        print(f"LLM Response: {response.parts[0].text}")  # Debug print

        # Extract similarity score from response using regex
        match = re.search(r'Similarity Score:\s*(\d+)', response.parts[0].text)

        if match:
            return int(match.group(1))  # Return the score as an integer

        print(f"No valid score found in response for job description: {job_description}")  # Debug print
        return 0  # Default score if no valid response found

    def rank_resumes(self, department, results):
        """Rank resumes based on similarity scores and store in a new collection."""
        ranked_results = sorted(results, key=lambda x: x["Similarity Score"], reverse=True)

        # Create a new collection for ranked results
        results_collection_name = f"{department.replace(' ', '_').upper()}_RANKED_RESULTS"
        results_collection = self.db[results_collection_name]

        # Clear existing results
        results_collection.delete_many({})

        # Update the ranked results with rank and store them in the new collection
        for index, result in enumerate(ranked_results):
            result["Rank"] = index + 1  # Rank starts from 1
            results_collection.insert_one(result)  # Insert the ranked result

    def process_all_resumes(self):
        """Process resumes for all job titles in the job descriptions."""
        job_descriptions = self.get_job_descriptions()

        for job in job_descriptions:
            job_title = job.get("Job Title", "")
            job_description = job.get("Job Description", "")
            department = job.get("Department", "")
            print(f"Processing Job Title: {job_title} | Department: {department}")  # Debug print

            matching_collection = self.find_matching_collection(department)

            resumes = list(matching_collection.find())
            if not resumes:
                print(f"No resumes found for department: {department}")
                continue  # Skip if no resumes found

            results = []
            matched_resumes = set()  # To track processed resumes

            # Collect existing results from the ranked collection
            results_collection_name = f"{department.replace(' ', '_').upper()}_RANKED_RESULTS"
            existing_results = list(self.db[results_collection_name].find())

            for result in existing_results:
                matched_resumes.add(result["Email"])  # Assuming unique emails for identification

            for resume in resumes:
                email = resume.get("Email", "")
                if email in matched_resumes:
                    print(f"Resume for {email} already processed. Skipping...")
                    continue  # Skip if the resume is already processed

                name = resume.get("Name", "")
                phone = resume.get("Phone", "")
                skills = resume.get("Skills", "")
                experience = resume.get("Experience", "")
                education = resume.get("Education", "")

                # Combine skills, experience, and education for similarity matching
                combined_resume_text = f"{skills} {experience} {education}"
                print(f"Processing Resume for: {name}")  # Debug print

                similarity_score = self.generate_similarity_score(job_description, combined_resume_text)

                if similarity_score > 0:
                    # Create a new JSON object to store results
                    result_data = {
                        "Name": name,
                        "Email": email,
                        "Phone": phone,
                        "Similarity Score": similarity_score,
                        "Acceptance Email Sent": False
                    }
                    results.append(result_data)
                    print(f"Processed and stored data for {name} with score {similarity_score}.")

            # Rank and store results in a new collection
            if results:  # Only rank if there are new results
                self.rank_resumes(department, results)

if __name__ == "__main__":
    api_key = "AIzaSyDhlz1NsYZ3ZjHQ4O71M115LaSxO1BvCsA"  # Replace with your actual API key
    mongo_uri = "mongodb+srv://omarwaleed5234:VuAXN91kEyFGzg7i@ats.7cukr.mongodb.net/?retryWrites=true&w=majority&appName=ATS"
    db_name = "ATS"

    matcher = JobSimilarityMatcher(api_key, mongo_uri, db_name)

    # Process resumes for all job titles dynamically
    matcher.process_all_resumes()
