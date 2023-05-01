from typing import Dict
from queue import Queue

from clients.mqtt_client import MqttClient


class Globals:
    def __init__(self):
        self.mqtt_client: MqttClient = None
        self.mqtt_handler = None
        self.vega_outbox_queue: Queue = None


globals = Globals()
