import dearpygui.dearpygui as dpg

from src.interfaces.dpg_client.async_utils import api


class LeftSidebar:
    def __init__(self):
        self.tags = {
            "cam_primary": "cb_cam_primary",
            "cam_secondary": "cb_cam_secondary",
            "mic_input": "cb_mic_input",
            "val_brightness": "slider_brightness",
            "val_contrast": "slider_contrast",
            "val_saturation": "slider_saturation",
            "val_gain": "slider_gain",
            "status_model": "txt_status_model",
            "status_quant": "txt_status_quant",
            "status_temp_l": "txt_temp_l",
            "status_temp_r": "txt_temp_r",
            "status_temp_e": "txt_temp_e",
            "vram_bar": "progress_vram"
        }
        self.vision_controls = {"brightness": 0.5, "contrast": 0.5, "saturation": 0.5, "gain": 0.5}

    def refresh_devices(self):
        def on_hardware(response):
            if response.status_code == 200:
                data = response.json()
                cams = [f"{c['model']} ({c['id']})" for c in data.get('detected_cameras', [])]
                # Update Combos
                dpg.configure_item(self.tags["cam_primary"], items=cams)
                dpg.configure_item(self.tags["cam_secondary"], items=cams)

        def on_audio(response):
            if response.status_code == 200:
                data = response.json()
                mics = [f"{d['name']} ({d['id']})" for d in data.get('devices', [])]
                dpg.configure_item(self.tags["mic_input"], items=mics)

        api.get("/v1/hardware", on_hardware)
        api.get("/v1/audio/devices", on_audio)

    def update_image_control(self, sender, app_data, user_data):
        # user_data is the key (e.g., "brightness")
        self.vision_controls[user_data] = app_data
        # Debounce or fire async? For sliders, fire async but maybe rate limit?
        # For now, fire directly.
        api.post("/v1/vision/controls", json={"params": {user_data: app_data}})

    def render(self):
        with dpg.child_window(width=300, border=False):
            # Header
            dpg.add_text("IMPRESSIONCORE B3", color=(34, 211, 238, 255))
            dpg.add_separator()
            dpg.add_spacer(height=10)

            # Hardware Config
            with dpg.group():
                dpg.add_text("HARDWARE CONFIGURATION", color=(100, 116, 139, 255)) # slate-500
                dpg.add_button(label="Refresh", width=-1, callback=lambda: self.refresh_devices())

                dpg.add_text("Primary Camera")
                dpg.add_combo(tag=self.tags["cam_primary"], width=-1)

                dpg.add_text("Secondary Camera")
                dpg.add_combo(tag=self.tags["cam_secondary"], width=-1)

                dpg.add_text("Microphone Input")
                dpg.add_combo(tag=self.tags["mic_input"], width=-1)

                dpg.add_button(label="VERIFY INTERFACE INTEGRITY", width=-1)

            dpg.add_spacer(height=20)

            # Image Suite
            with dpg.group():
                with dpg.group(horizontal=True):
                    dpg.add_text("IMAGE SUITE", color=(34, 211, 238, 255))

                for label, key, tag in [
                    ("Brightness", "brightness", self.tags["val_brightness"]),
                    ("Contrast", "contrast", self.tags["val_contrast"]),
                    ("Saturation", "saturation", self.tags["val_saturation"]),
                    ("Gain", "gain", self.tags["val_gain"])
                ]:
                    dpg.add_text(label)
                    dpg.add_slider_float(
                        tag=tag,
                        default_value=0.5,
                        max_value=1.0,
                        callback=self.update_image_control,
                        user_data=key,
                        width=-1
                    )

                dpg.add_button(label="RUN SYSTEM AUDIT", width=-1)

            dpg.add_spacer(height=20)

            # Neural Status
            with dpg.group():
                dpg.add_text("NEURAL STATUS", color=(100, 116, 139, 255))
                dpg.add_text("NOMINAL", color=(34, 211, 238, 255), indent=200) # Hacky alignment

                dpg.add_text("Active Core")
                dpg.add_input_text(tag=self.tags["status_model"], readonly=True, default_value="Loading...", width=-1)

                with dpg.group(horizontal=True):
                    with dpg.group():
                        dpg.add_text("Quantization")
                        dpg.add_text("Unknown", tag=self.tags["status_quant"], color=(34, 211, 238, 255))
                    dpg.add_spacer(width=50)
                    with dpg.group():
                        dpg.add_text("Compute Device")
                        dpg.add_text("CPU", color=(34, 211, 238, 255))

                dpg.add_spacer(height=5)
                dpg.add_text("Neural Temperatures")
                with dpg.group(horizontal=True):
                    for label, tag in [("Left", self.tags["status_temp_l"]), ("Right", self.tags["status_temp_r"]), ("Exec", self.tags["status_temp_e"])]:
                        with dpg.group():
                            dpg.add_text(label)
                            dpg.add_button(label="0.0", tag=tag, width=60)

                dpg.add_spacer(height=5)
                dpg.add_text("VRAM Allocation")
                dpg.add_progress_bar(tag=self.tags["vram_bar"], default_value=0.0, width=-1, height=5)

        # Initial Load
        self.refresh_devices()
