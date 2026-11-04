import os
import sys
import threading
import queue
import pyttsx3
import requests
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QTabWidget

# Try importing whisper for offline speech-to-text
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

class CortexAgentClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cortex OS — Executive Suite (Hybrid + Auto-Interrupt)")
        self.resize(900, 650)

        # Initialize Text-to-Speech (Fallback to local pyttsx3 for offline/speed)
        self.tts_engine = pyttsx3.init()
        self.is_speaking = False
        self.audio_queue = queue.Queue()

        # Load local Whisper model lightly if available
        self.whisper_model = None
        if WHISPER_AVAILABLE:
            try:
                self.whisper_model = whisper.load_model("tiny") # Tiny model for fast local CPU execution
            except Exception as e:
                print(f"Whisper load warning: {e}")

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Assistant Chat Tab
        chat_tab = QWidget()
        chat_layout = QVBoxLayout(chat_tab)

        self.status_label = QLabel("STATUS: ONLINE & READY")
        chat_layout.addWidget(self.status_label)

        self.display_area = QTextEdit()
        self.display_area.setReadOnly(True)
        chat_layout.addWidget(self.display_area)

        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type command or query...")
        self.input_field.returnPressed.connect(self.send_command)
        input_layout.addWidget(self.input_field)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_command)
        input_layout.addWidget(self.send_btn)

        # Speak / Voice Button with Auto-Interrupt Trigger
        self.speak_btn = QPushButton("Speak / Listen")
        self.speak_btn.clicked.connect(self.toggle_voice_listener)
        input_layout.addWidget(self.speak_btn)

        chat_layout.addLayout(input_layout)
        self.tabs.addTab(chat_tab, "Assistant Chat")

    def interrupt_speech(self):
        """Auto-Interrupt: Stops any ongoing speech instantly when user inputs new action."""
        if self.is_speaking:
            try:
                self.tts_engine.stop()
                self.is_speaking = False
            except Exception:
                pass

    def send_command(self):
        prompt = self.input_field.text().strip()
        if not prompt:
            return

        # 1. TRIGGER AUTO-INTERRUPT
        self.interrupt_speech()

        self.display_area.append(f"<b>You:</b> {prompt}")
        self.input_field.clear()

        # Send to Backend API
        threading.Thread(target=self.query_backend, args=(prompt,), daemon=True).start()

    def query_backend(self, prompt):
        try:
            res = requests.post("http://127.0.0.1:8000/query", json={"prompt": prompt, "user_id": "default"}, timeout=30)
            if res.status_code == 200:
                answer = res.json().get("response", "No response received.")
                self.display_area.append(f"<b>Cortex:</b> {answer}")
                self.speak_response(answer)
            else:
                self.display_area.append(f"<b>Cortex:</b> Error communicating with backend server.")
        except Exception as e:
            self.display_area.append(f"<b>Cortex:</b> Unable to connect to Brain server. ({e})")

    def speak_response(self, text):
        """Threaded local speech synthesis with interrupt safety."""
        def speak_worker():
            self.is_speaking = True
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception:
                pass
            self.is_speaking = False

        threading.Thread(target=speak_worker, daemon=True).start()

    def toggle_voice_listener(self):
        """Listens using local Whisper when offline/online seamlessly."""
        self.interrupt_speech()
        self.display_area.append("<i>[Listening via Whisper audio engine...]</i>")

        # Placeholder for local audio recording & Whisper transcription execution
        if self.whisper_model:
            # Here you would record a temporary .wav audio snippet and run:
            # result = self.whisper_model.transcribe("temp_audio.wav")
            # prompt = result["text"]
            pass
        else:
            self.display_area.append("<i>[Whisper model not initialized. Please type command.]</i>")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = CortexAgentClient()
    client.show()
    sys.exit(app.exec_())