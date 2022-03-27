import config as c
from threading import Thread
import queue,time
from influxClient import Influx
from vegaClient import Vega

if __name__=="__main__":
    queue=queue.Queue()
    db, ws=None, None
    while True:
        if db==None:
            print("💾🟢Start db")
            db = Thread(target=Influx, args=(c.DB_NAME, c.DB_HOST, c.DB_PORT, queue), daemon=True,  name="InfluxThread")
            db.start()      
        if ws==None:
            print("📡🟢Start vega")
            ws = Thread(target=Vega, args=(c.VEGA_URL, c.VEGA_LOGIN, c.VEGA_PASS, c.DELAY, c.DEV_UPDATE_DELAY, queue), daemon=True, name="VegaThread")
            ws.start()
        if not db.is_alive():
            print("💾🔴Stop db") 
            db=None
            time.sleep(5)
        if not ws.is_alive():
            print("📡🔴Stop vega")
            ws=None
            time.sleep(5)
            
         

