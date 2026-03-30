# main_window.py

import tkinter as tk
from tkinter import ttk, filedialog
from .device_properties import DevicePropertiesWindow
import json
from datetime import datetime

class MainWindow:
    def __init__(self, master, hardware_detector):
        self.master = master
        self.hardware_detector = hardware_detector
        self.master.title("Device Manager")
        self.master.geometry("800x600")
        self.selected_items = {}
        self.create_widgets()

    def create_widgets(self):
        # Add Report button at the top
        self.button_frame = ttk.Frame(self.master)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.report_button = ttk.Button(self.button_frame, text="Generate Report", command=self.generate_report)
        self.report_button.pack(side=tk.LEFT)

        # Create treeview with checkbox column
        self.tree_view = ttk.Treeview(self.master, columns=('checkbox',))
        self.tree_view.heading('#0', text='Device')
        self.tree_view.heading('checkbox', text='Select')
        self.tree_view.column('checkbox', width=60, anchor='center')
        self.tree_view.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.master, orient=tk.VERTICAL, command=self.tree_view.yview)
        self.tree_view.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Modify bindings
        self.tree_view.bind('<ButtonRelease-1>', self.toggle_checkbox)
        self.tree_view.bind("<Double-1>", self.on_double_click)
        self.tree_view.bind("<Button-3>", self.show_context_menu)

        # Create context menu
        self.context_menu = tk.Menu(self.master, tearoff=0)
        self.context_menu.add_command(label="Properties", command=self.show_properties)

        self.status_bar = tk.Label(self.master, text="Status: Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        self.status_bar.config(text=f"Status: {message}")

    def display_hardware(self, hardware_data):
        for category, items in hardware_data.items():
            category_id = self.tree_view.insert('', 'end', text=category)
            for item in items:
                self.tree_view.insert(category_id, 'end', text=item, values=('☐',))

    def toggle_checkbox(self, event):
        item = self.tree_view.identify('item', event.x, event.y)
        column = self.tree_view.identify_column(event.x)
        
        if column == '#1' and self.tree_view.parent(item):  # checkbox column and not category
            current = self.tree_view.set(item, 'checkbox')
            self.tree_view.set(item, 'checkbox', '☐' if current == '☑' else '☑')

    def generate_report(self):
        selected_devices = []
        
        # Collect selected devices
        for category_id in self.tree_view.get_children():
            category = self.tree_view.item(category_id)['text']
            for device_id in self.tree_view.get_children(category_id):
                if self.tree_view.set(device_id, 'checkbox') == '☑':
                    device_name = self.tree_view.item(device_id)['text']
                    properties = self.hardware_detector.get_device_properties(category, device_name)
                    selected_devices.append({
                        'category': category,
                        'name': device_name,
                        'properties': properties
                    })

        if not selected_devices:
            tk.messagebox.showwarning("No Selection", "Please select at least one device.")
            return

        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=f"hardware_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        if file_path:
            self.save_report(file_path, selected_devices)

    def save_report(self, file_path, devices):
        with open(file_path, 'w') as f:
            f.write("Hardware Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")

            for device in devices:
                f.write(f"Category: {device['category']}\n")
                f.write(f"Device: {device['name']}\n")
                f.write("-"*30 + "\n")
                f.write("Properties:\n")
                for prop, value in device['properties'].items():
                    f.write(f"  {prop}: {value}\n")
                f.write("\n" + "="*50 + "\n\n")

    def show_context_menu(self, event):
        item = self.tree_view.identify('item', event.x, event.y)
        if item and self.tree_view.parent(item):  # Only show menu for devices, not categories
            self.tree_view.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def on_double_click(self, event):
        item = self.tree_view.selection()[0]
        if self.tree_view.parent(item):  # Only show properties for devices, not categories
            self.show_properties()

    def show_properties(self):
        item = self.tree_view.selection()[0]
        if self.tree_view.parent(item):
            category = self.tree_view.item(self.tree_view.parent(item))['text']
            device_name = self.tree_view.item(item)['text']
            properties = self.hardware_detector.get_device_properties(category, device_name)
            DevicePropertiesWindow(self.master, f"{device_name} Properties", properties)