import queue
import threading
from influxdb import InfluxDBClient


class Influx:
    def __init__(self, db_name: str, db_host: str, port: str, queue: queue,
                 log_queue: queue) -> None:
        self.queue = queue
        self.log_queue = log_queue
        self.db_name = db_name
        try:
            self.influx_client = InfluxDBClient(host=db_host, port=port)
            print("💾👉🆕 create database", db_name)
            self.influx_client.create_database(db_name)
            print("💾👉select database", db_name)
            self.influx_client.switch_database(db_name)
        except Exception as ex:
            print("❗💾 DB Error:", ex)
        self.run()

    def run(self):
        influx_thread = threading.current_thread()
        while not getattr(influx_thread, "stop", False):
            if not self.queue.empty():
                try:
                    data = self.queue.get().get()
                    if data != []:
                        print(f"💾👉📜 Write points ({len(data)})")
                        self.influx_client.write_points(data)
                        self.influx_client.delete_series(tags=[{"counter": i["tags"]["counter"]} for i in data])
                        self.influx_client.write_points([{
                            "measurements": "devices",
                            "counter": i["tags"]["counter"]
                        } for i in data])
                except Exception as ex:
                    print("❗💾 DB Error:", ex)


if __name__ == "__main__":
    from config import DB_HOST, DB_PORT
    import queue
    i = Influx("vega", DB_HOST, DB_PORT, queue.Queue())
