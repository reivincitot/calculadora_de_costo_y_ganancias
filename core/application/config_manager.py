import json
import os


class ConfigManager:
    def __init__(self):
        self.config_path = "app_config.json"
        self.defaults = {
            "empresa": "Mi Empresa",
            "moneda": "CLP",
            "decimales": 2
        }

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                return json.load(f)
        return self.defaults

    def save_config(self, config: dict):
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
