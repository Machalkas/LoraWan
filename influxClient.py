from operator import imod
import queue, threading
from influxdb import InfluxDBClient

class Influx:
    def __init__(self, db_name:str, db_host:str, port:str, queue:queue) -> None:
        self.queue=queue
        self.db_name=db_name
        self.client=InfluxDBClient(host=db_host, port=port)
        self.client.create_database(db_name)
        self.client.switch_database(db_name)
        # self.client.write_points
        self.run()
    
    def run(self):
        t=threading.current_thread()
        while not getattr(t, "stop", False):
            if not self.queue.empty():
                d=self.queue.get()
                print("write to db",d.get())
                # print(f"//////////////////////////////////////////////////////////\n{d.message}\n//////////////////////////////////////////////////////////")
                # p=influxdb_client.Point(d.measurement).time(d.time)
                # for t in d.tags:
                #     p.tag(t[0],t[1])
                # for f in d.fields:
                #     p.field(f[0],f[1])

if __name__=="__main__":
    from config import DB_HOST, DB_PORT
    import queue
    i=Influx("vega", DB_HOST, DB_PORT, queue.Queue())

    