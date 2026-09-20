from agents import Runner,output_guardrail,OpenAIChatCompletionsModel,GuardrailFunctionOutput,Agent
import os 
from dotenv import load_dotenv
from openai import AsyncOpenAI
import asyncio
from pydantic import BaseModel,Field
from agents import OutputGuardrailTripwireTriggered


class EmailReview(BaseModel):
  isProfessional:bool= Field(description="Whether the email is professional")
  main_pitch_points :str= Field(description="the main 3 sentences in the mail through which there is high chance of respond from client.")
  containsPlaceholder: bool= Field(description="whether the email contain placeholder or not")

instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools. 
"""


load_dotenv(override=True)
BASE_URL =os.getenv("GROQ_BASE_URL")
API_KEY = os.getenv("GROQ_API_KEY")
client = AsyncOpenAI(base_url=BASE_URL,api_key=API_KEY)

MODEL_NAME="openai/gpt-oss-20b"


model = OpenAIChatCompletionsModel(model="openai/gpt-oss-safeguard-20b",openai_client=client)




@output_guardrail
async def guardrail(ctx,agent,message):
  print("Guardrail Started....")
  print("ctx---",ctx.context,"\n ----agent----",agent,"\n----message---",message)
  result = await Runner.run(checker,message, context=ctx.context)
  print("\n\n\n---- result",result.final_output )
  review = result.final_output
  is_problem = review.containsPlaceholder or not review.isProfessional
  print("\n\n\n-----is problem",is_problem)
  return GuardrailFunctionOutput(output_info={"review":review},tripwire_triggered=is_problem)

checker = Agent(name="Checker",instructions="""Review the sales email provided to you.
    Determine whether the email is professional.
    Identify the main pitch points.
    Check whether the email contains placeholders such as [Name],
    [Your Name], [Company], or similar placeholder text.
    Return the result according to the required output structure""",
    model=model,
    output_type=EmailReview)

sales_agent_guardrail = Agent(name="illiterate",instructions=instructions+"Speak like an illiterate",model=OpenAIChatCompletionsModel(model=MODEL_NAME,openai_client=client),
    output_guardrails=[guardrail])

async def main():
  try:
    result = await Runner.run(sales_agent_guardrail,"Write a cold sales email")
    print(result.final_output)
  except OutputGuardrailTripwireTriggered:
    print("the email generated is not professional, so Guardrail stopped it. ")





asyncio.run(main())