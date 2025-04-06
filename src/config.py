import os
import json

class Config:
    def __init__(self):
        self.config_file = os.path.expanduser('~/.config/vidmask/config.json')
        self.config = self.load()

    def load(self):
        """Load config from file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
        return {
            'devices': {
                'input': '',
                'output': ''
            }
        }

    def save(self):
        """Save config to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, section, key=None, default=None):
        """Get config value with default"""
        if key is None:
            # If no key provided, treat section as key
            return self.config.get(section, default)
        return self.config.get(section, {}).get(key, default)

    def set(self, section, key, value):
        """Set config value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save()

    def __getitem__(self, key):
        """Allow dict-like access"""
        return self.config.get(key, {}) 