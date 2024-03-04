import json



class UserPreference():
    def __init__(self):
        self.start_up_index = 0
        self.custom_quiz_setting_expand = False
        self.show_notification = True

    def to_json(self) -> str:
        return json.dumps(self.__dict__)
    
    @classmethod
    def from_json(cls, json_string):
        preference_data = json.loads(json_string)
        preference = cls()
        preference.__dict__.update(preference_data)
        return preference