import json



class System():
    def __init__(self):
        self.start_up_index = 0
        self.custom_quiz_expand = False
        self.show_notification = True

    def get_start_up(self) -> int:
        return self.start_up_index
    
    def set_start_up(self, index: int) -> None:
        self.start_up_index = index

    def get_custom_quiz_expand(self) -> bool:
        return self.custom_quiz_expand
    
    def set_custom_quiz_expand(self, state: bool) -> None:
        self.custom_quiz_expand = state

    def is_show_notification(self) -> bool:
        return self.show_notification
    
    def set_show_notification(self, state: bool) -> None:
        self.show_notification = state

    def to_json(self) -> str:
        return json.dumps(self.__dict__)
    
    @classmethod
    def from_json(cls, json_string):
        system_data = json.loads(json_string)
        system = cls()
        system.__dict__.update(system_data)
        return system