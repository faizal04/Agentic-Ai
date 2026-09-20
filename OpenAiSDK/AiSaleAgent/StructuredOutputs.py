
# -------------Structured Outputs ---------------


# Structured Outputs

# Structured Outputs allow an LLM to return data in a predefined structure, usually with specific fields and data types. This is useful when the output needs to be used later in the application, such as passing it to another module, algorithm, database, or agent.

# While JSON mode only guarantees valid JSON, it does not guarantee that the response follows the exact structure you expect. Structured Outputs guarantee that the response follows the schema you define, making the output more reliable for further processing.

# In simple terms: use Structured Outputs when the LLM's response is not just meant to be read, but also needs to be reliably used by your code.

documenation ="https://developers.openai.com/api/docs/guides/structured-outputs?example=structured-data#examples"

from openai import AsyncOpenAI
from agents import Agent,OpenAIChatCompletionsModel,Runner
import os 
from dotenv import load_dotenv
from pydantic import BaseModel,Field
import asyncio 

load_dotenv(override=True)
BASE_URL =os.getenv("GROQ_BASE_URL")
API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME="openai/gpt-oss-20b"
client = AsyncOpenAI(base_url=BASE_URL,api_key=API_KEY)


class EmailReview(BaseModel):
  isProfessional:bool= Field(description="Whether the email is professional")
  main_pitch_points :str= Field(description="the main 3 sentences in the mail through which there is high chance of respond from client.")
  containsPlaceholder: bool= Field(description="whether the email contain placeholder or not")

# email="""
# Hi [first_name],

# I'm hitting you up to see if you'd like to buy our product. It's really great. You'll miss out if you don't buy it.

# Laters.

# Faisal
# """

# async def main():
#     response = await client.responses.parse(
#         model="openai/gpt-oss-20b",
#         input=email,
#         text_format=EmailReview,
#     )

   
#     print(response.output_parsed)


# if __name__ == "__main__":
#     asyncio.run(main())




# higher level build for agentic workflow. 

checker = Agent(name="Checker",instructions="Your review potential sales emails",model=OpenAIChatCompletionsModel(model=MODEL_NAME,openai_client=client),output_type=EmailReview)


async def main():
  result = await Runner.run(checker,email)
  
  review = result.final_output
  print(review)


asyncio.run(main())