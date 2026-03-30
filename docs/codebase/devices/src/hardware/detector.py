import wmi

class HardwareDetector:
    def __init__(self):
        self.wmi = wmi.WMI()


    
    def _safe_detect(self, wmi_class, category, name_formatter):
        """Helper to safely detect hardware components."""
        items = []
        try:
            for item in getattr(self.wmi, wmi_class)():
                try:
                    name = name_formatter(item)
                    items.append({
                        'category': category,
                        'name': name
                    })
                except Exception as e:
                    items.append({
                        'category': category,
                        'name': f"Error reading device: {str(e)}"
                    })
        except Exception as e:
            items.append({
                'category': category,
                'name': f"Detection failed: {str(e)}"
            })
        return items

    def detect_hardware(self):
        hardware_list = []
        
        # Detect processors
        hardware_list.extend(self._safe_detect(
            'Win32_Processor',
            'Processors',
            lambda p: f"{p.Name.strip()} ({p.NumberOfCores} cores, {p.NumberOfLogicalProcessors} threads)"
        ))

        # Detect motherboard
        hardware_list.extend(self._safe_detect(
            'Win32_BaseBoard',
            'Motherboard',
            lambda b: f"{b.Manufacturer.strip()} {b.Product.strip()}"
        ))

        # Detect memory modules
        hardware_list.extend(self._safe_detect(
            'Win32_PhysicalMemory',
            'Memory',
            lambda m: f"{m.Manufacturer.strip()} {round(int(m.Capacity) / (1024**3), 2)}GB {m.Speed}MHz"
        ))

        # Detect display devices
        hardware_list.extend(self._safe_detect(
            'Win32_VideoController',
            'Display adapters',
            lambda d: f"{d.Name.strip()} ({d.AdapterRAM/(1024**3):.2f}GB)" if d.AdapterRAM else d.Name.strip()
        ))

        # Detect disk drives
        hardware_list.extend(self._safe_detect(
            'Win32_DiskDrive',
            'Disk drives',
            lambda d: f"{d.Caption.strip()} ({round(int(d.Size) / (1024**3), 2)}GB)"
        ))

        # Detect network adapters
        try:
            for nic in self.wmi.Win32_NetworkAdapter():
                if nic.PhysicalAdapter:
                    hardware_list.append({
                        'category': 'Network adapters',
                        'name': f"{nic.Name.strip()} ({nic.AdapterType})"
                    })
        except Exception as e:
            hardware_list.append({'category': 'Network adapters', 'name': f"Error: {e}"})

        # Detect sound devices
        hardware_list.extend(self._safe_detect(
            'Win32_SoundDevice',
            'Sound devices',
            lambda s: s.Name.strip()
        ))

        # Detect USB controllers
        hardware_list.extend(self._safe_detect(
            'Win32_USBController',
            'USB controllers',
            lambda u: u.Name.strip()
        ))

        # Detect USB devices
        hardware_list.extend(self._safe_detect(
            'Win32_USBHub',
            'USB devices',
            lambda u: u.Name.strip()
        ))

        # Detect BIOS
        hardware_list.extend(self._safe_detect(
            'Win32_BIOS',
            'BIOS',
            lambda b: f"{b.Manufacturer.strip()} {b.Version.strip()}"
        ))

        # Detect optical drives
        hardware_list.extend(self._safe_detect(
            'Win32_CDROMDrive',
            'Optical drives',
            lambda c: c.Name.strip()
        ))

        return hardware_list

    def get_device_properties(self, category, device_name):
        """Get detailed properties for a specific device."""
        wmi_mapping = {
            'Processors': 'Win32_Processor',
            'Motherboard': 'Win32_BaseBoard',
            'Memory': 'Win32_PhysicalMemory',
            'Display adapters': 'Win32_VideoController',
            'Disk drives': 'Win32_DiskDrive',
            'Network adapters': 'Win32_NetworkAdapter',
            'Sound devices': 'Win32_SoundDevice',
            'USB controllers': 'Win32_USBController',
            'USB devices': 'Win32_USBHub',
            'BIOS': 'Win32_BIOS',
            'Optical drives': 'Win32_CDROMDrive'
        }
        
        if category not in wmi_mapping:
            return {}

        wmi_class = wmi_mapping[category]
        devices = getattr(self.wmi, wmi_class)()
        
        for device in devices:
            # Strip manufacturer/name from device_name if present
            clean_name = device_name.split('(')[0].strip()
            if clean_name in str(device.Name):
                # Convert WMI object to dictionary
                properties = {}
                for prop in device.properties:
                    value = getattr(device, prop)
                    if value is not None:
                        properties[prop] = str(value)
                return properties
        
        return {}