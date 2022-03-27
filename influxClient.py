from operator import imod
import queue, threading
from influxdb import InfluxDBClient

class Influx:
    def __init__(self, db_name:str, db_host:str, port:str, queue:queue) -> None:
        self.queue=queue
        self.db_name=db_name
        try:
            self.client=InfluxDBClient(host=db_host, port=port)
            print("💾👉🆕 create database",db_name)
            self.client.create_database(db_name)
            print("💾👉select database",db_name)
            self.client.switch_database(db_name)
        except Exception as ex:
            print("❗💾 DB Error:",ex)
        self.run()
    
    def run(self):
        t=threading.current_thread()
        while not getattr(t, "stop", False):
            if not self.queue.empty():
                d=self.queue.get().get()
                if d!=[]:
                    print(f"💾👉📜 Write points ({len(d)})")
                    try:
                        self.client.write_points(d)
                    except Exception as ex:
                        print("❗💾 DB Error:",ex)

if __name__=="__main__":
    from config import DB_HOST, DB_PORT
    import queue
    i=Influx("vega", DB_HOST, DB_PORT, queue.Queue())

    