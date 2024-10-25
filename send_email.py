import os
import ssl
from email.message import EmailMessage
import smtplib

email_sender ='angrym21@gmail.com'
email_password = 'zysg szis hdvq kbzo'
email_receiver = 'omarwaleed5234@gmail.com'


subject = 'sending this from the terminal'
body = """
    Hello my name is Mohamed, and i am sending this message from the terminal of pycharm
"""

em = EmailMessage()
em['From']= email_sender
em['To']=email_receiver
em['Subject']=subject
em.set_content(body)

context=ssl.create_default_context()

with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
    smtp.login(email_sender,email_password)
    smtp.sendmail(email_sender,email_receiver,em.as_string())
    print("email sent")
