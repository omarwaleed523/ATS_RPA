import imaplib
import email
import os
from email.header import decode_header

# Gmail IMAP server settings
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

# Email account credentials
EMAIL_USER = 'omarwaleed5234@gmail.com'
EMAIL_PASS = 'njwf acix mevh lkgi'  # Use an app-specific password if 2FA is enabled

ATTACHMENTS_DIR = 'C:\\Users\\omarw\\PycharmProjects\\rpa_ats\\resume'



def authenticate_gmail():
    """Connect to Gmail via IMAP and authenticate."""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL_USER, EMAIL_PASS)
    return mail


def download_attachments(mail):
    """Download the last 10 email attachments."""
    mail.select("inbox")  # Select the inbox folder
    result, data = mail.search(None, "ALL")  # Search for all emails

    email_ids = data[0].split()  # Get list of email IDs
    latest_email_ids = email_ids[-10:]  # Retrieve the last 10 email IDs

    for email_id in latest_email_ids:
        # Fetch the email by ID
        result, msg_data = mail.fetch(email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                print(f"Processing email: {subject}")

                # Iterate over email parts
                if msg.is_multipart():
                    for part in msg.walk():
                        # Check if the part is an attachment
                        if part.get_content_disposition() == "attachment":
                            filename = part.get_filename()
                            if filename:
                                filename, encoding = decode_header(filename)[0]
                                if isinstance(filename, bytes):
                                    filename = filename.decode(encoding if encoding else "utf-8")

                                # Save the attachment
                                if not os.path.exists(ATTACHMENTS_DIR):
                                    os.makedirs(ATTACHMENTS_DIR)

                                filepath = os.path.join(ATTACHMENTS_DIR, filename)
                                with open(filepath, "wb") as f:
                                    f.write(part.get_payload(decode=True))
                                print(f"Attachment {filename} saved to {filepath}")


def main():
    # Authenticate to Gmail
    mail = authenticate_gmail()

    # Download attachments from the last 10 emails
    download_attachments(mail)

    # Close the connection and logout
    mail.close()
    mail.logout()


if __name__ == "__main__":
    main()
