import config as c
from threading import Thread
import queue
from influxClient import Influx
from vegaClient import Vega

if __name__=="__main__":
    db_queue=queue.Queue()
    ws_queue=queue.Queue()
    db = Thread(target=Influx, args=(c.DB_NAME, c.DB_HOST, db_queue), name="InfluxThread").start()
    ws = Thread(target=Vega, args=(c.VEGA_URL, c.VEGA_LOGIN, c.VEGA_PASS, c.DEVICES, ws_queue), name="VegaThread").start()
    while True:
        pass

