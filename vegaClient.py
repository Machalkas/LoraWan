import threading
import websocket
import queue
import json
from dataClass import CounterData
from time import sleep, time
from threading import Thread
from config import CONSOLE_LOG


class Vega:
    def __init__(self, url: str, login: str, password: str, delay: int,
                 dev_delay: int, queue: queue, log_queue: queue) -> None:
        self.queue = queue
        self.log_queue = log_queue
        self.login = login
        self.password = password
        self.delay = delay
        self.dev_delay = dev_delay
        self.devices = []
        self.ws = websocket.WebSocketApp(url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws.run_forever()

    def on_open(self, ws):
        def run():
            try:
                timer = 0
                print("📡👉🔑 auth request")
                ws.send(json.dumps({
                     'cmd': 'auth_req',
                     'login': self.login,
                     'password': self.password}))
                vega_thread = threading.current_thread()
                while not getattr(vega_thread, "stop", False):
                    if self.devices != []:
                        sleep(self.delay)
                        print("📡👉📜 request data")
                    if time()-timer >= self.dev_delay:
                        print("📡👉🔄 update device list")
                        # return list of dev
                        ws.send(json.dumps({'cmd': 'get_devices_req'}))
                        timer = time()
            except Exception as ex:
                print("📡❗ Vega error:", ex)
        self.thread = Thread(target=run, daemon=True, name="WsWriterThread").start()

    def get_saved_data_from_devices(self):
        for device in self.devices:
            self.ws.send(json.dumps({'cmd': 'get_data_req',
                                     'devEui': device["id"],
                                     'select': {'direction': 'UPLINK'}}))

    def on_message(self, ws, message):
        dt = CounterData(message)
        if dt.action != dt.N:
            if dt.action == dt.GET_DEV:
                self.devices = dt.devices
                self.get_saved_data_from_devices()
            self.queue.put(dt)
        if dt.action != dt.CONSOLE or CONSOLE_LOG:
            log_emoji = {dt.AUTH: "🔑", dt.GET_DEV: "🔄", dt.GET_DATA: "📜"}
            print(f"📡👈{log_emoji[dt.action]} | {dt.action}")  # TODO: add logger

    def on_error(self, ws, error):
        print("❗📡ws error:", error)
        # pass

    def on_close(self, ws, close_status_code, close_msg):
        self.thread.stop = True
        self.thread.join()
