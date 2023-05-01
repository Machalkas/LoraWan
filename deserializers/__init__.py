from abc import ABC, abstractmethod
from datetime import datetime
import json
from typing import Union
from config import DT_FORMAT
from deserializers.exceptions import DeserializerKeyError, DeserializerValueError, ShittyError


def catch_key_error(func):
    def wrapper(self, *args, **kargs):
        try:
            return func(self, *args, **kargs)
        except KeyError as ex:
            raise DeserializerKeyError(ex)
        except ValueError as ex:
            raise DeserializerValueError(ex)
        except Exception as ex:
            raise ShittyError(ex)
            
    return wrapper


class BaseDeserializer:
    def __init__(self, message: Union[str, dict]) -> None:
        if isinstance(message, str):
            message = json.loads(message)
        self.deserialize(message)

    @abstractmethod
    def deserialize(self, message: dict):
        pass

    def get_dict(self, ignore_key: list = None) -> dict:
        raw_dict = self.__dict__
        if not isinstance(ignore_key, list):
            return raw_dict
        for key in ignore_key:
            raw_dict.pop(key)
        return raw_dict


class NewDeviceDeserializer(BaseDeserializer):
    @catch_key_error
    def deserialize(self, message: dict):
        self.device_eui: str = message["device_eui"]
        self.device_name: str = message.get("device_name")



# class NewDevicesListDeserializer(BaseDeserializer):
#     @catch_key_error
#     def deserialize(self, message: dict):
#         self.energy_meters: list[NewDeviceDeserializer] = [NewDeviceDeserializer(dev) for dev in message]