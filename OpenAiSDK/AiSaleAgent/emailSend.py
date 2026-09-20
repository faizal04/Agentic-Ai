import os 
import smtplib
from dotenv import load_dotenv

from email.message import EmailMessage
load_dotenv(override=True)
EMAIL_ADDRESS = os.getenv("EMAIL")
EMAIL_SMTP_SERVER=os.getenv("EMAIL_SMTP_SERVER")
EMAIL_APP_PASSWORD =os.getenv("GMAIL_APP_PASSWORD")
if not EMAIL_ADDRESS and EMAIL_APP_PASSWORD and EMAIL_SMTP_SERVER:
  raise ValueError("something is wrong with your address ,password or server")
else:
  print("\n \t ------ MAIL SET -----")
def email_send(subject, text_body,html_body):
  msg = EmailMessage()
  msg["from"] = EMAIL_ADDRESS
  msg["to"]= EMAIL_ADDRESS
  msg["Subject"] = subject
  msg.set_content(text_body)
  msg.add_alternative(html_body,subtype="html")

  with smtplib.SMTP_SSL(host=EMAIL_SMTP_SERVER,port=465) as server:
    server.login(EMAIL_ADDRESS,EMAIL_APP_PASSWORD)
    server.send_message(msg)


email_send("Testing testing 123", "Fingers crossed..", "<html><body><strong>Fingers</strong> crossed..</body></html>")