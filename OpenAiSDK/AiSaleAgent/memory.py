from agents import Runner,Agent,set_tracing_disabled,OpenAIChatCompletionsModel
from dotenv import load_dotenv
import asyncio
import requests
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
import os
from agents.extensions.memory import AdvancedSQLiteSession
# from agents.decorators import tool


load_dotenv(override=True)
BASE_URL =os.getenv("GEMINI_BASE_URL")
API_KEY = os.getenv("GOOGLE_API_KEY")
Model_Name= "gemini-3.1-flash-lite"
if not BASE_URL and not API_KEY:
  raise ValueError("please provide the base_url and api key")

client = AsyncOpenAI(base_url=BASE_URL,api_key=API_KEY)
set_tracing_disabled(disabled=True)


async def main():
  agent = Agent(name="Assistant",instructions="you are a funny friend of the user..",model=OpenAIChatCompletionsModel(model=Model_Name,openai_client=client))

  # result = await Runner.run(agent,"hello my self faisal...")
  # print(result.final_output)
  # print("result input------list---\n\n\n",result.to_input_list())
  # history = result.to_input_list()


  # response=await Runner.run(agent,"what is my name?")
  # print("without memory \n",response.final_output)

  # response=await Runner.run(agent,history+[{"role":"user","content":"what is my name?"}])
  # print("with memory \n",response.final_output)

  session_id=12345
  session = AdvancedSQLiteSession(session_id= session_id,db_path="conversations.db",create_tables=True)
  
  print("first Turn \n \n \n ")
  first_result = await Runner.run(agent, "tell me 4 jokes ",session=session)
  print(first_result.final_output)



  print("second Turn \n \n \n ")
  second_result = await Runner.run(agent,"what was the third joke? repeat it.",session=session)
  print("\n\n\n ",second_result.final_output,"\n\n")


  


asyncio.run(main())