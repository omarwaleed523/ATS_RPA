import os
import ssl
from email.message import EmailMessage
import smtplib
import sys

def send_email(email_sender, email_password, email_receiver, candidate_name):
    subject = "Congratulations!"
    body = f"Dear {candidate_name},\n\n" \
           "Congratulations! You have been ranked.\n" \
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

if __name__ == "__main__":
    email_sender = 'angrym21@gmail.com'
    email_password = 'zysg szis hdvq kbzo'  # Use environment variables for sensitive data in production
    email_receiver = sys.argv[1]
    candidate_name = sys.argv[2]

    send_email(email_sender, email_password, email_receiver, candidate_name)
