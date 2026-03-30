class HardwareCategory:
    def __init__(self):
        self.categories = {}

    def add_hardware(self, category, hardware_item):
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(hardware_item)

    def get_hardware_by_category(self, category):
        return self.categories.get(category, [])

    def get_all_categories(self):
        return list(self.categories.keys())