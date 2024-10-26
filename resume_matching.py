import google.generativeai as genai
import json
import re
from pymongo import MongoClient


class JobSimilarityMatcher:
    def __init__(self, api_key, mongo_uri, db_name):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("models/gemini-1.5-flash")  # Initialize your model

        # MongoDB setup
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

    def get_job_descriptions(self):
        """Retrieve job descriptions from the collection."""
        return list(self.db.job_descriptions.find())

    def find_matching_collection(self, job_title):
        """Find a collection in the database that matches the job title."""
        collection_name = job_title.replace(" ", "_").upper()
        return self.db[collection_name]

    def generate_similarity_score(self, job_description, resume):
        """Generate a similarity score between the job description and the resume."""
        instruction = (
            f"""
            ill give you two JSON files 
1- a job description for data engineer job position
2- a resume for someone who applied for this position
i want you to act as an HR recruiter. Your task is to match a job description with a candidate's resume. 
            Please evaluate the following based on the job description and resume content:

            Job Description:
            {job_description}

            Candidate's Resume:
            {resume}

            Please return a similarity score from 0 to 100 based on the relevance of skills, experience, and education from job description on the resume.
            If there are strong matches, return a high score; if there are few or no matches, return a low score.
            """
        )
        response = self.model.generate_content(instruction)

        # Check if the response has valid parts
        if response.parts and len(response.parts) > 0:
            print(f"LLM Response: {response.parts[0].text}")  # Debug print for the LLM response

            # Extract similarity score from response
            score_pattern = r'\d{1,3}'
            match = re.search(score_pattern, response.parts[0].text)
            if match:
                return int(match.group(0))  # Return the score as an integer

        # Log an error if the response is invalid or empty
        print(f"Invalid response from LLM for job description: {job_description}")
        return 0  # Default score if no valid response found

    def rank_resumes(self, job_title):
        """Rank resumes based on similarity scores after insertion."""
        results_collection_name = f"{job_title.replace(' ', '_').upper()}_RESULTS"
        results_collection = self.db[results_collection_name]

        # Retrieve all results for ranking
        results = list(results_collection.find())
        ranked_results = sorted(results, key=lambda x: x["Similarity Score"], reverse=True)

        # Update the ranked results with rank
        for index, result in enumerate(ranked_results):
            result["Rank"] = index + 1  # Rank starts from 1
            # Update the record in the database
            results_collection.update_one(
                {"_id": result["_id"]}, {"$set": {"Rank": result["Rank"]}}
            )

    def process_all_resumes(self):
        """Process resumes for all job titles in the job descriptions."""
        job_descriptions = self.get_job_descriptions()

        for job in job_descriptions:
            job_title = job.get("Job Title", "")
            job_description = job.get("Job Description", "")
            print(f"Processing Job Title: {job_title}")  # Debug print
            print(f"Job Description: {job_description}")  # Debug print
            matching_collection = self.find_matching_collection(job_title)

            resumes = list(matching_collection.find())
            if not resumes:
                print(f"No resumes found for job title: {job_title}")
                continue  # Skip if no resumes found

            for resume in resumes:
                name = resume.get("Name", "")
                email = resume.get("Email", "")
                phone = resume.get("Phone", "")
                skills = resume.get("Skills", "")
                experience = resume.get("Experience", "")
                education = resume.get("Education", "")

                # Combine skills, experience, and education for similarity matching
                combined_resume_text = f"{skills} {experience} {education}"
                print(f"Processing Resume for: {name}")  # Debug print
                print(f"Resume Text: {combined_resume_text}")  # Debug print

                # Check if the resume is already processed
                existing_result = self.db[f"{job_title.replace(' ', '_').upper()}_RESULTS"].find_one({"Email": email})
                if existing_result:
                    print(f"Resume for {name} already processed. Skipping...")
                    continue  # Skip if the resume is already processed

                similarity_score = self.generate_similarity_score(job_description, combined_resume_text)

                # Create a new JSON object to store in a new collection
                result_data = {
                    "Name": name,
                    "Email": email,
                    "Phone": phone,
                    "Similarity Score": similarity_score
                }

                # Store results in a new collection named after the job title
                results_collection_name = f"{job_title.replace(' ', '_').upper()}_RESULTS"
                results_collection = self.db[results_collection_name]
                results_collection.insert_one(result_data)
                print(f"Processed and stored data for {name} in {results_collection_name}.")

            # Rank the resumes based on similarity scores
            self.rank_resumes(job_title)


if __name__ == "__main__":
    api_key = "AIzaSyDhlz1NsYZ3ZjHQ4O71M115LaSxO1BvCsA"  # Replace with your actual API key
    mongo_uri = "mongodb+srv://omarwaleed5234:VuAXN91kEyFGzg7i@ats.7cukr.mongodb.net/?retryWrites=true&w=majority&appName=ATS"
    db_name = "ATS"

    matcher = JobSimilarityMatcher(api_key, mongo_uri, db_name)

    # Process resumes for all job titles dynamically
    matcher.process_all_resumes()
