import os
import subprocess
import webbrowser
import pyautogui
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from openai import OpenAI

# Initialize Groq client using your free Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "gsk_BhHjlDaRAK8aACVzHL8...") # or load from your config
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

app = FastAPI(title="Cortex OS Backend (Groq Free Tier)", version="3.6")

current_state = {
    "mode": "Tactical",
    "voice_name": "Sonia",
    "voice_speed": 175
}

PROMPT_PERSONAS = {
    "Friendly": "You are Cortex, a warm, energetic, and highly supportive AI executive partner.",
    "Casual": "You are Cortex, a chill, concise, and relaxed AI developer assistant.",
    "Tactical": "You are Cortex, a precise, direct, zero-fluff tactical OS operating assistant.",
    "Professional": "You are Cortex, an elite, highly formal corporate executive assistant."
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "open_application",
            "description": "Opens a local desktop application or web service like Gmail.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of app or service (e.g., task manager, notepad, gmail)"}
                },
                "required": ["app_name"]
            }
        }
    }
]

def execute_local_action(name, args):
    if name == "open_application":
        app_name = args.get("app_name", "").lower()
        if "gmail" in app_name:
            webbrowser.open("https://mail.google.com")
            return "Opened Gmail in browser."
        elif "task manager" in app_name:
            subprocess.Popen(["taskmgr.exe"])
            return "Launched Task Manager."
        elif "notepad" in app_name:
            subprocess.Popen(["notepad.exe"])
            return "Launched Notepad."
        else:
            pyautogui.press('win')
            pyautogui.write(app_name)
            pyautogui.press('enter')
            return f"Launched application '{app_name}'."
    return "Action completed."

class CommandRequest(BaseModel):
    prompt: str
    voice_speed: int = 175

@app.post("/query")
def process_cortex_command(req: CommandRequest):
    system_instruction = PROMPT_PERSONAS.get(current_state["mode"], PROMPT_PERSONAS["Tactical"])
    try:
        # Use Groq's high-speed free models (e.g., llama-3.3-70b-versatile or mixtral-8x7b)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": req.prompt}
            ],
            tools=tools,
            tool_choice="auto"
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            results = []
            for tool_call in msg.tool_calls:
                args = json.loads(tool_call.function.arguments)
                res = execute_local_action(tool_call.function.name, args)
                results.append(res)
            return {"response": f"[{current_state['voice_name']}] {' '.join(results)}", "voice": current_state['voice_name']}

        return {"response": msg.content, "voice": current_state['voice_name']}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API Execution Error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)