import sys
import os
import json
import websocket
import base64
import pyaudio
import threading
from dotenv import load_dotenv

# Get the absolute path of the project's root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)

from common.tools import tool_map
from openai_agents.realtime_agent.tool_schemas import rt_tool_schemas_dict 

# Load environment variables
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# WebSocket URL and headers
url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
headers = [
    "Authorization: Bearer " + OPENAI_API_KEY,
    "OpenAI-Beta: realtime=v1"
]

class RT_Agent:
    def __init__(self, sys_msg, tools, verbose=False, modalities=["text", "audio"]):
        self.sys_msg = sys_msg
        self.tools = tools
        self.verbose = verbose
        self.output_modals = modalities
        self.p = pyaudio.PyAudio()
        self.audio_stream_output = None
        self.audio_stream_input = None
        self.done_event = threading.Event()
        self.input_mode = None  # Initialize for convo mode
        if tools:
            self.tool_schemas = [rt_tool_schemas_dict[tool_name] for tool_name in tools]
        self.mode = None
        self.invoke_message = None

    def send_message(self, ws, text):
        """
        Helper function to send a user message (conversation.item.create)
        and then request an AI response (response.create).
        """
        message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": text}],
            },
        }
        ws.send(json.dumps(message))
        response_request = {
            "type": "response.create",
            "response": {"modalities": ["audio", "text"]},
        }
        ws.send(json.dumps(response_request))

    def stream_microphone_audio(self, ws):
        """
        Capture audio from the microphone, encode it, and send it to the WebSocket.
        """
        while not self.done_event.is_set() and ws.sock and ws.sock.connected:
            try:
                audio_chunk = self.audio_stream_input.read(1024, exception_on_overflow=False)
                base64_chunk = base64.b64encode(audio_chunk).decode("ascii")
                event = {"type": "input_audio_buffer.append", "audio": base64_chunk}
                ws.send(json.dumps(event))
            except websocket.WebSocketConnectionClosedException:
                print("WebSocket connection closed, stopping microphone streaming.")
                break
            except Exception as e:
                print("Error streaming microphone audio:", e)
                break

    def _on_message(self, ws, msg):
        """
        Handles incoming WebSocket messages.
        """
        data = json.loads(msg)
        if "audio" in self.output_modals and data.get("type") == "response.audio.delta":
            audio_b64 = data.get("delta")
            if audio_b64:
                audio_data = base64.b64decode(audio_b64)
                if self.audio_stream_output:
                    self.audio_stream_output.write(audio_data)
        if "text" in self.output_modals and data.get("type") == "response.audio_transcript.delta":
            print(data["delta"], end="", flush=True)
        if data.get("type") == "response.done":
            print("\n--- End of response ---\n")
            if data["response"]["output"][0].get("type") == "function_call":
                res_output = data["response"]["output"][0]
                call_id = res_output["call_id"]
                tool_name = res_output["name"]
                parsed_args = json.loads(res_output["arguments"])
                print(f"Calling {tool_name} with arguments {parsed_args}")
                output = self.call_tool(tool_name, parsed_args)
                print(f"Output: {output}")
                tool_response = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": json.dumps({tool_name: output})
                    }
                }
                ws.send(json.dumps(tool_response))
                ws.send(json.dumps({
                    "type": "response.create",
                    "response": {"modalities": ["audio", "text"]}
                }))
            if self.mode == "invoke":
                ws.close()
                self.done_event.set()

    def _on_open(self, ws):
        """
        Handles WebSocket connection opening.
        """
        print("WebSocket connected. Session started.")
        # Open output stream if audio output is enabled
        if "audio" in self.output_modals:
            self.audio_stream_output = self.p.open(
                format=pyaudio.paInt16, channels=1, rate=24000, output=True
            )
        # Open input stream only for convo mode with audio input
        if self.mode == "convo" and self.input_mode == "audio":
            self.audio_stream_input = self.p.open(
                format=pyaudio.paInt16, channels=1, rate=24000, input=True, frames_per_buffer=1024
            )
        # Send session setup
        session_update = {"type": "session.update", "session": {"modalities": self.output_modals}}
        if self.tools:
            session_update["session"]["tools"] = self.tool_schemas
            session_update["session"]["tool_choice"] = "auto"
        ws.send(json.dumps(session_update))
        # Handle mode-specific actions
        if self.mode == "convo" and self.input_mode == "audio":
            threading.Thread(target=self.stream_microphone_audio, args=(ws,), daemon=True).start()
        elif self.mode == "invoke":
            self.send_message(ws, self.invoke_message)

    def _on_close(self, ws, close_status_code, close_msg):
        """
        Handles WebSocket connection closure.
        """
        print(f"WebSocket closed: {close_status_code} {close_msg}")
        self.done_event.set()
        if self.audio_stream_input:
            self.audio_stream_input.stop_stream()
            self.audio_stream_input.close()
            self.audio_stream_input = None
        if self.audio_stream_output:
            self.audio_stream_output.stop_stream()
            self.audio_stream_output.close()
            self.audio_stream_output = None

    def _on_error(self, ws, error):
        """
        Handles WebSocket errors.
        """
        print("WebSocket Error:", error)

    def invoke(self, user_msg):
        """
        Invoke the agent with a single user message.
        """
        self.mode = "invoke"
        self.invoke_message = user_msg
        self.done_event.clear()
        ws = websocket.WebSocketApp(
            url,
            header=headers,
            on_open=self._on_open,
            on_message=self._on_message,
            on_close=self._on_close,
            on_error=self._on_error,
        )
        ws.run_forever()

    def convo(self, input_mode="text"):
        """
        Start a conversation with the agent, allowing text or audio input based on input_mode.
        """
        self.mode = "convo"
        self.input_mode = input_mode
        self.done_event.clear()
        ws = websocket.WebSocketApp(
            url,
            header=headers,
            on_open=self._on_open,
            on_message=self._on_message,
            on_close=self._on_close,
            on_error=self._on_error,
        )
        def input_loop():
            while not self.done_event.is_set():
                user_input = input("You: ")
                if user_input.lower() == "exit":
                    self.done_event.set()
                    ws.close()
                    break
                if user_input.strip():
                    self.send_message(ws, user_input)
        if self.input_mode == "text":
            threading.Thread(target=input_loop, daemon=True).start()
        ws.run_forever()

    def call_tool(self, name, args):
        result = tool_map[name](**args)
        return result

# Example usage
if __name__ == "__main__":
    agent = RT_Agent(sys_msg="", tools=list(tool_map.keys()))
    print("Choose mode:")
    print("1. Invoke (Single message)")
    print("2. Convo (Interactive conversation)")
    mode = input("Enter 1 or 2: ")
    if mode == "1":
        user_message = input("Enter your message: ")
        agent.invoke(user_message)
    elif mode == "2":
        print("Choose input mode:")
        print("1. Text")
        print("2. Audio")
        choice = input("Enter 1 or 2: ")
        input_mode = "text" if choice == "1" else "audio"
        agent.convo(input_mode=input_mode)
    else:
        print("Invalid choice. Exiting.")