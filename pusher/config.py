import json
import os
from pathlib import Path

APP_NAME = "pusher"

class Config:
    def __init__(self):
        self.config_dir = Path.home() / ".config" / APP_NAME
        self.config_file = self.config_dir / "config.json"
        self.data = {
            "source_dir": None,
            "dest_dir": None
        }
        self.load()

    def load(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.data.update(data)
            except (json.JSONDecodeError, OSError):
                pass # Start with defaults

    def save(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.data, f, indent=4)
        except OSError as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self.save()
