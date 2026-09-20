import os 
from dotenv import load_dotenv
from agents import Agent,Runner,trace,set_tracing_export_api_key,OpenAIChatCompletionsModel
import asyncio 


from openai import AsyncOpenAI
from personal.OpenAiSDK.AiSaleAgent.tool import send_email_tool
load_dotenv(override=True)

MODEL_NAME="groq/compound-mini"
BASE_URL =os.getenv("GROQ_BASE_URL")
API_KEY = os.getenv("GROQ_API_KEY")


intro = """
You are a sales agent working for NowEraTech, 
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI.
You write emails.
"""

instructions1 = intro + "Your email style is professional, serious, with gravitas and credibility."
instructions2 = intro + "Your email style is witty, engaging, and humorous."


client = AsyncOpenAI(base_url=BASE_URL,api_key=API_KEY)


sales_picker_client = AsyncOpenAI(base_url=os.getenv("GEMINI_BASE_URL"),api_key=os.getenv("GEMINI_API_KEY"),
)
# ---------------orchestrating via llm -------------------

sales_agent_1 = Agent(name="Professional Sales Agent", instructions=instructions1,model=OpenAIChatCompletionsModel(model=MODEL_NAME,openai_client=client))
sales_agent_2 = Agent(name="Humorous Sales Agent",instructions=instructions2,model=OpenAIChatCompletionsModel(model=MODEL_NAME,openai_client=client))



description = "Use this tool to write a sales email. In the input, just instruct it to write a sales email."

tool1= sales_agent_1.as_tool(tool_name="sales_email_writer1",tool_description=description)
tool2= sales_agent_2.as_tool(tool_name="sales_email_writer2",tool_description=description)

tools = [tool1,tool2,send_email_tool]


print(tools)

instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_writer tools.
"""

task = """
Follow these steps:

1. Generate Drafts: Use each of the three sales_email_writer tools to generate different email drafts.
Just instruct each to write a sales email; no further details are needed.
Do not proceed until all three drafts are ready, one from each tool.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
 
3. Use your tool to send the best email (and only the best email) to the user. Only send 1 email.
"""

sales_manager= Agent(name="Sales Manager",instructions=instructions,tools=tools,model=OpenAIChatCompletionsModel(model="gemini-3.1-flash-lite",openai_client=sales_picker_client))

async def main2():
  with trace("yt llm call "):
    result = await Runner.run(sales_manager,task)
    print("--------result--------",result)

asyncio.run(main2())