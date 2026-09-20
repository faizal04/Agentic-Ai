import os 
import json 
from openai import OpenAI
import gradio as gr
from dotenv import load_dotenv 
from personal.OpenAiSDK.context import system_prompt
from personal.OpenAiSDK.tool import tools, handle_tool_call

load_dotenv(override=True)
gemini = os.getenv("GEMINI_API_KEY")

openai = OpenAI(api_key=gemini,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/")

model_name= "gemini-3.1-flash-lite"


def chat(message,history):
    messages= [{"role":"system","content":system_prompt}]+history+[{"role":"user","content":message}]
    response = openai.chat.completions.create(model=model_name,messages= messages,tools= tools)
    while response.choices[0].finish_reason=="tool_calls":
        message = response.choices[0].message
        tool_calls=message.tool_calls
        results= handle_tool_call(tool_calls)
        print(results,"----------results")
        messages.append(message)
        messages.extend(results)
        response= openai.chat.completions.create(model=model_name,messages= messages,tools= tools)
    return response.choices[0].message.content



gr.ChatInterface(chat).launch(inbrowser=False)