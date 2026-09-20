from rich.console import Console 
from dotenv import load_dotenv
from openai import OpenAI
import os 
import json 

load_dotenv(override=True)

model_name = "openai/gpt-oss-120B"

def show(text):
    try:
        Console().print(text,style="white on blue")
    except Exception:
        print(text)



# gemini = os.getenv("GEMINI_API_KEY")
openai = OpenAI(base_url="https://api.groq.com/openai/v1",
    api_key=os.environ.get("GROQ_API_KEY"))

checklist=[]

def get_checklist_report() -> str:
    result = ""

    for index, item in enumerate(checklist):
        if item["completed"]:
            result += (
                f"Checklist #{index + 1}: "
                f"[strike][green]{item['description']}[/green][/strike]\n"
            )
        else:
            result += (
                f"Checklist #{index + 1}: "
                f"{item['description']}\n"
            )

    show(result)
    return result



def create_checklist(description:list[str])->str:
    for desc in description:
        checklist.append(
            {"description":desc,
            "completed":False}
            )
    return get_checklist_report()


    
def mark_completed(index:int,completion_notes:str) ->str:
    if 1<=index and index<= len(checklist):
        checklist[index-1].update({"completed": True})
    else:
        return "No checklist at this index"
    Console().print(completion_notes)
    return get_checklist_report()






create_checklist_json={
    "name":"create_checklist",
    "description":"add new checklist from the list",
    "parameters":{
        "type":"object",
        "properties":{
            "description":{
                "type":"array",
                "items":{"type":"string"},
                "title":"Description of checklist items"
            },

        },
        "required":["description"],

    }
}

mark_complete_json={
    "name":"mark_complete",
    "description":"To mark complete to the items",
    "parameters":{
        "type":"object",
        "properties":{
            "index":{"type":"integer","description":"The 1 based index of the checklist item to mark as complete","title":"Index"},
            "completion_notes":{"type":"string",'title': 'Completion Notes',"description":"notes about how you completed the checklist item in rich console markup"},
        },
    "required":["index","completion_notes"],
    },
    
}

tools= [{"type":"function","function":create_checklist_json},{"type":"function","function":mark_complete_json}]

def handle_tools_calls(tool_calls):
    results=[]
    for tool_call in tool_calls:
        tool_name= tool_call.function.name
        arguments= json.loads(tool_call.function.arguments)
        tool= globals().get(tool_name)
        result= tool(**arguments) if tool else "no tool found"
        results.append({"role":"tool","content":json.dumps(result),"tool_call_id":tool_call.id})
    return results
system_message = """
You are an AI agent that solves problems using a checklist.

Follow this exact process:

1. First create a checklist containing the steps required to solve the problem.
2. Then execute the checklist items one at a time.
3. After completing each step, you MUST call mark_complete for that checklist item.
4. Provide a short completion note when calling mark_complete.
5. Do not provide the final answer until every checklist item has been completed.
6. If information is missing, create a checklist step to make a reasonable estimate.
7. After all checklist items are marked complete, provide the final solution.

Provide the final response using Rich console markup.
Do not ask the user questions.
"""
def loop():
    messages=[{"role":"system","content":system_message}]+ [{"role":"user","content":"A train leaves kashmir at 2:00 pm traveling 60 mph.Another train leaves jammu at 3:00 pm traveling 80 mph toward kashmir.When do they meet?"}]
    print(tools)
    response= openai.chat.completions.create(model= model_name,messages= messages,tools= tools)
    while response.choices[0].finish_reason== "tool_calls":
        message= response.choices[0].message
        tool_calls= message.tool_calls
        results= handle_tools_calls(tool_calls)
        messages.append(message)
        messages.extend(results)
        response = openai.chat.completions.create(model=model_name,messages= messages,tools= tools)
    show(response.choices[0].message.content)

checklist=[]
loop()