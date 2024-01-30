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

        self.notes_directory = 'data/notes'
        self.notes = self.read_notes_titles()

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


    def read_notes_titles(self) -> list:
        notes = []
        for filename in os.listdir(self.notes_directory):
            if filename.endswith('.md'):
                notes.append(Note(os.path.splitext(filename)[0].replace("_", " ").capitalize(), None))  
        return notes
    
    def read_note(self, index) -> Note:
        if self.notes[index].content == None:
            with open(os.path.join(self.notes_directory, os.listdir(self.notes_directory)[index]), 'r') as file:
                self.notes[index].content = markdown.markdown(file.read())
        return self.notes[index]
    
    def get_notes(self) -> list:
        return self.notes
    

    def get_quiz_bank(self) -> list:
        with open('data/quizzes/quiz_bank1.json', 'r') as f:
            return json.load(f)
            
