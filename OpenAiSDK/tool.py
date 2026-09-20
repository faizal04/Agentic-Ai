import json
import os
from dotenv import load_dotenv
import requests
pushover_url = "https://api.pushover.net/1/messages.json"
load_dotenv(override=True)
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")

def push(text):
    requests.post(pushover_url,data={
        "token":pushover_token,
        "user":pushover_user,
        "message":text
    })
def record_user_detail(email,name="Name not provided",notes="not provided"):
    push(f"the user {name}, email {email} wants to convey you {notes}")
    return "OK"

def record_unknown_question(question):
    push(f"Recording question {question} asked that i couldn't answer")
    return "OK"

record_user_detail_json = {
    "name": "record_user_detail",
    "description": "Record a visitor's contact details when they want to get in touch. Include their name and a short summary of what they want to discuss.",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The user's email address"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {"type": "string", "description": "Brief summary of what they want to discuss"},
        },
        "required": ["email"],
    },
}
record_unknown_question_json ={
    "name": "record_unknown_question",
    "description":"Record the question which you are not able to answer",
    "parameters":{
        "type":"object",
        "properties":{
            "question":{

            "type":"string",
            "description":"Records the question which llm was not able to answer "

            },

        },
        "required":["question"]
    }
    }
tools =[{"type": "function","function":record_user_detail_json},
{"type":"function","function":record_unknown_question_json}]



tool_map={
    "record_user_detail":record_user_detail,
    "record_unknown_question":record_unknown_question
}
def handle_tool_call(tool_call):
    results =[]
    for tool_call in tool_call:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        tool = tool_map.get(tool_name)
        print("toolMap -----> ", tool)
        result = tool(**arguments) if tool else "tool not found"+tool_name
        results.append({
            "role":"tool","content":json.dumps(result),
            "tool_call_id":tool_call.id
        })
    return results