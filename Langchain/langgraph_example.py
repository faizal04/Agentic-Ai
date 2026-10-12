import os 
import random
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph,START,END
from IPython.display import Image,display
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import GoogleSerperRun
from langchain_community.utilities import GoogleSerperAPIWrapper
import smtplib
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from email.message import EmailMessage
load_dotenv(override=True)


EMAIL_ADDRESS = os.getenv("EMAIL")
EMAIL_SMTP_SERVER=os.getenv("EMAIL_SMTP_SERVER")
EMAIL_APP_PASSWORD =os.getenv("GMAIL_APP_PASSWORD")

class State(TypedDict):
 messages:Annotated[list,add_messages]
 urdu:str


# nouns = ["Cabbages", "Unicorns", "Toasters", "Penguins", "Bananas", "Eels", "Pickles"]
# adjectives = ["outrageous", "smelly", "pedantic", "existential", "sparkly", "haunted"]

# def silly_node(state:State)->dict:
#     sentence =f"{random.choice(nouns)} are {random.choice(adjectives)}"
#     return {"messages":[{"role":"assistant","content":sentence}]}

# builder = StateGraph(State)
# builder.add_node("silly",silly_node)
# builder.add_edge(START,"silly")
# builder.add_edge("silly",END)
# graph = builder.compile()


# graph--------------------


# display(Image(graph.get_graph().draw_mermaid_png()))
def imageSave(graph,filename:str)->None:
    """Save a compiled LangGraph diagram as a PNG file."""
    png = graph.get_graph().draw_mermaid_png()
    Path(filename).write_bytes(png)

# result = graph.invoke({"messages":[{"role":"user","content":"say something"}]})
# print(result["messages"][-1].content)

apiKey = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model= "gemini-3.1-flash-lite",api_key=apiKey)



def chat_bot(state:State)->dict:
   return{"messages":[llm.invoke(state["messages"])]}

chatbuild = StateGraph(State)

chatbuild.add_node("chatbot",chat_bot)
chatbuild.add_edge(START,"chatbot")
chatbuild.add_edge("chatbot",END)
graphChatbot=chatbuild.compile()

# imageSave(graphChatbot,"chatbuild.png")

# chatbotResult = graphChatbot.invoke({"messages":[{"role":"user","content":"what is the directed graph in langgraph in one sentence"}]})
# print(chatbotResult["messages"][-1].content[0]["text"])

search = GoogleSerperRun(api_wrapper=GoogleSerperAPIWrapper())
senderEmail = os.getenv("EMAIL")
senderEmailPassword= os.getenv("GMAIL_APP_PASSWORD")
@tool
def send_email(subject:str, text_body:str)->str:
  """Send an email with the supplied subject and body."""
  msg = EmailMessage()
  msg["from"] = EMAIL_ADDRESS
  msg["to"]= EMAIL_ADDRESS
  msg["Subject"] = subject
  msg.set_content(text_body)
  

  with smtplib.SMTP_SSL(host=EMAIL_SMTP_SERVER,port=465) as server:
    server.login(EMAIL_ADDRESS,EMAIL_APP_PASSWORD)
    server.send_message(msg)


tools =[send_email,search]
llm_with_tool = llm.bind_tools(tools)

def chatbot_node_withTools(state:State)->dict:
   return {"messages":[llm_with_tool.invoke(state["messages"])]}

buildWithTools = StateGraph(State)
buildWithTools.add_node("chatbottool",chatbot_node_withTools)
buildWithTools.add_node("tools",ToolNode(tools))

buildWithTools.add_edge(START,"chatbottool")
buildWithTools.add_conditional_edges("chatbottool",tools_condition)
buildWithTools.add_edge("tools","chatbottool")

compileChatbot=buildWithTools.compile()

imageSave(compileChatbot,"compileChatbot.png")




# print(result["messages"][-1].content)


def translate(state:State)->dict:
   last= state["messages"][-1].content
   prompt=f"translate this message into urdu language. Here is the message {last}"
   return {"urdu":llm.invoke(prompt).content}

translatorBuilder =StateGraph(State)

translatorBuilder.add_node("chatbot",chatbot_node_withTools)
translatorBuilder.add_node("tools",ToolNode(tools))
translatorBuilder.add_node("translator",translate)

translatorBuilder.add_edge(START,"chatbot")
translatorBuilder.add_conditional_edges("chatbot",tools_condition,{"tools":"tools",END:"translator"})
translatorBuilder.add_edge("tools","chatbot")
translatorBuilder.add_edge("translator",END)

translatebuild= translatorBuilder.compile()
imageSave(translatebuild,"graphwithtranslator.png")

result= translatebuild.invoke({"messages":[{"role":"user","content":"Use the search tool to tell me the latest 2 news which are relavent to me as a developer in the tech world and drop me a mail of it with the subject and the news ."}]})
print(result["messages"][-1].content)
print(result["urdu"])

