import os 
from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib
from crewai.tools import tool
load_dotenv(override=True)
EMAIL_ADDRESS = os.getenv("EMAIL")
EMAIL_SMTP_SERVER=os.getenv("EMAIL_SMTP_SERVER")
EMAIL_APP_PASSWORD =os.getenv("GMAIL_APP_PASSWORD")
@tool("email_send")
def email_send(subject, text_body,html_body):
  """Send an email to the specified recipient."""
  msg = EmailMessage()
  msg["from"] = EMAIL_ADDRESS
  msg["to"]= EMAIL_ADDRESS
  msg["Subject"] = subject
  msg.set_content(text_body)
  msg.add_alternative(html_body,subtype="html")

  with smtplib.SMTP_SSL(host=EMAIL_SMTP_SERVER,port=465) as server:
    server.login(EMAIL_ADDRESS,EMAIL_APP_PASSWORD)
    server.send_message(msg)
