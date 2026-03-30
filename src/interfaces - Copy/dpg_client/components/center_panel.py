import threading
import time

import cv2
import dearpygui.dearpygui as dpg
import numpy as np

from src.interfaces.dpg_client.async_utils import api
from src.orchestrator.orbcloud_audio import OrbCloudAudio


class CenterPanel:
    def __init__(self):
        self.tags = {
            "tex_alpha": "tex_vision_alpha",
            "tex_beta": "tex_vision_beta",
            "chat_history": "child_chat_history",
            "input_msg": "input_message",
            "btn_mic": "btn_mic_toggle"
        }
        self.audio = OrbCloudAudio()
        self.is_listening = False

        # Initialize textures (640x480 placeholder)
        self.width = 640
        self.height = 480
        self.blank_texture = np.zeros((self.height, self.width, 4), dtype=np.float32).flatten()

        # Register textures
        with dpg.texture_registry(show=False):
            dpg.add_dynamic_texture(width=self.width, height=self.height, default_value=self.blank_texture, tag=self.tags["tex_alpha"])
            dpg.add_dynamic_texture(width=self.width, height=self.height, default_value=self.blank_texture, tag=self.tags["tex_beta"])

        # Start Video Thread
        self.running = True
        threading.Thread(target=self._video_loop, daemon=True).start()

    def _video_loop(self):
        # Connect to existing backend stream
        stream_url = "http://localhost:8000/v1/vision/stream"
        cap = cv2.VideoCapture(stream_url)

        while self.running:
            try:
                ret, frame = cap.read()
                if ret:
                    # Resize to match texture
                    frame = cv2.resize(frame, (self.width, self.height))
                    # Convert BGR to RGBA
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                    # Normalize 0-255 to 0.0-1.0
                    data = frame.astype(np.float32) / 255.0
                    dpg.set_value(self.tags["tex_alpha"], data.flatten())
                    # Mirror to beta for now (or fetch second stream if avail)
                    dpg.set_value(self.tags["tex_beta"], data.flatten())
            except Exception as e:
                print(f"Stream error: {e}")
                time.sleep(1)
            time.sleep(0.016) # ~60fps cap

    def send_message(self):
        msg = dpg.get_value(self.tags["input_msg"])
        if not msg:
            return

        # UI Optimistic update
        dpg.add_text(f"USER: {msg}", parent=self.tags["chat_history"], color=(34, 211, 238, 255))
        dpg.set_value(self.tags["input_msg"], "")

        def on_response(response):
            if response.status_code == 200:
                data = response.json()
                reply = data.get("response", "...")
                dpg.add_text(f"CORE: {reply}", parent=self.tags["chat_history"], color=(255, 255, 255, 255))
                # Auto-scroll?
                # dpg.set_y_scroll(self.tags["chat_history"], -1) # Not easily supported yet

        api.post("/v1/process", json={"prompt": msg, "voice_enabled": True}, callback=on_response)

    def toggle_voice(self):
        if self.is_listening:
            self.audio.stop_listening()
            self.is_listening = False
            dpg.configure_item(self.tags["btn_mic"], label="MIC OFF", base_color=(100, 0, 0)) # Red-ish
        else:
            if not self.audio.open():
                print("Failed to open audio")
                return

            self.is_listening = True
            dpg.configure_item(self.tags["btn_mic"], label="LISTENING...", base_color=(0, 200, 0)) # Green

            def on_speech(text):
                print(f"Heard: {text}")
                current_text = dpg.get_value(self.tags["input_msg"])
                dpg.set_value(self.tags["input_msg"], f"{current_text} {text}".strip())

            self.audio.start_listening(callback=on_speech)

    def render(self):
        with dpg.child_window(border=False):
            # Video Area
            with dpg.group(horizontal=True):
                 # Aspect ratio? We'll just fit width
                 # avail_width = dpg.get_content_region_avail()[0] # CAUSING CRASH
                 # dpg.add_image(self.tags["tex_alpha"], width=avail_width/2 - 5, height=300)
                 # dpg.add_image(self.tags["tex_beta"], width=avail_width/2 - 5, height=300)
                 # Hardcoded for layout stability first
                 dpg.add_image(self.tags["tex_alpha"], width=400, height=300)
                 dpg.add_image(self.tags["tex_beta"], width=400, height=300)

            dpg.add_spacer(height=20)

            # Chat Area
            with dpg.child_window(tag=self.tags["chat_history"], height=-50, border=True):
                dpg.add_text("System initialized. Ready for input.", color=(100, 100, 100))

            # Input Area
            with dpg.group(horizontal=True):
                dpg.add_button(tag=self.tags["btn_mic"], label="MIC", width=50, callback=self.toggle_voice)
                dpg.add_input_text(tag=self.tags["input_msg"], hint="Message ImpressionCore...", width=-100, on_enter=True, callback=self.send_message)
                dpg.add_button(label="SEND", width=80, callback=self.send_message)

    def shutdown(self):
        self.running = False
        if self.is_listening:
            self.audio.close()
