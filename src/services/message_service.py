from typing import Any, Callable, Type

class MessageService:
    def __init__(self) -> None:
        self.subscriptions = {}

    def subscribe(self, subscriber_instance: Any, publisher_type: Type, callback: Callable[..., None]) -> None:
        if publisher_type == type(subscriber_instance):
            raise ValueError(f'{subscriber_instance} cannot subscribe to its own messages.')
        if publisher_type not in self.subscriptions:
            # print(f"subscribe to:{publisher_type}")
            self.subscriptions[publisher_type] = []
        self.subscriptions[publisher_type].append((subscriber_instance, callback))

    def unsubscribe(self, subscriber_instance: Any) -> None:
        for publisher_type in self.subscriptions:
            self.subscriptions[publisher_type] = [(instance, callback) for instance, callback 
                                                in self.subscriptions[publisher_type] if instance != subscriber_instance]

    def send(self, sender: Any, message_title: str, *args: Any) -> None:
        # print(f"sender:{sender}")
        if type(sender) in self.subscriptions:
            for _, callback in self.subscriptions[type(sender)]:
                callback(message_title, *args)
