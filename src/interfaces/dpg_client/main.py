import dearpygui.dearpygui as dpg

from src.interfaces.dpg_client.components.center_panel import CenterPanel
from src.interfaces.dpg_client.components.sidebar_left import LeftSidebar
from src.interfaces.dpg_client.components.sidebar_right import RightSidebar
from src.interfaces.dpg_client.ui import style


def main():
    dpg.create_context()

    # Load Style
    style.load_theme()
    style.load_font()

    # Create Components
    left_panel = LeftSidebar()
    right_panel = RightSidebar()
    center_panel = CenterPanel()

    def resize_callback(sender, app_data):
        # app_data is [width, height]
        width, _height = app_data[0], app_data[1]
        center_width = width - 620 # 300 left + 300 right + padding
        if center_width < 400:
            center_width = 400

        # We can't easily resize the center child window dynamically by tag if it wasn't saved?
        # Ideally components expose their container tag
        pass

    with dpg.window(tag="Primary Window"), dpg.group(horizontal=True):
        left_panel.render()
        center_panel.render()
        right_panel.render()

    dpg.create_viewport(title='ImpressionCore B3 [Native]', width=1280, height=800)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window("Primary Window", True)

    # Start loop
    try:
        dpg.start_dearpygui()
    except KeyboardInterrupt:
        pass
    finally:
        center_panel.shutdown()
        dpg.destroy_context()

if __name__ == "__main__":
    main()
