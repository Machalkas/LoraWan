from abc import abstractmethod
from enum import Enum
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
        for key, value in raw_dict.items():
            if isinstance(value, BaseDeserializer):
                raw_dict[key] = value.get_dict()
        if not isinstance(ignore_key, list):
            return raw_dict
        for key in ignore_key:
            raw_dict.pop(key)
        return raw_dict


class Class(Enum):
    CLASS_A = "CLASS_A"
    CLASS_C = "CLASS_C"


class ABP(BaseDeserializer):
    @catch_key_error
    def deserialize(self, message: dict):
        self.devAddress: int = int(message["dev_address"])
        self.appsKey: str = message["apps_key"]
        self.nwksKey: str = message["nwks_key"]


class NewDeviceDeserializer(BaseDeserializer):
    @catch_key_error
    def deserialize(self, message: dict):
        self.deviceEui: str = message["device_eui"]
        self.Class: str = Class(message["class"]).value
        self.deviceName: str = message.get("device_name")
        # self.ABP: ABP = ABP(message["abp"])


if __name__ == "__main__":
    x = NewDeviceDeserializer('{"device_eui":"70B3D58FF101475A", "class": "CLASS_C", "device_name": "test", "abp": {"dev_address": 1, "apps_key": "02222222222222222222222222222222", "nwks_key": "1234"}}')
    print(x.get_dict())
# class NewDevicesListDeserializer(BaseDeserializer):
#     @catch_key_error
#     def deserialize(self, message: dict):
#         self.energy_meters: list[NewDeviceDeserializer] = [NewDeviceDeserializer(dev) for dev in message]