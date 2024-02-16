from typing import Any
from configuration.app_settings import Settings
from models.authentication.authentication import Method
import json
import os
import markdown
import random
from datetime import datetime
from enum import Enum

class Note:
    def __init__(self, title, content):
        self.title = title
        self.content = content

class Badge(Enum):
    BEGINNER = (-3, "b8.png")
    NO_ADVANCED = (-2, "b0.png")
    NO_FA = (-1, "b4.png")
    ONE_FA = (0, "b5.png")
    TWO_FA = (1, "b6.png")
    MFA = (2, "b7.png")
    LEARNER = (3, "b9.png")
    SECURITY_SAVY = (4, "b1.png")
    QUIZ_WHIZ = (5, "b2.png")
    SECURITY_SCHOLAR = (6, "b3.png")
    COIN_HUNTER = (7, "b10.png")

class User:
    def __init__(self):
        self.coins = 100
        self.quiz_completed = 0
        self.simulation_played = 0
        self.recent_activities = []
        self.badges = []
        self.improvements = []
        self.readings = []

    def get_coins(self) -> int:
        return self.coins

    def get_quiz_completed(self) -> int:
        return self.quiz_completed
    
    def get_simulation_played(self) -> int:
        return self.simulation_played
    
    def get_badges(self) -> list:
        return self.badges
    
    def get_recent_activities(self) -> list:
        return self.recent_activities
    
    def get_improvements(self) -> list:
        return self.improvements

    def update_coins(self, amount) -> None:
        self.coins += amount

    def complete_quiz(self) -> None:
        self.quiz_completed += 1

    def play_simulation(self) -> None:
        self.simulation_played += 1

    def add_activity(self, activity_title, description) -> None:
        formatted_date = datetime.now().strftime("%A, %b %d, %Y, %I:%M %p")
        if len(self.recent_activities) == 3:
            self.recent_activities.pop(0)
        self.recent_activities.append((activity_title, formatted_date, description))

    def add_badge(self, badge: Badge) -> None:
        if badge.value not in self.badges:
            self.badges.append(badge.value)

    def add_improvement(self, improvement) -> None:
        self.improvements.append(improvement)

    def add_reading(self, reading) -> None:
        self.readings.append(reading)
    
    def to_json(self) -> str:
        return json.dumps(self.__dict__)
    
    @classmethod
    def from_json(cls, json_string):
        user_data = json.loads(json_string)
        user = cls()
        user.__dict__.update(user_data)
        return user

class DataService():
    def __init__(self, message_service) -> None:
        self.message_service = message_service
        self.file_path = Settings.SYSTEM_FILE_PATH

        if not os.path.exists(self.file_path):
            # if not exist initalise the data file
            self.reset_data()
        else:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.user = User.from_json(json.dumps(data["user"]))

        self.notes_directory = 'data/notes'
        self.notes = self.read_notes_titles()
        self.cached_quiz_bank = []

    def save_data(self) -> None:
        print("saving data...")
        with open(self.file_path, 'w') as f:
            json.dump({"user": json.loads(self.user.to_json())}, f)
    
    def reset_data(self) -> None:
        self.user = User()
        data = {"user": json.loads(self.user.to_json())}
        with open(self.file_path, 'w') as f:
            json.dump(data, f)
        self.message_service.send(self, "Update coins", self.user.coins)
        self.message_service.send(self, "Update quiz", self.user.quiz_completed)
        self.message_service.send(self, "Update simulation", self.user.simulation_played)
        self.message_service.send(self, "Update badges", self.user.simulation_played)

    """
    =====================================================================================
    USER
    =====================================================================================
    """

    def update_user_coin(self, value: int) -> None:
        self.user.update_coins(value)
        self.message_service.send(self, "Update coins", self.user.coins)

    def update_user_quiz(self) -> None:
        self.user.complete_quiz()
        self.user.add_activity("Quiz Completion", "Great job on completing the quiz! Keep learning.")
        self.update_user_coin(100)
        self.message_service.send(self, "Update quiz", self.user.quiz_completed)

    def update_user_simulation(self) -> None:
        self.user.play_simulation()
        self.user.add_activity("Simulation Completion", "Well done! You've mastered a simulation. Keep growing.")
        self.update_user_coin(100)
        self.message_service.send(self, "Update simulation", self.user.simulation_played)

    def update_user_badge(self, badge: Badge) -> None:
        self.user.add_badge(badge)
        self.message_service.send(self, "Update badges", self.user.simulation_played)

    def get_user_coins(self) -> int:
        return self.user.get_coins()

    def get_user_simulation_played(self) -> int:
        return self.user.get_simulation_played()
    
    def get_user_quiz_completed(self) -> int:
        return self.user.get_quiz_completed()
    
    def get_user_recent_activiies(self) -> list:
        return self.user.get_recent_activities()[::-1]
    
    def get_user_badges(self) -> list:
        return self.user.get_badges()

    def get_user_improvements(self) -> list:
        return self.user.get_improvements()
    """
    =====================================================================================
    SIMULATION SECTION
    =====================================================================================
    """


    def get_security_questions(self) -> list:
        try:
            with open('data/security_questions.json', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            print("File is not found")
            return []
        
        # Select 9 random questions
        return random.sample(data['securityQuestions'], 9)

    """
    =====================================================================================
    LEARN SECTION
    =====================================================================================
    """

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
    

    """
    =====================================================================================
    QUIZ SECTION
    =====================================================================================
    """

    def get_quiz_bank(self) -> list:
        if not self.cached_quiz_bank:
            with open('data/quizzes/quiz_bank1.json', 'r') as f:
                self.cached_quiz_bank = json.load(f)
        return self.cached_quiz_bank
            
