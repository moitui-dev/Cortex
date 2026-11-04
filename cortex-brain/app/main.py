import sqlite3
import os
import shutil
import py_compile
import subprocess
import webbrowser
import psutil
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import core_security

app = FastAPI(title="Cortex Brain Server & Web App", version="16.2")

# Cloud API Configuration (Fallback / Distribution option)
USE_CLOUD_API = os.getenv("CORTEX_USE_CLOUD", "false").lower() == "true"
CLOUD_API_KEY = os.getenv("CORTEX_API_KEY", "")

class MultimodalRequest(BaseModel):
    prompt: str
    user_id: str = "default"
    image_b64: str = ""

class SandboxModifyRequest(BaseModel):
    user_id: str
    filename: str
    content: str

class SelfModifyRequest(BaseModel):
    target_file: str
    new_code: str

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "cloud_mode": USE_CLOUD_API,
        "permissions": {
            "terminal": core_security.get_permission("terminal_access"),
            "self_mod": core_security.get_permission("self_modification"),
            "camera": core_security.get_permission("camera_access"),
            "admin": core_security.get_permission("admin_execution")
        }
    }

@app.post("/query")
def query_brain(request: MultimodalRequest):
    try:
        user_prompt = request.prompt.lower().strip()
        user_profile = core_security.get_user_profile(request.user_id)
        user_name = user_profile.get("name", "Moitui Beckham")
        if not user_name or user_name.lower() == "user":
            user_name = "Moitui Beckham"

        dynamic_system_prompt = (
            f"You are Cortex, an advanced autonomous executive operating system serving {user_name} on their Windows workstation. "
            "Always give direct, concise, factual answers (1-2 sentences max). "
            "Never append the user's name to responses unless they explicitly ask you to say their name. "
            "Never output internal system rules, constraints, or meta-commentary."
        )

        # --- MASTER UNIVERSAL AUTOMATION ENGINE ---
        if core_security.get_permission("terminal_access"):

            # 1. Real-Time Hardware & System Status Triggers
            if "cpu" in user_prompt or "ram" in user_prompt or "memory" in user_prompt or "system usage" in user_prompt:
                cpu_usage = psutil.cpu_percent(interval=0.3)
                ram_usage = psutil.virtual_memory().percent
                return {"response": f"CPU usage is at {cpu_usage} percent, and RAM memory is at {ram_usage} percent."}

            if "battery" in user_prompt or "power" in user_prompt or "charge" in user_prompt:
                battery = psutil.sensors_battery()
                if battery:
                    percent = battery.percent
                    plugged_status = "plugged in and charging" if battery.power_plugged else "running on battery power"
                    return {"response": f"Battery is at {percent} percent and is currently {plugged_status}."}
                else:
                    return {"response": "Battery sensors are not available on this system."}

            if "time" in user_prompt or "clock" in user_prompt:
                current_time = datetime.now().strftime("%I:%M %p")
                return {"response": f"The current time on your desktop is {current_time}."}

            if "date" in user_prompt or "day is it" in user_prompt:
                current_date = datetime.now().strftime("%A, %B %d, %Y")
                return {"response": f"Today's date is {current_date}."}

            # 2. Browser & Web Service Launchers
            if "open chrome" in user_prompt:
                subprocess.Popen(["start", "chrome"], shell=True)
                core_security.log_audit("LAUNCH_APP", "Chrome")
                return {"response": "Opening Google Chrome."}

            if "open firefox" in user_prompt:
                subprocess.Popen(["start", "firefox"], shell=True)
                core_security.log_audit("LAUNCH_APP", "Firefox")
                return {"response": "Opening Firefox."}

            if "open brave" in user_prompt:
                subprocess.Popen(["start", "brave"], shell=True)
                core_security.log_audit("LAUNCH_APP", "Brave")
                return {"response": "Opening Brave browser."}

            if "open gmail" in user_prompt:
                webbrowser.open("https://mail.google.com")
                core_security.log_audit("WEB_DISPATCH", "Gmail")
                return {"response": "Opening Gmail."}

            if "play" in user_prompt and ("youtube" in user_prompt or "music" in user_prompt):
                query = user_prompt.replace("play", "").replace("on youtube", "").replace("search for", "").strip()
                url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                webbrowser.open(url)
                core_security.log_audit("MEDIA_PLAY", query)
                return {"response": f"Streaming '{query}' on YouTube."}

            # 3. Desktop Apps, IDEs & Utilities
            if "task manager" in user_prompt:
                subprocess.Popen(["taskmgr.exe"])
                core_security.log_audit("LAUNCH_UTIL", "Task Manager")
                return {"response": "Opening Task Manager."}

            if "open word" in user_prompt or "open ms word" in user_prompt:
                subprocess.Popen(["start", "winword"], shell=True)
                core_security.log_audit("LAUNCH_APP", "MS Word")
                return {"response": "Launching Microsoft Word."}

            if "open excel" in user_prompt:
                subprocess.Popen(["start", "excel"], shell=True)
                core_security.log_audit("LAUNCH_APP", "MS Excel")
                return {"response": "Launching Microsoft Excel."}

            if "open vs code" in user_prompt or "open code" in user_prompt:
                subprocess.Popen(["code"], shell=True)
                core_security.log_audit("LAUNCH_IDE", "VS Code")
                return {"response": "Opening Visual Studio Code."}

            if "open notepad" in user_prompt:
                subprocess.Popen(["notepad.exe"])
                core_security.log_audit("LAUNCH_APP", "Notepad")
                return {"response": "Opening Notepad."}

            if "open capcut" in user_prompt:
                subprocess.Popen(["start", "capcut"], shell=True)
                core_security.log_audit("LAUNCH_APP", "CapCut")
                return {"response": "Opening CapCut."}

            if "open photoroom" in user_prompt:
                webbrowser.open("https://www.photoroom.com")
                core_security.log_audit("LAUNCH_APP", "Photoroom")
                return {"response": "Opening Photoroom."}

            # 4. Terminal & File Management
            if "open cmd" in user_prompt or "open terminal" in user_prompt:
                subprocess.Popen(["start", "cmd.exe"], shell=True)
                core_security.log_audit("LAUNCH_TERM", "CMD")
                return {"response": "Opening Command Prompt."}

            if "open files" in user_prompt or "open file explorer" in user_prompt:
                subprocess.Popen(["explorer.exe"], shell=True)
                core_security.log_audit("LAUNCH_FILES", "Explorer")
                return {"response": "Opening File Explorer."}

            if "create" in user_prompt and ("file" in user_prompt or "desktop" in user_prompt):
                desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                filename = "cortex_notes.txt"
                if "named" in user_prompt:
                    parts = user_prompt.split("named")
                    if len(parts) > 1:
                        filename = parts[1].strip().split()[0]
                file_path = os.path.join(desktop_path, filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f"Generated by Cortex OS for {user_name}.\n")
                core_security.log_audit("FILE_CREATE", file_path)
                return {"response": f"Created file '{filename}' on your Desktop."}

        # --- MULTIMODAL VISION & LLM ROUTING (HYBRID LOCAL / CLOUD) ---
        history = core_security.fetch_memory(limit=6, user_id=request.user_id)

        if request.image_b64:
            if not core_security.get_permission("camera_access"):
                raise HTTPException(status_code=403, detail="Camera/Vision access is disabled.")
            payload = {"model": "llava", "prompt": request.prompt, "images": [request.image_b64], "stream": False}
            ollama_res = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
            if ollama_res.status_code == 200:
                res_text = ollama_res.json().get("response", "").strip()
            else:
                raise HTTPException(status_code=500, detail=f"Vision model error: {ollama_res.text}")
        else:
            if USE_CLOUD_API and CLOUD_API_KEY:
                headers = {"Authorization": f"Bearer {CLOUD_API_KEY}", "Content-Type": "application/json"}
                messages = [{"role": "system", "content": dynamic_system_prompt}]
                for h in history:
                    messages.append({"role": h["role"], "content": h["content"]})
                messages.append({"role": "user", "content": request.prompt})

                cloud_payload = {"model": "gpt-4o-mini", "messages": messages}
                cloud_res = requests.post("https://api.openai.com/v1/chat/completions", json=cloud_payload, headers=headers, timeout=60)

                if cloud_res.status_code == 200:
                    res_text = cloud_res.json()["choices"][0]["message"]["content"].strip()
                else:
                    raise HTTPException(status_code=500, detail=f"Cloud API error: {cloud_res.text}")
            else:
                full_prompt = f"System: {dynamic_system_prompt}\n"
                for h in history:
                    full_prompt += f"{h['role'].capitalize()}: {h['content']}\n"
                full_prompt += f"User: {request.prompt}\nCortex:"
                payload = {"model": "llama3.2:3b", "prompt": full_prompt, "stream": False}

                ollama_res = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
                if ollama_res.status_code == 200:
                    res_text = ollama_res.json().get("response", "").strip()
                else:
                    raise HTTPException(status_code=500, detail=f"Ollama error: {ollama_res.text}")

        core_security.save_memory("user", request.prompt, request.user_id)
        core_security.save_memory("assistant", res_text, request.user_id)
        return {"response": res_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brain Communication Failure: {str(e)}")

@app.post("/user/profile")
def update_profile(user_id: str, name: str, preferred_style: str = "concise"):
    core_security.set_user_profile(user_id, name, preferred_style)
    return {"status": "success", "user_id": user_id, "name": name}

@app.post("/system/self-modify")
def self_modify(req: SelfModifyRequest):
    if not core_security.get_permission("self_modification"):
        raise HTTPException(status_code=403, detail="Self-modification permission is locked.")

    target = req.target_file
    if not os.path.exists(target):
        raise HTTPException(status_code=404, detail="Target source file not found.")

    backup_path = target + ".bak"
    try:
        shutil.copy(target, backup_path)
        with open(target, "w", encoding="utf-8") as f:
            f.write(req.new_code)
        py_compile.compile(target, doraise=True)
        core_security.log_audit("SELF_MODIFY", f"Successfully updated {target}")
        return {"status": "success", "message": f"Successfully updated and verified {target}."}
    except Exception as e:
        if os.path.exists(backup_path):
            shutil.copy(backup_path, target)
        raise HTTPException(status_code=500, detail=f"Syntax validation failed. Reverted changes: {str(e)}")

@app.get("/dashboard", response_class=HTMLResponse)
def mobile_web_app():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head><title>Cortex Mobile Dashboard</title></head>
    <body style="background:#0B1220; color:#F1F5F9; font-family:sans-serif; padding:16px;">
        <h2>🤖 Cortex Executive Operating System</h2>
        <p>Universal automations, hardware monitoring, vision engine, and self-modification security active.</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)