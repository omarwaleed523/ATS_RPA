import os
import subprocess
from pymongo import MongoClient


class CandidateRetriever:
    def __init__(self, mongo_uri, db_name):
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]

    def get_results_collections(self):
        """Retrieve all collections that end with '_RESULTS'."""
        return [coll for coll in self.db.list_collection_names() if coll.endswith('_RESULTS')]

    def retrieve_candidates(self):
        """Retrieve candidates' names, emails, ranks, and job titles from all results collections."""
        results_collections = self.get_results_collections()
        candidates_list = []

        for collection_name in results_collections:
            job_title = collection_name.replace("_RESULTS", "").replace("_",
                                                                        " ")  # Convert collection name to job title
            collection = self.db[collection_name]
            candidates = collection.find({}, {"Name": 1, "Email": 1, "Rank": 1})

            for candidate in candidates:
                candidates_list.append({
                    "Job Title": job_title,
                    "Name": candidate.get("Name"),
                    "Email": candidate.get("Email"),
                    "Rank": candidate.get("Rank")
                })

        # Print out the candidates list for debugging
        print(f"Retrieved candidates: {candidates_list}")  # Debugging line

        return candidates_list

    def send_email_to_candidates(self, candidates):
        """Send an email to each candidate who has a rank."""
        for candidate in candidates:
            if candidate['Rank'] is not None:  # Ensure rank exists
                email_receiver = candidate['Email']
                candidate_name = candidate['Name']

                # Check for None values
                if email_receiver is None or candidate_name is None:
                    print(f"Skipped candidate due to None value: {candidate}")
                    continue

                print(f"Sending email to: {candidate_name}, Email: {email_receiver}")  # Debugging line

                # Call the email sending script
                subprocess.run(['python', 'send_email_acceptance.py', email_receiver, candidate_name])


if __name__ == "__main__":
    mongo_uri = "mongodb+srv://omarwaleed5234:VuAXN91kEyFGzg7i@ats.7cukr.mongodb.net/?retryWrites=true&w=majority&appName=ATS"
    db_name = "ATS"

    retriever = CandidateRetriever(mongo_uri, db_name)

    # Retrieve candidates and send emails
    candidates = retriever.retrieve_candidates()
    retriever.send_email_to_candidates(candidates)
