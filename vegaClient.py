import threading
import websocket, queue, json
from dataClass import Data
from time import sleep
from threading import Thread

class Vega:
    def __init__(self, url:str, login:str, password:str, delay:int, queue:queue) -> None:
        self.queue=queue
        self.login=login
        self.password=password
        self.delay=delay
        self.dev=[]
        self.ws = websocket.WebSocketApp(url,
                                        on_open=self.on_open,
                                        on_message=self.on_message,
                                        on_error=self.on_error,
                                        on_close=self.on_close)
        self.ws.run_forever()
    def on_open(self, ws):
        def run():
            ws.send(json.dumps({'cmd':'auth_req', 'login':self.login, 'password':self.password}))
            ws.send(json.dumps({'cmd':'get_devices_req'}))#return list of dev
            # ws.send(json.dumps({'cmd': 'get_data_req','devEui':self.dev[1],'select':{'direction':'UPLINK'}}))
            t=threading.current_thread()
            while getattr(t, "stop", False):
                for i in self.dev:
                    ws.send(json.dumps({'cmd': 'get_data_req','devEui':i["id"],'select':{'direction':'UPLINK'}}))
                sleep(self.delay)
        self.thread=Thread(target=run, daemon=True, name="WsWriterThread").start()

    def on_message(self, ws, message):
        dt = Data(message)
        if dt.action!=dt.N:
            if dt.action==dt.GET_DEV:
                self.dev=dt.devs
            self.queue.put(dt)
        print(dt,"\n")

    def on_error(self, ws, error):
        print("ws error:",error)

    def on_close(self, ws, close_status_code, close_msg):
        self.thread.stop=True
        self.thread.join()