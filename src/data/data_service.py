import json
import os
from configuration.app_settings import Settings
from models.authentication.authentication import Method


class DataService():
    def __init__(self, message_service) -> None:
        self.message_service = message_service
        self.file_path = Settings.SYSTEM_FILE_PATH

        if not os.path.exists(self.file_path):
            # if not exist initalise the data file
            data = {'user_coins': 0}
            with open(self.file_path, 'w') as f:
                json.dump(data, f)
        else:
            with open(self.file_path, 'r') as f:
                self.data = json.load(f)

    def get_user_coin(self) -> int:
        return self.data['user_coins']

    def increment_user_coin(self, value: int) -> None:
        self.data['user_coins'] += value
        self.message_service.send(self, "Update coins", self.get_user_coin())

    def save_data(self) -> None:
        print("saving data...")
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f)
            
