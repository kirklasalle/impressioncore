import wmi
import logging

logger = logging.getLogger(__name__)

class HardwareDetector:
    def __init__(self):
        self.wmi = wmi.WMI()

    def detect_hardware(self):
        hardware_list = []
        
        try:
            # Detect processors
            for processor in self.wmi.Win32_Processor():
                try:
                    cores = processor.NumberOfCores if processor.NumberOfCores else "Unknown"
                    logical = processor.NumberOfLogicalProcessors if processor.NumberOfLogicalProcessors else "Unknown"
                    name = processor.Name.strip() if processor.Name else "Unknown Processor"
                    hardware_list.append({
                        'category': 'Processors',
                        'name': f"{name} ({cores} cores, {logical} threads)"
                    })
                except Exception as e:
                    logger.debug(f"Error processing processor info: {e}")
                    hardware_list.append({
                        'category': 'Processors',
                        'name': "Unknown Processor"
                    })

            # Detect motherboard
            for board in self.wmi.Win32_BaseBoard():
                try:
                    manufacturer = board.Manufacturer.strip() if board.Manufacturer else "Unknown"
                    product = board.Product.strip() if board.Product else "Motherboard"
                    hardware_list.append({
                        'category': 'Motherboard',
                        'name': f"{manufacturer} {product}"
                    })
                except Exception as e:
                    logger.debug(f"Error processing motherboard info: {e}")
                    hardware_list.append({
                        'category': 'Motherboard',
                        'name': "Unknown Motherboard"
                    })

            # Detect memory modules
            for memory in self.wmi.Win32_PhysicalMemory():
                try:
                    if memory.Capacity:
                        size_gb = round(int(memory.Capacity) / (1024**3), 2)
                    else:
                        size_gb = "Unknown"
                        
                    manufacturer = memory.Manufacturer.strip() if memory.Manufacturer else "Unknown"
                    speed = memory.Speed if memory.Speed else "Unknown"
                    
                    hardware_list.append({
                        'category': 'Memory',
                        'name': f"{manufacturer} {size_gb}GB {speed}MHz"
                    })
                except Exception as e:
                    logger.debug(f"Error processing memory info: {e}")
                    hardware_list.append({
                        'category': 'Memory',
                        'name': "Unknown Memory Module"
                    })

            # Detect display devices
            for display in self.wmi.Win32_VideoController():
                try:
                    name = display.Name.strip() if display.Name else "Unknown Display"
                    
                    if display.AdapterRAM:
                        ram_gb = f"({display.AdapterRAM/(1024**3):.2f}GB)"
                    else:
                        ram_gb = ""
                        
                    hardware_list.append({
                        'category': 'Display adapters',
                        'name': f"{name} {ram_gb}"
                    })
                except Exception as e:
                    logger.debug(f"Error processing display info: {e}")
                    hardware_list.append({
                        'category': 'Display adapters',
                        'name': "Unknown Display Adapter"
                    })

            # Detect disk drives
            for disk in self.wmi.Win32_DiskDrive():
                try:
                    caption = disk.Caption.strip() if disk.Caption else "Unknown Disk"
                    
                    if disk.Size is not None:
                        size_gb = round(int(disk.Size) / (1024**3), 2)
                        size_str = f"({size_gb}GB)"
                    else:
                        size_str = ""
                        
                    hardware_list.append({
                        'category': 'Disk drives',
                        'name': f"{caption} {size_str}"
                    })
                except Exception as e:
                    logger.debug(f"Error processing disk info: {e}")
                    hardware_list.append({
                        'category': 'Disk drives',
                        'name': "Unknown Disk"
                    })

            # Detect network adapters
            for nic in self.wmi.Win32_NetworkAdapter():
                try:
                    if nic.PhysicalAdapter:
                        name = nic.Name.strip() if nic.Name else "Unknown Network Adapter"
                        adapter_type = nic.AdapterType if nic.AdapterType else "Unknown"
                        hardware_list.append({
                            'category': 'Network adapters',
                            'name': f"{name} ({adapter_type})"
                        })
                except Exception as e:
                    logger.debug(f"Error processing network adapter info: {e}")

            # Detect sound devices
            for sound in self.wmi.Win32_SoundDevice():
                try:
                    name = sound.Name.strip() if sound.Name else "Unknown Sound Device"
                    hardware_list.append({
                        'category': 'Sound devices',
                        'name': name
                    })
                except Exception as e:
                    logger.debug(f"Error processing sound device info: {e}")

            # Detect USB controllers
            for usb in self.wmi.Win32_USBController():
                try:
                    name = usb.Name.strip() if usb.Name else "Unknown USB Controller"
                    hardware_list.append({
                        'category': 'USB controllers',
                        'name': name
                    })
                except Exception as e:
                    logger.debug(f"Error processing USB controller info: {e}")

            # Detect USB devices
            for usb in self.wmi.Win32_USBHub():
                try:
                    name = usb.Name.strip() if usb.Name else "Unknown USB Device"
                    hardware_list.append({
                        'category': 'USB devices',
                        'name': name
                    })
                except Exception as e:
                    logger.debug(f"Error processing USB device info: {e}")

            # Detect BIOS
            for bios in self.wmi.Win32_BIOS():
                try:
                    manufacturer = bios.Manufacturer.strip() if bios.Manufacturer else "Unknown"
                    version = bios.Version.strip() if bios.Version else "Unknown"
                    hardware_list.append({
                        'category': 'BIOS',
                        'name': f"{manufacturer} {version}"
                    })
                except Exception as e:
                    logger.debug(f"Error processing BIOS info: {e}")

            # Detect optical drives
            for cd in self.wmi.Win32_CDROMDrive():
                try:
                    name = cd.Name.strip() if cd.Name else "Unknown Optical Drive"
                    hardware_list.append({
                        'category': 'Optical drives',
                        'name': name
                    })
                except Exception as e:
                    logger.debug(f"Error processing optical drive info: {e}")
                    
        except Exception as e:
            logger.error(f"Error detecting hardware: {e}")

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

        try:
            wmi_class = wmi_mapping[category]
            devices = getattr(self.wmi, wmi_class)()
            
            for device in devices:
                # Strip manufacturer/name from device_name if present
                clean_name = device_name.split('(')[0].strip()
                try:
                    if device.Name and clean_name in str(device.Name):
                        # Convert WMI object to dictionary
                        properties = {}
                        for prop in device.properties:
                            try:
                                value = getattr(device, prop)
                                if value is not None:
                                    properties[prop] = str(value)
                            except Exception as e:
                                logger.debug(f"Error getting property {prop}: {e}")
                        return properties
                except Exception as e:
                    logger.debug(f"Error checking device name: {e}")
        except Exception as e:
            logger.error(f"Error getting device properties: {e}")
        
        return {}