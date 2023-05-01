
import json
from typing import Union
from os.path import normpath

from deserializers import BaseDeserializer


class Api:
    def __init__(self) -> None:
        self.handlers = {}
        self.handler_not_found = None

    def handler(self, topic: str, deserializer: BaseDeserializer = None):
        assert topic not in self.handlers, f"Handler with topic \"{topic}\" already exists"
        def wrapper(handler):
            self.handlers[normpath(topic)] = {"handler": handler, "deserializer": deserializer}
            return handler
        return wrapper
    
    def not_found_handler(self):
        def wrapper(handler):
            self.handler_not_found = handler
            return handler
        return wrapper

    async def handle_request(self, handler_self, message: Union[str, dict], topic: str):
        topic = normpath(topic)
        if isinstance(message, str):
            message = json.loads(message)
        handler_dict = self.handlers.get(topic)
        if handler_dict is None:
            return None if self.handler_not_found is None else await self.handler_not_found(handler_self, topic=topic)
        deserializer = handler_dict.get("deserializer")
        handler = handler_dict.get("handler")
        if deserializer is None:
            return await handler(handler_self, topic=topic)
        return await handler(handler_self, message=deserializer(message), topic=topic)
