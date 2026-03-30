import platform
import psutil

def get_system_info():
    """Retrieve system information including OS, CPU, and memory."""
    system_info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "CPU": {
            "Physical Cores": psutil.cpu_count(logical=False),
            "Total Cores": psutil.cpu_count(logical=True),
            "Max Frequency (MHz)": psutil.cpu_freq().max,
        },
        "Memory": {
            "Total (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
            "Available (GB)": round(psutil.virtual_memory().available / (1024 ** 3), 2),
            "Used (GB)": round(psutil.virtual_memory().used / (1024 ** 3), 2),
        }
    }
    return system_info