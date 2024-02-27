from enum import Enum
from models.authentication.authentication import Method
from datetime import datetime
import json


class Badge(Enum):
    ONE_FA = [0, "b5.png"]
    TWO_FA = [1, "b6.png"]
    MFA = [2, "b7.png"]
    LEARNER = [3, "b9.png"]
    SECURITY_SAVY = [4, "b1.png"]
    QUIZ_WHIZ = [5, "b2.png"]
    SECURITY_SCHOLAR = [6, "b3.png"]
    COIN_HUNTER = [7, "b10.png"]


class User:
    def __init__(self):
        self.coins = 100
        self.quiz_completed = 0
        self.simulation_played = 0
        self.recent_activities = []
        self.badges = []
        self.improvements = []
        self.readings = []
        self.unlocked_simulations = {
            Method.PASSWORD.value: True,
            Method.SECRET_QUESTION.value: False,
            Method.PICTURE_PASSWORD.value: False,
            Method.FINGERPRINT.value: False,
            Method.CHIP_PIN.value: False,
            Method.TOTP.value: False,
            Method.TWOFA_KEY.value: False
        }

    def get_coins(self) -> int:
        return self.coins

    def get_quiz_completed(self) -> int:
        return self.quiz_completed
    
    def get_simulation_played(self) -> int:
        return self.simulation_played
    
    def get_badges(self) -> list:
        return self.badges
    
    def get_badges_count(self) -> tuple:
        return (len(self.badges), 8)
    
    def get_recent_activities(self) -> list:
        return self.recent_activities
    
    def get_improvements(self) -> list:
        return self.improvements
    
    def get_readings(self) -> list:
        return self.readings
    
    def get_unlocked_simulations(self) -> dict:
        return self.unlocked_simulations

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

    def add_badge(self, badge: Badge) -> bool:
        if badge.value not in self.badges:
            self.badges.append(badge.value)
            return True
        return False

    def update_improvements(self, improvements: list[tuple]) -> None:
        for category, difference in improvements:
            found = False
            for i in range(len(self.improvements)-1, -1, -1):
                if self.improvements[i][0] == category:
                    changed_val = self.improvements[i][1]+difference
                    if changed_val < 0:
                        self.improvements[i] = (category, changed_val)
                    else:
                        del self.improvements[i]
                    found = True
                    break
            if not found and difference < 0:
                self.improvements.append((category, difference))

    def update_readings(self, readings: list[tuple]) -> None:
        self.readings = readings

    def update_reading(self, state, title, i) -> None:
        self.readings[i] = (title, state)

    def unlock_simulations(self, method_val: int) -> None:
        self.unlocked_simulations[method_val] = True
    
    def to_json(self) -> str:
        return json.dumps(self.__dict__)
    
    @classmethod
    def from_json(cls, json_string):
        def convert_keys_to_int(x):
            if isinstance(x, dict):
                return {int(k): v for k, v in x.items()}
            return x

        user_data = json.loads(json_string)
        user = cls()
        user.__dict__.update(user_data)
        user.unlocked_simulations = convert_keys_to_int(user.unlocked_simulations)
        return user