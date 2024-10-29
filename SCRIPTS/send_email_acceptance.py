import os
import ssl
from email.message import EmailMessage
import smtplib
from pymongo import MongoClient

def send_email(email_sender, email_password, email_receiver, candidate_name, job_title):
    """Send an acceptance email to the candidate."""
    subject = "Congratulations!"
    body = f"Dear {candidate_name},\n\n" \
           f"Congratulations! You have been ranked for the position of {job_title}.\n" \
           "We appreciate your application and look forward to discussing your candidacy further.\n\n" \
           "Best Regards,\nYour Company"

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())
        print(f"Email sent to {candidate_name} at {email_receiver}")

def process_ranked_candidates(email_sender, email_password, mongo_uri, db_name):
    """Process ranked candidates and send acceptance emails."""
    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client[db_name]

    # Retrieve all collections for job titles
    job_titles = db.list_collection_names()
    print(f"Available job title collections: {job_titles}")  # Debugging print

    for job_title in job_titles:
        results_collection_name = f"{job_title}_RANKED_RESULTS"
        results_collection = db[results_collection_name]

        # Check if the results collection exists and print its count
        count = results_collection.count_documents({})
        print(f"Document count in {results_collection_name}: {count}")  # Debugging print

        # Check if there are candidates with Acceptance Email Sent = False
        candidates_to_notify = list(results_collection.find({"Acceptance Email Sent": False}))
        if not candidates_to_notify:
            print(f"No candidates found with Acceptance Email Sent = False in {results_collection_name}. Skipping...")
            continue

        # Retrieve top 3 ranked candidates who haven't received an acceptance email
        candidates_to_notify = sorted(candidates_to_notify, key=lambda x: x["Rank"])[:3]

        # If there are candidates to notify, send acceptance emails
        for candidate in candidates_to_notify:
            name = candidate.get("Name")
            email = candidate.get("Email")

            if name and email:
                # Send the acceptance email
                send_email(email_sender, email_password, email, name, job_title)

                # Mark the candidate as notified
                results_collection.update_one({"_id": candidate["_id"]}, {"$set": {"Acceptance Email Sent": True}})
                print(f"Marked {name} as notified for {job_title}.")

if __name__ == "__main__":
    # Setup email sender credentials and MongoDB connection
    email_sender = 'angrym21@gmail.com'
    email_password = 'zysg szis hdvq kbzo'  # Use environment variables for sensitive data in production
    mongo_uri = "mongodb+srv://omarwaleed5234:VuAXN91kEyFGzg7i@ats.7cukr.mongodb.net/?retryWrites=true&w=majority&appName=ATS"
    db_name = "ATS"
    # Process candidates to send emails
    process_ranked_candidates(email_sender, email_password, mongo_uri, db_name)
