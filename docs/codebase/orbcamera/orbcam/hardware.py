import wmi
import logging

logger = logging.getLogger(__name__)

class HardwareDetector:
    def __init__(self):
        try:
            self.wmi = wmi.WMI()
        except Exception as e:
            logger.error(f"Failed to initialize WMI: {e}")
            self.wmi = None

    def detect_hardware(self):
        """Detect hardware devices in the system."""
        if not self.wmi:
            return []
            
        hardware_list = []
        
        # Detect USB devices (which includes cameras)
        for usb in self.wmi.Win32_USBHub():
            if usb.Name:  # Add null check
                hardware_list.append({
                    'category': 'USB devices',
                    'name': usb.Name.strip()
                })
            else:
                hardware_list.append({
                    'category': 'USB devices',
                    'name': "Unknown USB Device"
                })

        # Detect cameras through WMI
        for device in self.wmi.Win32_PnPEntity():
            if device.Name and "camera" in device.Name.lower():  # Add null check
                hardware_list.append({
                    'category': 'Cameras',
                    'name': device.Name.strip()
                })

        return hardware_list

    def get_device_properties(self, category: str, device_name: str) -> dict:
        """Get properties for a specific device."""
        if not self.wmi:
            return {}

        properties = {}
        
        if category == 'USB devices':
            for device in self.wmi.Win32_USBHub():
                if device_name in str(device.Name):
                    for prop in device.properties:
                        value = getattr(device, prop)
                        if value is not None:
                            properties[prop] = str(value)
                    break

        return properties
