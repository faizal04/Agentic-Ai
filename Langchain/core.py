import os 
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage,SystemMessage,ToolMessage
from langchain_core.tools import tool 
from pydantic import BaseModel,Field

load_dotenv(override=True)
apiKey= os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model= "gemini-3.1-flash-lite",api_key=apiKey)
message = "what is the actual langchain core. in just one sentence"

# reply = llm.invoke(message)

# print(reply.content)



# Streaming -----------------------

# for chunk in llm.stream("give me 3 best poetry of zia mohideen"):
#   print(chunk.content)




# messages -------------------------

messages = [SystemMessage("you are a developer with the experience of 15 years. you have to guide the user in just list. max list size should be 3. like giving 3 bullet points for their query. if asked unrelated to the development or technology. you have restrain from answering it. you have be honest with the user no matter what happens. and you have to show them the reality. "),
HumanMessage("i am a full stack developer but i don't have experience. i applied at multiple positions still no repond what should i do. ")]

# print(llm.invoke(messages).content)



# tools --------------------
@tool 
def get_share_price(symbol:str)->str:
  """Return the current share price for a given ticker symbol."""
  fake_price={"AAPL":222,"TSLA":500,"GOOGLE":900}
  return fake_price.get(symbol.upper(),0.0)

print("name",get_share_price.name)
print("description",get_share_price.description)
print("arguments",get_share_price.args)

# calling tool -----------------
# print("called directly",get_share_price.invoke({"symbol":"AAPL"}))


# Giving tool to the Model ------------------

llm_with_tool = llm.bind_tools([get_share_price])
# response= llm_with_tool.invoke("what is the share price of tesla?")

# print("response",repr(response.content))
# print("response detail",response)


# when we invoke, the model may come back not with an answer but with a request to run a tool. That request shows up in `.tool_calls`.


conversation = [HumanMessage("what is the share price of Tesla?")]
ai_message = llm_with_tool.invoke(conversation)
conversation.append(ai_message)

for call in ai_message.tool_calls:
  if call["name"]=="get_share_price":
    result= get_share_price.invoke(call["args"])
    conversation.append(ToolMessage(content=str(result),tool_call_id= call["id"]))

# final= llm_with_tool.invoke(conversation)
# print(final.content)




# Structured outputs  

class Company(BaseModel):
  name:str=Field(description="The company name")
  ticker:str=Field(description="the stock ticker symbol")
  founded_year:int=Field(description="the year in which the company was founded")

structured_llm =llm.with_structured_output(Company)
company = structured_llm.invoke("Tell me about the Tesla company")
print(company)
# name, ticker,founded year
print("the company was founded in",company.founded_year)

