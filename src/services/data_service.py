from configuration.app_configuration import Settings
from models.user_preference import *
from models.user import *
from models.note import *
import json
import os
import random


class DataService():
    def __init__(self, message_service) -> None:
        self.message_service = message_service
        self.user_path = Settings.USER_FILE_PATH
        self.signal_update = False

        if not os.path.exists(self.user_path):
            # if not exist initalise the data file
            self.reset_data()
        else:
            with open(self.user_path, 'r') as f:
                data = json.load(f)
                self.user = User.from_json(json.dumps(data["user"]))
                self.user_preference = UserPreference.from_json(json.dumps(data["user_preference"]))

        self.notes = self.read_notes_titles()
        self.cached_quiz_bank = []
        self.cached_security_questions = []
        self.cached_facts = []
        self.cached_details = {}
        self.cache_help_index = dict()

    def save_data(self) -> None:
        if self.signal_update:
            with open(self.user_path, 'w') as f:
                json.dump({"user": json.loads(self.user.to_json()), "user_preference": json.loads(self.user_preference.to_json())}, f)
            self.signal_update = False
    
    def reset_data(self) -> None:
        self.user = User()
        self.user_preference = UserPreference()
        data = {"user": json.loads(self.user.to_json()), "user_preference": json.loads(self.user_preference.to_json())}
        with open(self.user_path, 'w') as f:
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
        if self.user.coins + value >= 0:
            self.signal_update = True
            self.user.update_coins(value)

            #BADGE CONDITION
            if self.user.coins >= 1000:
                self.update_user_badge(Badge.COIN_HUNTER)
            #BADGE END

            self.message_service.send(self, "Update Coins", self.user.coins, value > 0)
            return True
        else:
            self.message_service.send(self, "Insufficient Coins", value*-1 - self.user.coins)
            return False

    def update_user_quiz(self, correct: int) -> None:
        self.signal_update = True
        self.user.increase_quiz_count()
        self.user.add_activity("Quiz Completion", "Great job on completing the quiz! Keep learning.")
        self.update_user_coin(correct*20)
        self.message_service.send(self, "Update Quiz", self.user.quiz_completed)

    def update_user_simulation(self) -> None:
        self.signal_update = True
        self.user.increase_simulation_count()
        self.user.add_activity("Simulation Completion", "Well done! You've mastered a simulation. Keep growing.")
        self.update_user_coin(100)
        self.message_service.send(self, "Update Simulation", self.user.simulation_played)

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

    def update_user_reading(self, title: str, state: bool, i: int) -> None:
        self.signal_update = True
        self.user.update_reading(title, state, i)

        #BADGE CONDITION
        readings = self.user.readings
        count = 0
        for _, state in readings:
            if state:
                count += 1
        if count / len(readings) >= 0.7:
            self.update_user_badge(Badge.SECURITY_SCHOLAR)
        #BADGE END
            
    def unlock_user_simulation(self, method_val: int) -> None:
        self.signal_update = True
        self.user.unlock_simulation(method_val)

    def get_user_coins(self) -> int:
        return self.user.coins

    def get_user_simulation_played(self) -> int:
        return self.user.simulation_played
    
    def get_user_quiz_completed(self) -> int:
        return self.user.quiz_completed
    
    def get_user_recent_activiies(self) -> list:
        return self.user.recent_activities[::-1]
    
    def get_user_badges(self) -> list:
        return self.user.badges
    
    def get_user_badges_count(self) -> tuple:
        return self.user.get_badges_count()

    def get_user_improvements(self) -> list:
        return self.user.improvements
    
    def get_user_readings(self) -> list:
        return self.user.readings
    
    def get_user_unlocked_simulations(self) -> dict:
        return self.user.unlocked_simulations
    
    """
    =====================================================================================
    SYSTEM
    =====================================================================================
    """

    def get_system_start_up(self) -> int:
        return self.user_preference.start_up_index
    
    def change_system_start_up(self, index: int) -> None:
        self.signal_update = True
        self.user_preference.start_up_index = index

    def get_custom_quiz_setting_expand(self) -> bool:
        return self.user_preference.custom_quiz_setting_expand
    
    def change_custom_quiz_setting_expand(self, state: bool) -> None:
        self.signal_update = True
        self.user_preference.custom_quiz_setting_expand = state
        self.message_service.send(self, "Update Custom Quiz", state)

    def get_fun_fact(self) -> str:
        if not self.cached_facts:
            try:
                with open(Settings.FACT_FILE_PATH, 'r') as file:
                    self.cached_facts = json.load(file)["facts"]
            except FileNotFoundError:
                return "Where are all the MFA facts :("
        return random.choice(self.cached_facts)
    
    def is_system_show_notification(self) -> bool:
        return self.user_preference.show_notification
    
    def set_system_show_notification(self, state: bool) -> None:
        self.signal_update = True
        self.user_preference.show_notification = state
        self.message_service.send(self, "Update Notification", state)

    """
    =====================================================================================
    SIMULATION SECTION
    =====================================================================================
    """
    def get_simulation_details(self, name: str) -> dict:
        if name in self.cached_details:
            return self.cached_details[name]
        try:
            with open(f'{Settings.SIMULATION_NOTE_PATH}{name}.json', 'r') as file:
                self.cached_details[name] = json.load(file)
                return self.cached_details[name]
        except FileNotFoundError:
            return {}

    def get_security_questions(self) -> list:
        if not self.cached_security_questions:
            try:
                with open(Settings.SECURITY_QUESTION_FILE_PATH, 'r') as file:
                    self.cached_security_questions = json.load(file)["security_questions"]
            except FileNotFoundError:
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
                    title = title.title()
                notes.append(Note(title, ""))

        if len(notes) > len(self.get_user_readings()):
            readings = []
            for note in notes:
                readings.append((note.title, False))
            self.user.readings = readings

        return notes
    
    def read_note_content(self, index: int) -> str:
        if self.notes[index].content == "":
            with open(os.path.join(Settings.NOTE_FILE_PATH, os.listdir(Settings.NOTE_FILE_PATH)[index]), 'r') as file:
                self.notes[index].content = file.read()
        return self.notes[index].content
    
    def get_notes(self) -> list:
        return self.notes
    

    """
    =====================================================================================
    QUIZ SECTION
    =====================================================================================
    """

    def get_quiz_bank(self) -> list:
        if not self.cached_quiz_bank:
            with open(Settings.QUIZ_FILE_PATH+'quiz_bank1.json', 'r') as f:
                self.cached_quiz_bank = json.load(f)
        return self.cached_quiz_bank
    
    """
    =====================================================================================
    HELP SECTION
    =====================================================================================
    """

    def get_help_token(self) -> tuple:
        if not self.cache_help_index:
            with open(Settings.HELP_TOKEN_FILE_PATH, 'r') as f:
                return (self.cache_help_index, json.load(f))
        return (self.cache_help_index, None)