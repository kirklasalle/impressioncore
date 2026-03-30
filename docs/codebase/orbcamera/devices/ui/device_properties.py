import tkinter as tk
from tkinter import ttk

class DevicePropertiesWindow:
    def __init__(self, parent, title, properties):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("600x400")
        
        # Create treeview
        self.tree = ttk.Treeview(self.window, columns=('Value',), show='headings')
        self.tree.heading('Value', text='Value')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate properties
        for prop, value in properties.items():
            self.tree.insert('', tk.END, values=(f"{prop}: {value}",))
