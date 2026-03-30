import dearpygui.dearpygui as dpg

from src.interfaces.dpg_client.async_utils import api


class RightSidebar:
    def __init__(self):
        self.tags = {
            "val_x": "txt_track_x",
            "val_y": "txt_track_y",
            "val_z": "txt_track_z",
            "count_detect": "txt_detect_count",
            "list_sessions": "list_sessions"
        }

    def refresh_sessions(self):
        def on_sessions(response):
            if response.status_code == 200:
                data = response.json()
                # data is list of dicts {id, title, timestamp}
                items = [f"{s.get('title', 'Untitled')} ({s.get('timestamp', '')[:10]})" for s in data]
                dpg.configure_item(self.tags["list_sessions"], items=items)

        api.get("/v1/sessions", on_sessions)

    def update_telemetry(self):
        def on_telemetry(response):
            if response.status_code == 200:
                data = response.json()
                pos = data.get("pos", [0,0,0])
                dpg.set_value(self.tags["val_x"], f"{pos[0]:.3f}")
                dpg.set_value(self.tags["val_y"], f"{pos[1]:.3f}")
                dpg.set_value(self.tags["val_z"], f"{pos[2]:.3f}")

                detects = data.get("detections", {})
                count = sum(len(v) for v in detects.values())
                dpg.set_value(self.tags["count_detect"], f"{count} Views")

        api.get("/v1/vision/telemetry", on_telemetry)

    def render(self):
        with dpg.child_window(width=300, border=False):
            # Raw Tracking Data
            with dpg.group():
                dpg.add_text("RAW TRACKING DATA", color=(34, 211, 238, 255))
                with dpg.group(horizontal=True):
                    for label, tag in [("X-Pos", self.tags["val_x"]), ("Y-Pos", self.tags["val_y"]), ("Z-Depth", self.tags["val_z"])]:
                        with dpg.group():
                            dpg.add_text(label)
                            dpg.add_text("0.000", tag=tag, color=(34, 211, 238, 255))
                            dpg.add_spacer(width=60)

                dpg.add_spacer(height=5)
                with dpg.group(horizontal=True):
                    dpg.add_text("Active Detections")
                    dpg.add_text("0 Views", tag=self.tags["count_detect"], color=(34, 211, 238, 255))

            dpg.add_spacer(height=20)
            dpg.add_button(label="INITIALIZE NEW PATHWAY", width=-1, height=40)

            dpg.add_spacer(height=20)

            # Temporal Archive
            with dpg.group():
                dpg.add_text("TEMPORAL ARCHIVE", color=(100, 116, 139, 255))
                dpg.add_listbox(tag=self.tags["list_sessions"], items=[], num_items=15, width=-1)

        # Initial Load
        self.refresh_sessions()
