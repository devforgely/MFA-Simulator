import json
import os
from configuration.app_settings import Settings
from models.authentication.authentication import Method


class DataService():
    def __init__(self) -> None:
        self.file_path = Settings.SYSTEM_FILE_PATH
        if not os.path.exists(self.file_path):
            data = {'user_coins': 0}
            with open(self.file_path, 'w') as f:
                json.dump(data, f)

    def increment_user_coin(self, value: int) -> None:
        with open(self.file_path, 'r') as f:
            data = json.load(f)
        data['user_coins'] += value

        with open(self.file_path, 'w') as f:
            json.dump(data, f)
            
