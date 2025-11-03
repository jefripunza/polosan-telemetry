import json
import os

class DataJSON:
    def __init__(self, filename: str, init_value=None):
        self._filename = filename
        self._init_value = init_value if init_value is not None else {}

        if not self._file_exists():
            self.write(self._init_value)

    def _file_exists(self) -> bool:
        try:
            return self._filename in os.listdir()
        except OSError:
            return False

    def read(self):
        try:
            with open(self._filename, 'r') as f:
                return json.load(f)
        except (OSError, ValueError):
            return self._init_value

    def write(self, data) -> bool:
        try:
            with open(self._filename, 'w') as f:
                json.dump(data, f)
            return True
        except OSError:
            return False

    # 🔹 get value by key (dict-like)
    def get(self, key, default=None):
        data = self.read()
        return data.get(key, default) if data else default

    # 🔹 set value by key and save
    def set(self, key, value):
        data = self.read() or {}
        data[key] = value
        self.write(data)
