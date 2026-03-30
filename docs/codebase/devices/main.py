import tkinter as tk
from tkinter import messagebox
import logging
import sys
from src.ui.main_window import MainWindow
from src.hardware.detector import HardwareDetector
from src.hardware.categories import HardwareCategory

def setup_logging():
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("device_manager_error.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    setup_logging()
    try:
        root = tk.Tk()
        hardware_detector = HardwareDetector()
        hardware_category = HardwareCategory()
        app = MainWindow(root, hardware_detector)
        
        # Detect and categorize hardware
        try:
            hardware_data = hardware_detector.detect_hardware()
            for item in hardware_data:
                hardware_category.add_hardware(item['category'], item['name'])
        except Exception as e:
            logging.error(f"Error during hardware detection: {str(e)}")
            messagebox.showerror("Detection Error", f"An error occurred while detecting hardware:\n{str(e)}")
        
        # Display hardware in tree view
        app.display_hardware(hardware_category.categories)
        root.mainloop()

    except Exception as e:
        logging.critical(f"Critical Application Error: {str(e)}")
        # If root exists, try to show message box, otherwise stderr
        try:
            messagebox.showerror("Critical Error", f"Application crashed:\n{str(e)}")
        except:
            print(f"Critical Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()