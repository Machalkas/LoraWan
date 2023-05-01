import threading
import websocket
import queue
import json
from utils.dataClass import CounterData
from time import sleep, time
from threading import Thread
# from config import CONSOLE_LOG
from utils import logger


class Vega:
    def __init__(self, url: str, login: str, password: str, delay: int,
                 dev_delay: int, inbox_queue: queue.Queue, outbox_queue: queue.Queue) -> None:
        self.inbox_queue = inbox_queue
        self.outbox_queue = outbox_queue
        self.login = login
        self.password = password
        self.delay = delay
        self.dev_delay = dev_delay
        self.devices = []
        self.block_get_data = False  # just for test
        self.ws = websocket.WebSocketApp(url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever()

    def queue_listener(self, ws):
        vega_thread = threading.current_thread()
        while not getattr(vega_thread, "stop", False):
            if not self.outbox_queue.empty():
                send_message = self.outbox_queue.get()
                if isinstance(send_message, dict):
                    send_message = json.dumps(send_message)
                if isinstance(send_message, str):
                    logger.debug(f"send message to vega: {send_message}")
                    try:
                        ws.send(send_message)
                    except Exception as ex:
                        print(ex)
            sleep(.2)


    def on_open(self, ws):
        def run():
            try:
                timer = 0
                logger.info("auth request")
                ws.send(json.dumps({
                     'cmd': 'auth_req',
                     'login': self.login,
                     'password': self.password}))
                vega_thread = threading.current_thread()
                while not getattr(vega_thread, "stop", False):
                    if self.devices != []:
                        self.get_saved_data_from_devices()
                        logger.info("request saved data from")
                        sleep(self.delay)
                    if time()-timer >= self.dev_delay:
                        logger.info("request device list")
                        ws.send(json.dumps({'cmd': 'get_devices_req'}))
                        timer = time()
            except Exception as ex:
                logger.error(f"Vega error: {ex}")
        self.thread = Thread(target=run, daemon=True, name="WsWriterThread").start()
        self.queue_thread = Thread(target=self.queue_listener, args=(ws,), daemon=True, name="WsQueueThread").start()

    def get_saved_data_from_devices(self):
        # if self.block_get_data:
        #     return
        for device in self.devices:
            self.ws.send(json.dumps({'cmd': 'get_data_req',
                                     'devEui': device["device_eui"],
                                     'select': {'direction': 'UPLINK', 'date_from': f"{int((time()-self.delay*2)*1000)}"}}))
        logger.info("send get_data_req")
        self.block_get_data = True

    def on_message(self, ws, message):
        logger.debug(message)
        dt = CounterData(message)
        if dt.action != dt.N:
            if dt.action == dt.GET_DEVICES:
                self.devices = dt.devices
                # self.get_saved_data_from_devices()
            self.inbox_queue.put(dt)
        # if dt.action != dt.CONSOLE or CONSOLE_LOG:
        #     logger.info(f"{dt.action}")

    def on_error(self, ws, error):
        logger.error(f"websocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.thread.stop = True
        self.queue_thread.stop = True
        self.thread.join()
        self.queue_thread.join()
