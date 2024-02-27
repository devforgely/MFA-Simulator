from typing import Any
from configuration.app_configuration import Settings
from models.system import *
from models.user import *
from models.note import Note
import json
import os
import markdown
import random
    


class DataService():
    def __init__(self, message_service) -> None:
        self.message_service = message_service
        self.file_path = Settings.SYSTEM_FILE_PATH
        self.signal_update = False

        if not os.path.exists(self.file_path):
            # if not exist initalise the data file
            self.reset_data()
        else:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.user = User.from_json(json.dumps(data["user"]))
                self.system = System.from_json(json.dumps(data["system"]))

        self.notes = self.read_notes_titles()
        self.cached_quiz_bank = []
        self.cached_security_questions = []
        self.cached_facts = []

    def save_data(self) -> None:
        if self.signal_update:
            with open(self.file_path, 'w') as f:
                json.dump({"user": json.loads(self.user.to_json()), "system": json.loads(self.system.to_json())}, f)
            self.signal_update = False
    
    def reset_data(self) -> None:
        self.user = User()
        self.system = System()
        data = {"user": json.loads(self.user.to_json()), "system": json.loads(self.system.to_json())}
        with open(self.file_path, 'w') as f:
            json.dump(data, f)
        self.notes = self.read_notes_titles()
        self.signal_update = False
        self.message_service.send(self, "Reboot")

    """
    =====================================================================================
    USER
    =====================================================================================
    """

    def update_user_coin(self, value: int) -> bool:
        if self.user.get_coins() + value >= 0:
            self.signal_update = True
            self.user.update_coins(value)

            #BADGE CONDITION
            if self.user.get_coins() >= 1000:
                self.update_user_badge(Badge.COIN_HUNTER)
            #BADGE END

            self.message_service.send(self, "Update Coins", self.user.get_coins(), value > 0)
            return True
        else:
            self.message_service.send(self, "Insufficient Coins", value*-1 - self.user.get_coins())
            return False

    def update_user_quiz(self, correct: int) -> None:
        self.signal_update = True
        self.user.complete_quiz()
        self.user.add_activity("Quiz Completion", "Great job on completing the quiz! Keep learning.")
        self.update_user_coin(correct*20)
        self.message_service.send(self, "Update Quiz", self.user.get_quiz_completed())

    def update_user_simulation(self) -> None:
        self.signal_update = True
        self.user.play_simulation()
        self.user.add_activity("Simulation Completion", "Well done! You've mastered a simulation. Keep growing.")
        self.update_user_coin(100)
        self.message_service.send(self, "Update Simulation", self.user.get_simulation_played())

    def update_user_badge(self, badge: Badge) -> None:
        if self.user.add_badge(badge):
            self.signal_update = True
            count = 1
            #BADGE CONDITION
            current, total = self.user.get_badges_count()
            if current == total-1:
                if self.user.add_badge(Badge.SECURITY_SAVY): count += 1
            #BADGE END
            self.message_service.send(self, "Update Badges", self.user.get_badges_count(), count)

    def update_user_improvement(self, improvements: list[tuple]) -> None:
        self.signal_update = True
        self.user.update_improvements(improvements)
        self.message_service.send(self, "Update Improvements", None)

    def update_user_reading(self, state: bool, title: str, i: int) -> None:
        self.signal_update = True
        self.user.update_reading(state, title, i)

        #BADGE CONDITION
        readings = self.user.get_readings()
        count = 0
        for _, state in readings:
            if state:
                count += 1
        if count / len(readings) >= 0.7:
            self.update_user_badge(Badge.SECURITY_SCHOLAR)
        #BADGE END
            
    def unlock_user_simulation(self, method_val: int) -> None:
        self.signal_update = True
        self.user.unlock_simulations(method_val)

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
    
    def get_user_badges_count(self) -> tuple:
        return self.user.get_badges_count()

    def get_user_improvements(self) -> list:
        return self.user.get_improvements()
    
    def get_user_readings(self) -> list:
        return self.user.get_readings()
    
    def get_user_unlocked_simulations(self) -> dict:
        return self.user.get_unlocked_simulations()
    
    """
    =====================================================================================
    SYSTEM
    =====================================================================================
    """

    def get_system_start_up(self) -> int:
        return self.system.get_start_up()
    
    def change_system_start_up(self, index) -> None:
        self.signal_update = True
        self.system.set_start_up(index)

    def get_custom_quiz_expand(self) -> bool:
        return self.system.get_custom_quiz_expand()
    
    def change_custom_quiz_expand(self, state) -> None:
        self.signal_update = True
        self.system.set_custom_quiz_expand(state)
        self.message_service.send(self, "Update Custom Quiz", state)

    def get_fun_fact(self) -> str:
        if not self.cached_facts:
            try:
                with open('data/facts.json', 'r') as file:
                    self.cached_facts = json.load(file)["facts"]
            except FileNotFoundError:
                print("File is not found")
                return "Where are all the MFA facts :("
        return random.choice(self.cached_facts)
    
    def is_system_show_notification(self) -> bool:
        return self.system.is_show_notification()
    
    def set_system_show_notification(self, state) -> None:
        self.signal_update = True
        self.system.set_show_notification(state)
        self.message_service.send(self, "Update Notification", state)

    """
    =====================================================================================
    SIMULATION SECTION
    =====================================================================================
    """
    def get_simulation_details(self, name: str) -> dict:
        try:
            with open(f'data/authentication_details/{name}.json', 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            print("File is not found")
            return {}

    def get_security_questions(self) -> list:
        if not self.cached_security_questions:
            try:
                with open('data/security_questions.json', 'r') as file:
                    self.cached_security_questions = json.load(file)["security_questions"]
            except FileNotFoundError:
                print("File is not found")
                return []
        
        # Select 9 random questions
        return random.sample(self.cached_security_questions, 9)

    """
    =====================================================================================
    LEARN SECTION
    =====================================================================================
    """

    def read_notes_titles(self) -> list:
        notes = []
        for filename in os.listdir(Settings.NOTE_FILE_PATH):
            if filename.endswith('.md'):
                title = os.path.splitext(filename)[0].replace("_", " ")
                if not title.isupper():
                    title = title.capitalize()
                notes.append(Note(title, None))

        if len(notes) > len(self.get_user_readings()):
            readings = []
            for note in notes:
                readings.append((note.title, False))
            self.user.update_readings(readings)

        return notes
    
    def read_note(self, index) -> Note:
        if self.notes[index].content == None:
            with open(os.path.join(Settings.NOTE_FILE_PATH, os.listdir(Settings.NOTE_FILE_PATH)[index]), 'r') as file:
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
            
