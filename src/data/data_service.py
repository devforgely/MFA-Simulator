from configuration.app_settings import Settings
from models.authentication.authentication import Method
import json
import os
import markdown
import random

class Note:
    def __init__(self, title, content):
        self.title = title
        self.content = content

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

        self.notes = self.read_notes_from_directory('data/notes')

    def get_user_coin(self) -> int:
        return self.data['user_coins']

    def increment_user_coin(self, value: int) -> None:
        self.data['user_coins'] += value
        self.message_service.send(self, "Update coins", self.get_user_coin())

    def save_data(self) -> None:
        print("saving data...")
        with open(self.file_path, 'w') as f:
            json.dump(self.data, f)


    def get_security_questions(self) -> list:
        try:
            with open('data/security_questions.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            print("File is not found")
            return []
        
        # Select 9 random questions
        return random.sample(data['securityQuestions'], 9)


    def read_notes_from_directory(self, directory) -> list:
        notes = []
        for filename in os.listdir(directory):
            if filename.endswith('.md'):
                with open(os.path.join(directory, filename), 'r') as file:
                    title = os.path.splitext(filename)[0]
                    content = markdown.markdown(file.read())
                    notes.append(Note(title, content))
        return notes
    
    def get_notes(self) -> list:
        return self.notes
            
