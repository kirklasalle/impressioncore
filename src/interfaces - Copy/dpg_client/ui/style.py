import dearpygui.dearpygui as dpg


def load_theme():
    # Palette based on ImpressionCore screenshot (Cyan/Slate/Dark)
    COLOR_BG = (15, 23, 42, 255)        # bg-slate-900
    COLOR_PANEL = (30, 41, 59, 200)     # slightly lighter slate for panels
    COLOR_BORDER = (34, 211, 238, 80)   # text-cyan-400 (dimmed for border)
    COLOR_ACCENT = (34, 211, 238, 255)  # text-cyan-400
    COLOR_TEXT = (203, 213, 225, 255)   # text-slate-300
    COLOR_TEXT_DIM = (148, 163, 184, 255)# text-slate-400

    with dpg.theme() as global_theme, dpg.theme_component(dpg.mvAll):
        # Window & Child Bg
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, COLOR_BG)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, COLOR_PANEL)
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, COLOR_PANEL)

        # Text
        dpg.add_theme_color(dpg.mvThemeCol_Text, COLOR_TEXT)
        dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, COLOR_TEXT_DIM)

        # Borders
        dpg.add_theme_color(dpg.mvThemeCol_Border, COLOR_BORDER)
        dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (0, 0, 0, 0))
        dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
        dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 1)

        # Inputs / Frames
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 100))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (34, 211, 238, 40))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (34, 211, 238, 60))
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)

        # Buttons
        dpg.add_theme_color(dpg.mvThemeCol_Button, (34, 211, 238, 20))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (34, 211, 238, 60))
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (34, 211, 238, 100))
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)

        # Sliders/Grab
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, COLOR_ACCENT)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (103, 232, 249, 255)) # Cyan-300

        # Scrollbar
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, (34, 211, 238, 40))
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, (34, 211, 238, 80))
        dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, (34, 211, 238, 120))
        dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 12)

        # Titles/Headers
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, COLOR_BG)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, COLOR_BG)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, COLOR_BG)

    dpg.bind_theme(global_theme)

def load_font():
    # Try to load a system monospace font, fallback to default
    try:
        # Create font registry
        with dpg.font_registry():
            # Attempt to use Consolas (standard on Windows)
            # Size 13 matches the "small/tech" look
            font_path = "C:/Windows/Fonts/consola.ttf"
            with dpg.font(font_path, 13) as default_font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)

            dpg.bind_font(default_font)
    except Exception as e:
        print(f"Font load warning: {e}. Using default.")
