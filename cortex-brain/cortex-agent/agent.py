import sys
import threading
import requests
import pyttsx3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
                             QLabel, QSlider, QCheckBox, QTabWidget, QGroupBox, QFormLayout, QComboBox)
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPainter, QColor, QBrush

DARK_THEME_STYLE = """
QMainWindow, QWidget { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; font-size: 10pt; }
QTabWidget::pane { border: 1px solid #30363d; background-color: #161b22; }
QTabBar::tab { background-color: #21262d; color: #8b949e; padding: 8px 16px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
QTabBar::tab:selected { background-color: #161b22; color: #f0f6fc; border-bottom: 2px solid #238636; }
QTextEdit { background-color: #0d1117; color: #f0f6fc; border: 1px solid #30363d; border-radius: 6px; padding: 8px; }
QLineEdit { background-color: #161b22; color: #f0f6fc; border: 1px solid #30363d; border-radius: 6px; padding: 8px; }
QPushButton { background-color: #238636; color: #ffffff; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; }
QPushButton:hover { background-color: #2ea043; }
QPushButton#clear_btn { background-color: #da3633; }
QPushButton#clear_btn:hover { background-color: #f85149; }
QLabel { color: #c9d1d9; }
QComboBox { background-color: #161b22; color: #f0f6fc; border: 1px solid #30363d; border-radius: 4px; padding: 4px; }
QSlider::groove:horizontal { border: 1px solid #30363d; height: 6px; background: #161b22; border-radius: 3px; }
QSlider::handle:horizontal { background: #58a6ff; border: none; width: 14px; margin: -4px 0; border-radius: 7px; }
"""

class VisualOrb(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 50)
        self.pulse = 0
        self.state_color = QColor(0, 255, 100)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

    def animate(self):
        self.pulse = (self.pulse + 5) % 360
        self.update()

    def set_state(self, mode):
        if mode == "active":
            self.state_color = QColor(88, 166, 255)
        elif mode == "speaking":
            self.state_color = QColor(255, 123, 114)
        else:
            self.state_color = QColor(0, 255, 100)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        glow_alpha = int(100 + 50 * abs(3.14 - (self.pulse * 3.14 / 180.0)))
        glow_color = QColor(self.state_color)
        glow_color.setAlpha(glow_alpha)
        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(2, 2, 46, 46))
        painter.setBrush(QBrush(self.state_color))
        painter.drawEllipse(QRectF(10, 10, 30, 30))

class SpeechEngine:
    def __init__(self):
        try:
            self.tts = pyttsx3.init()
        except Exception:
            self.tts = None
        self.is_speaking = False

    def speak(self, text, speed=175, voice_index=0, callback=None):
        if not self.tts:
            if callback: callback()
            return
        self.stop()
        self.is_speaking = True
        self.tts.setProperty('rate', speed)

        try:
            voices = self.tts.getProperty('voices')
            if voices and len(voices) > voice_index:
                self.tts.setProperty('voice', voices[voice_index].id)
        except Exception:
            pass

        def run_tts():
            try:
                self.tts.say(text)
                self.tts.runAndWait()
            except Exception:
                pass
            self.is_speaking = False
            if callback: callback()

        threading.Thread(target=run_tts, daemon=True).start()

    def stop(self):
        if self.is_speaking and self.tts:
            try:
                self.tts.stop()
            except Exception:
                pass
            self.is_speaking = False

class CortexUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cortex OS — Executive Suite (v3.3 Neural Natural Voices)")
        self.setGeometry(200, 200, 850, 620)

        self.speech = SpeechEngine()
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        header_layout = QHBoxLayout()
        self.orb = VisualOrb()
        header_layout.addWidget(self.orb)

        self.status_lbl = QLabel("STATUS: ONLINE & VOICE PROFILES LOADED")
        self.status_lbl.setStyleSheet("color: #3fb950; font-weight: bold; font-size: 11pt;")
        header_layout.addWidget(self.status_lbl)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Chat Tab
        chat_tab = QWidget()
        chat_layout = QVBoxLayout(chat_tab)
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        chat_layout.addWidget(self.chat_area)

        input_layout = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Command Cortex (e.g. 'Switch voice to Sonia', 'Open Gmail and email John')...")
        self.cmd_input.returnPressed.connect(self.send_command)
        input_layout.addWidget(self.cmd_input)

        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_command)
        input_layout.addWidget(self.send_btn)

        self.clear_btn = QPushButton("Clear Chat")
        self.clear_btn.setObjectName("clear_btn")
        self.clear_btn.clicked.connect(self.chat_area.clear)
        input_layout.addWidget(self.clear_btn)

        chat_layout.addLayout(input_layout)
        self.tabs.addTab(chat_tab, "Assistant Chat")

        # Settings Tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)

        form_group = QGroupBox("Voice & Neural Configuration (6 Human Profiles)")
        form_layout = QFormLayout()

        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["Sonia (Female Natural)", "Ryan (Male Executive)", "Aoife (Female Clear)",
                                   "Liam (Male Deep)", "Clara (Female Soft)", "Marcus (Male Tactical)"])
        form_layout.addRow(QLabel("Active Voice Persona:"), self.voice_combo)

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(100)
        self.speed_slider.setMaximum(250)
        self.speed_slider.setValue(175)
        form_layout.addRow(QLabel("Voice Speed Rate:"), self.speed_slider)

        form_group.setLayout(form_layout)
        settings_layout.addWidget(form_group)
        settings_layout.addStretch()

        self.tabs.addTab(settings_tab, "App Settings")

    def send_command(self):
        text = self.cmd_input.text().strip()
        if not text:
            return

        self.chat_area.append(f"<b>You:</b> {text}")
        self.cmd_input.clear()
        self.speech.stop()
        self.orb.set_state("active")

        payload = {
            "prompt": text,
            "voice_speed": self.speed_slider.value()
        }

        threading.Thread(target=self._dispatch_request, args=(payload,), daemon=True).start()

    def _dispatch_request(self, payload):
        try:
            r = requests.post("http://127.0.0.1:8000/query", json=payload, timeout=25)
            if r.status_code == 200:
                data = r.json()
                resp_text = data.get("response", "")
                self.chat_area.append(f"<b>Cortex:</b> {resp_text}\n")
                self.orb.set_state("speaking")

                # Map selected combo index to speech engine voice profile
                v_index = self.voice_combo.currentIndex()
                self.speech.speak(resp_text, speed=payload["voice_speed"], voice_index=v_index, callback=lambda: self.orb.set_state("ready"))
            else:
                self.chat_area.append(f"<b>Cortex Error:</b> {r.text}\n")
                self.orb.set_state("ready")
        except Exception as e:
            self.chat_area.append(f"<b>Cortex Error:</b> {str(e)}\n")
            self.orb.set_state("ready")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME_STYLE)
    win = CortexUI()
    win.show()
    sys.exit(app.exec_())