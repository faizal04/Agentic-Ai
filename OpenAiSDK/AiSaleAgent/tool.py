from agents.decorators import tool
from personal.OpenAiSDK.AiSaleAgent.emailSend import email_send
@tool
def send_email_tool(subject,text_body,html_body):
  email_send(subject,text_body,html_body)
  return "Email Send Successfully"