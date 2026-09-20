
import os 
from dotenv import load_dotenv
from agents import Agent,Runner,trace,set_tracing_export_api_key,OpenAIChatCompletionsModel,ModelSettings,handoff
import asyncio 
from personal.OpenAiSDK.AiSaleAgent.emailSend import email_send
from email.message import EmailMessage
import smtplib
from openai import OpenAI,AsyncOpenAI
# from examples.auto_mode import input_with_fallback
from agents.decorators import tool
from personal.OpenAiSDK.AiSaleAgent.examples import input_with_fallback
load_dotenv(override=True)
MODEL_NAME="groq/compound-mini"
# ----------Orchestration Via Code ---------------
intro = """
You are a sales agent working for NowEraTech, 
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI.
You write emails.
"""

instructions1 = intro + "Your email style is professional, serious, with gravitas and credibility."
instructions2 = intro + "Your email style is witty, engaging, and humorous."




BASE_URL =os.getenv("GROQ_BASE_URL")
API_KEY = os.getenv("GROQ_API_KEY")

client = AsyncOpenAI(base_url=BASE_URL,api_key=API_KEY)


sales_picker_client = AsyncOpenAI(base_url=os.getenv("GEMINI_BASE_URL"),api_key=os.getenv("GEMINI_API_KEY"),
)

sales_agent_1 = Agent(name="Professional Sales Agent", instructions=instructions1,model=OpenAIChatCompletionsModel(model=MODEL_NAME,openai_client=client))
sales_agent_2 = Agent(name="Humorous Sales Agent",instructions=instructions2,model=OpenAIChatCompletionsModel(model=MODEL_NAME,openai_client=client))


@tool
def send_email_tool(subject,text_body,html_body):
  email_send(subject,text_body,html_body)
  return "Email Send Successfully"





async def main():
  with trace("sales manager with code yt"):
      input_prompt = input_with_fallback("Which business you wan to target?","Write the short cold email to the business of Dry Fruits in kashmir and tell them that online presence matters.  ")

    

      results = await asyncio.gather(
        Runner.run(sales_agent_1,input_prompt),
        Runner.run(sales_agent_2,input_prompt)
        )

      print("\n\n\n------result-1-------\n\n\n",results[0].final_output  )
      print("\n\n\n------result-2-------\n\n\n",results[1].final_output  )

      outputs = [result.final_output for result in results]
      emails = "Cold Sales Emails: \n\n".join(outputs)
      print("-----------emails------------------",emails)
      decision = """
      You pick the best cold sales email from the given options.
      Imagine you are a customer and pick the one you are most likely to respond to.
      Do not give an explanation; reply with the selected email only.
      Then use your tool to send the email.
      """
      model_settings=ModelSettings(tool_choice="required")

      sales_picker =Agent(name="Sales_picker",instructions=decision,tools=[send_email_tool],model_settings=model_settings,model=OpenAIChatCompletionsModel(model="gemini-3.1-flash-lite",openai_client=sales_picker_client))


      best_sale_email = await Runner.run(sales_picker,emails)
      print("best sales email \n\n\n----",best_sale_email.final_output)
asyncio.run(main())
