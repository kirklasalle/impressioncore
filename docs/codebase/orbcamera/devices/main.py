import tkinter as tk
from ui.main_window import MainWindow
from src.hardware.detector import HardwareDetector
from src.hardware.categories import HardwareCategory

def main():
    root = tk.Tk()
    hardware_detector = HardwareDetector()
    hardware_category = HardwareCategory()
    app = MainWindow(root, hardware_detector)
    
    # Detect and categorize hardware
    hardware_data = hardware_detector.detect_hardware()
    for item in hardware_data:
        hardware_category.add_hardware(item['category'], item['name'])
    
    # Display hardware in tree view
    app.display_hardware(hardware_category.categories)
    root.mainloop()

if __name__ == "__main__":
    main()