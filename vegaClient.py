import threading
import websocket, queue, json
from dataClass import Data
from time import sleep, time
from threading import Thread
from config import CONSOLE_LOG

class Vega:
    def __init__(self, url:str, login:str, password:str, delay:int, dev_delay:int, queue:queue) -> None:
        self.queue=queue
        self.login=login
        self.password=password
        self.delay=delay
        self.dev_delay=dev_delay
        self.dev=[]
        self.ws = websocket.WebSocketApp(url,
                                        on_open=self.on_open,
                                        on_message=self.on_message,
                                        on_error=self.on_error,
                                        on_close=self.on_close)
        self.ws.run_forever()
    def on_open(self, ws):
        def run():
            timer=0
            print("📡👉🔑 auth request")
            ws.send(json.dumps({'cmd':'auth_req', 'login':self.login, 'password':self.password}))
            t=threading.current_thread()
            while not getattr(t, "stop", False):
                if self.dev!=[]:
                    sleep(self.delay)
                    print("📡👉📜 request data")
                for i in self.dev:
                    # print("sending to ",i["id"])
                    ws.send(json.dumps({'cmd': 'get_data_req','devEui':i["id"],'select':{'direction':'UPLINK', 'limit':1}}))
                if time()-timer>=self.dev_delay:
                    print("📡👉🔄 update dev list")
                    ws.send(json.dumps({'cmd':'get_devices_req'}))#return list of dev
                    timer=time()                    
        self.thread=Thread(target=run, daemon=True, name="WsWriterThread").start()

    def on_message(self, ws, message):
        dt = Data(message)
        if dt.action!=dt.N:
            if dt.action==dt.GET_DEV:
                self.dev=dt.devs
            self.queue.put(dt)
        if dt.action!=dt.CONSOLE or CONSOLE_LOG:
            log_emogy={dt.AUTH:"🔑", dt.GET_DEV:"🔄", dt.GET_DATA:"📜"}
            print(f"📡👈{log_emogy[dt.action]}\n", dt,"\n")#TODO: add logger
            

    def on_error(self, ws, error):
        print("❗📡ws error:",error)
        # pass

    def on_close(self, ws, close_status_code, close_msg):
        self.thread.stop=True
        self.thread.join()