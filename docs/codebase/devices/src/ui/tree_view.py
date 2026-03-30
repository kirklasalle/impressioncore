# tree_view.py

import tkinter as tk
from tkinter import ttk

class TreeView:
    def __init__(self, master):
        self.tree = ttk.Treeview(master)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def display_hardware(self, hardware_data):
        for category, items in hardware_data.items():
            category_id = self.tree.insert('', 'end', text=category)
            for item in items:
                self.tree.insert(category_id, 'end', text=item)

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)