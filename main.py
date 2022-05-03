import queue
import time
from threading import Thread
import config as c
from influxClient import Influx
from vegaClient import Vega


if __name__ == "__main__":
    que = queue.Queue()
    log_queue = queue.Queue()
    db, ws, logger = None, None, None
    while True:
        if db is None:
            print("💾🟢Start db")
            db = Thread(target=Influx,
                        args=(c.DB_NAME, c.DB_HOST, c.DB_PORT, que, log_queue),
                        daemon=True,
                        name="InfluxThread")
            db.start()
        if ws is None:
            print("📡🟢Start vega")
            ws = Thread(target=Vega,
                        args=(c.VEGA_URL,
                              c.VEGA_LOGIN,
                              c.VEGA_PASS,
                              c.DELAY,
                              c.DEV_UPDATE_DELAY,
                              que,
                              log_queue),
                        daemon=True,
                        name="VegaThread")
            ws.start()
        if not db.is_alive():
            print("💾🔴Stop db")
            db = None
            time.sleep(5)
        if not ws.is_alive():
            print("📡🔴Stop vega")
            ws = None
            time.sleep(5)
