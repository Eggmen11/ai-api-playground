import sys
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Get the absolute path of the project's root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

from openai_agents.common.tools import tool_map
from openai_agents.tool_calling_agent.tool_schemas import tool_schemas_dict

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
client = OpenAI()

default_sys_msg = "You are a helful agent possibly equiped with some useful tools"

class Agent:
    def __init__(self, model: str, tools: list, sys_msg=default_sys_msg, verbose=False):
        self.model = model
        self.tools = tools
        self.tool_schemas = [tool_schemas_dict[tool_name] for tool_name in tools]
        self.messages = [{"role":"system", "content": sys_msg}]
        self.verbose = verbose


    def append_msg(self, role: str, msg: str, tool_call_id=None):
        if tool_call_id:
            # Append exactly one message that references the tool_call_id
            self.messages.append({
                "role": role,
                "tool_call_id": tool_call_id,
                "content": msg
            })
        else:
            # Otherwise append a normal message
            self.messages.append({
                "role": role,
                "content": msg
            })


    def get_model_response(self, user_msg=None):
        if user_msg:
            self.append_msg("user", user_msg)

        response = client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tool_schemas,
            tool_choice="auto",
        )
        return response


    def get_model_stream(self, user_msg=None):
        if user_msg:
            self.append_msg("user", user_msg)

        stream = client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            tools=self.tool_schemas,
            tool_choice="auto",
            stream=True
        )
        return stream
    

    def call_tool(self, name: str, args:dict):
        result = tool_map[name](**args)
        return result


    def invoke(self, user_msg:str):
        self.append_msg("user", user_msg)

        while True:
            #print(self.messages)
            model_response = self.get_model_response()  
            model_msg = model_response.choices[0].message
            
            tool_calls = model_msg.tool_calls or []

            if not tool_calls:
                self.append_msg("assistant", model_msg.content)
                return model_msg.content

            self.messages.append(model_msg)

            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                tool_result = self.call_tool(tool_name, args)
                
                self.append_msg("tool", str(tool_result), tool_call.id)


    def stream(self, user_msg: str):
        self.append_msg("user", user_msg)
        assistant_msg = ""

        while True:
            final = True
            final_tool_calls = {}
            stream = self.get_model_stream(user_msg)

            user_msg = ""

            for chunk in stream:
                # If there's a new chunk of content, print & store it
                content = chunk.choices[0].delta.content
                if content:
                    print(content, end="")
                    assistant_msg += content
                    self.append_msg("assistant", content)

                if chunk.choices[0].delta.tool_calls:
                    final = False  # We know we have at least one tool call
                    for tool_call in chunk.choices[0].delta.tool_calls:
                        index = tool_call.index
                        # Gather calls by index to ensure correct ordering
                        if index not in final_tool_calls:
                            final_tool_calls[index] = tool_call
                        else:
                            # Accumulate arguments if multiple partial calls for the same index
                            final_tool_calls[index].function.arguments += tool_call.function.arguments

            if final:
                break

            #print(f"\nFinal Tool Calls: {final_tool_calls}")
            self.messages.append({
                "role": "assistant",
                "tool_calls": list(final_tool_calls.values())
            })

            for idx in sorted(final_tool_calls.keys()):
                tool_call = final_tool_calls[idx]
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                tool_result = self.call_tool(tool_name, args)
                self.append_msg("tool", str(tool_result), tool_call.id)
                #print("\nTool call result appended:", tool_call.id, tool_result)
        print()


    def convo(self, stream=False):
        print("Welcome to Agent Convo (to exit type 'exit')")
        while True:
            user_msg = input(">")
            if user_msg == "exit":
                return
            
            if stream:
                print("Agent: ", end="")
                self.stream(user_msg)
                # Printing gets handeled in the stream
            else:
                agent_msg = self.invoke(user_msg)
                print(f"Agent: {agent_msg}")

if __name__ == '__main__':
    base_model = "gpt-4o-mini"
    tools = list(tool_map.keys())
    sys_msg = f"You are a helpful Agent equiped with these tools: {str(tools)}"
    a1 = Agent(base_model, tools, sys_msg)
    #response = a1.invoke("can you tell me the weather of paris and the weather in prague")
    #a1.convo()

    print(a1.invoke("Hello"))

