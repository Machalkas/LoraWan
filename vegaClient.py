import websocket, queue, json
from dataClass import Data
from time import sleep
from threading import Thread

class Vega:
    def __init__(self, url:str, login:str, password:str, devices:list, queue:queue, delay:int=5) -> None:
        self.queue=queue
        self.login=login
        self.password=password
        self.dev=devices
        self.delay=delay
        self.ws = websocket.WebSocketApp(url,
                                        on_open=self.on_open,
                                        on_message=self.on_message,
                                        on_error=self.on_error,
                                        on_close=self.on_close)
        self.ws.run_forever()
    
    def on_open(self, ws):
        def run():
            ws.send(json.dumps({'cmd':'auth_req', 'login':self.login, 'password':self.password}))
            while True:
                for i in self.dev:
                    ws.send(json.dumps({'cmd':'get_devices_req'}))
                    ws.send(json.dumps({'cmd': 'get_data_req','devEui':i,'select':{'direction':'UPLINK'}}))
                sleep(self.delay)
        Thread(target=run).start()

    def on_message(self, ws, message):
        self.queue.put(Data(message))

    def on_error(self, ws, error):
        pass

    def on_close(self, ws, close_status_code, close_msg):
        pass