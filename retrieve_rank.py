import os
import subprocess
import logging
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CandidateRetriever:
    def __init__(self, mongo_uri, db_name):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.email_script = 'send_email_acceptance.py'  # Make the email script name configurable

    def get_results_collections(self):
        """Retrieve all collections that end with '_RESULTS'."""
        return [coll for coll in self.db.list_collection_names() if coll.endswith('_RESULTS')]

    def retrieve_candidates(self):
        """Retrieve candidates' names, emails, ranks, job titles, and email status from all results collections."""
        results_collections = self.get_results_collections()
        candidates_list = []

        for collection_name in results_collections:
            job_title = collection_name.replace("_RESULTS", "").replace("_", " ")  # Convert collection name to job title
            collection = self.db[collection_name]
            candidates = collection.find({}, {"Name": 1, "Email": 1, "Rank": 1, "Acceptance Email Sent": 1})

            for candidate in candidates:
                candidates_list.append({
                    "Job Title": job_title,
                    "Name": candidate.get("Name"),
                    "Email": candidate.get("Email"),
                    "Rank": candidate.get("Rank"),
                    "Acceptance Email Sent": candidate.get("Acceptance Email Sent", False)  # Default to False if not present
                })

        # Log the retrieved candidates list for debugging
        logging.info(f"Retrieved candidates: {candidates_list}")

        return candidates_list

    def send_email_to_candidates(self, candidates):
        """Send an email to each candidate who has a rank and hasn't received the acceptance email."""
        for candidate in candidates:
            if candidate['Rank'] is not None and not candidate['Acceptance Email Sent']:  # Ensure rank exists and email not sent
                email_receiver = candidate['Email']
                candidate_name = candidate['Name']
                job_title = candidate['Job Title']  # Get the job title for the email

                # Check for None values
                if email_receiver is None or candidate_name is None:
                    logging.warning(f"Skipped candidate due to None value: {candidate}")
                    continue

                logging.info(f"Sending email to: {candidate_name}, Email: {email_receiver}")

                # Call the email sending script with error handling
                try:
                    subprocess.run(['python', self.email_script, email_receiver, candidate_name, job_title], check=True)

                    # Update the document in MongoDB to set 'Acceptance Email Sent' to True
                    self.db[candidate['Job Title'].replace(" ", "_") + "_RESULTS"].update_one(
                        {"Name": candidate_name, "Email": email_receiver},
                        {"$set": {"Acceptance Email Sent": True}}
                    )
                    logging.info(f"Email successfully sent to {candidate_name}. Updated status in database.")

                except subprocess.CalledProcessError as e:
                    logging.error(f"Failed to send email to {candidate_name} at {email_receiver}: {str(e)}")
                except Exception as e:
                    logging.error(f"An unexpected error occurred while sending email: {str(e)}")

if __name__ == "__main__":
    mongo_uri = "mongodb+srv://omarwaleed5234:VuAXN91kEyFGzg7i@ats.7cukr.mongodb.net/?retryWrites=true&w=majority&appName=ATS"
    db_name = "ATS"

    retriever = CandidateRetriever(mongo_uri, db_name)

    # Retrieve candidates and send emails
    candidates = retriever.retrieve_candidates()
    retriever.send_email_to_candidates(candidates)
