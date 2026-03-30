# 1. First Steps

**Created:** December 27, 2025  
**Updated:** December 29, 2025  
**Author:** ImpressionCore Team  
**Tags:** #docs\dearpygui\first_steps.md #documentation  
**Category:** Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

## 1.1. Installing

Python 3.6 (64 bit) or above is required.

```bash
pip install dearpygui
```

## 1.2. First Run

Confirm the pip install by running the code block below.

```python
import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=600, height=300)

with dpg.window(label="Example Window"):
    dpg.add_text("Hello, world")
    dpg.add_button(label="Save")
    dpg.add_input_text(label="string", default_value="Quick brown fox")
    dpg.add_slider_float(label="float", default_value=0.273, max_value=1)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
```

## 1.3. Demo

DPG has a complete built-in demo/showcase. It is a good idea to look into this demo.

```python
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=600, height=600)

demo.show_demo()

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
```

**Note**: The main script must always:

- Create the context `create_context`
- Create the viewport `create_viewport`
- Setup dearpygui `setup_dearpygui`
- Show the viewport `show_viewport`
- Start dearpygui `start_dearpygui`
- Clean up the context `destroy_context`
