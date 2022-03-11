import influxdb_client, queue, threading
from influxdb_client.client.write_api import SYNCHRONOUS

class Influx:
    def __init__(self, db_name:str, db_host:str, token:str, queue:queue) -> None:
        self.queue=queue
        self.db_name=db_name
        self.client=influxdb_client.InfluxDBClient(url=db_host, token=token)
        self.write_api=self.client.write_api(write_options=SYNCHRONOUS)
        self.run()
    
    def run(self):
        t=threading.current_thread()
        while not getattr(t, "stop", False):
            if not self.queue.empty():
                # print("write to db")
                d=self.queue.get()
                print(f"//////////////////////////////////////////////////////////\n{d.message}\n//////////////////////////////////////////////////////////")
                # p=influxdb_client.Point(d.measurement).time(d.time)
                # for t in d.tags:
                #     p.tag(t[0],t[1])
                # for f in d.fields:
                #     p.field(f[0],f[1])



    