# --------------------Handsoff-------------------------------------------

import os 
from dotenv import load_dotenv
from agents import Agent,Runner,trace,OpenAIChatCompletionsModel,ModelSettings
import asyncio 
from personal.OpenAiSDK.AiSaleAgent.tool import send_email_tool

from openai import OpenAI,AsyncOpenAI
# from examples.auto_mode import input_with_fallback
load_dotenv(override=True)
MODEL_NAME="groq/compound-mini"


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


description = "Use this tool to write a sales email. In the input, just instruct it to write a sales email."

tool1= sales_agent_1.as_tool(tool_name="sales_email_writer1",tool_description=description)
tool2= sales_agent_2.as_tool(tool_name="sales_email_writer2",tool_description=description)

instructions = """
You are a Sales Manager at ComplAI. You get your sales team to draft emails, then send them all to a sales picker.
"""

task = """
Follow these steps:

1. Generate Drafts: Use each of the two sales_email_writer tools to generate different email drafts.
Just instruct each to write a sales email; no further details are needed.
Do not proceed until all two drafts are ready, one from each tool.
 
2. Handoff to the sales picker to choose and send the best email.
"""


decision = """
You pick the best cold sales email from the given options.
Imagine you are a customer and pick the one you are most likely to respond to.
Then use your tool to send the email.
"""

model_settings=ModelSettings(tool_choice="required")

sales_picker =Agent(name="Sales_picker",instructions=decision,tools=[send_email_tool],model_settings=model_settings,model=OpenAIChatCompletionsModel(model="gemini-3.1-flash-lite",openai_client=sales_picker_client))
tools = [tool1,tool2]
handoffs= [sales_picker]

sales_manager_handoff = Agent(name="sales manager handoff",instructions=instructions,model=OpenAIChatCompletionsModel(model="gemini-3.1-flash-lite",openai_client=sales_picker_client), tools=tools ,handoffs=handoffs)

async def handoffs():
  with trace("sales Manager handoff"):
    result = await Runner.run(sales_manager_handoff,task)

asyncio.run(handoffs())