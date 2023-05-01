import json
from deserializers import NewDeviceDeserializer
from deserializers.exceptions import BaseDeserializerException
from utils.api import Api
from utils.globals import globals
from utils import logger

mqtt_api = Api()

class BaseMqttHandler:

    async def handle_request(self, message: dict | str, topic: str):
        if not isinstance(message, dict):
            try:
                message = json.loads(message)
            except json.decoder.JSONDecodeError:
                logger.error(f"Fail to deserialize payload: {message}")
                return
        logger.debug(f"handle {topic}")
        try:
            result = await mqtt_api.handle_request(self, message, topic)
            if result:
                await globals.mqtt_client.publish(topic+"/response", result)
        except BaseDeserializerException as ex:
            logger.error(f"Fail handle request {topic} -> {type(ex).__name__}: {ex}")
            await globals.mqtt_client.publish(topic+"/response", {"error": str(ex)})


class MqttHandler(BaseMqttHandler):

    @mqtt_api.handler("gateway/add_device", NewDeviceDeserializer)
    async def save_statistic(self, message: NewDeviceDeserializer, topic: str):
        data = message.get_dict()
        data = {
            "cmd": "manage_devices_req",
            "devices_list": [data]
        }
        globals.vega_outbox_queue.put(data)
    
    @mqtt_api.not_found_handler()
    async def not_found(self, topic: str):
        logger.warning(f"Handler for topic {topic} not found")
        return {"error": "handler not found"}
