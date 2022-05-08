import queue
import threading
from influxdb import InfluxDBClient

from dataClass import CounterData


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
                    raw_data = self.queue.get()
                    data = raw_data.get()
                    if data != []:
                        print(f"💾👉📜 Write points ({len(data)})")
                        self.influx_client.write_points(data)
                    
                    self.write_history(raw_data)
                except ZeroDivisionError as ex:
                    print("❗💾 DB Error:", ex)

    def write_history(self, counter_data: CounterData):
        decoded_history_data = counter_data.get()
        history_data = {
            "measurement": "history",
            "tags": {"action": str(counter_data.action)},
            "fields": {"raw_data": str(counter_data)}
        }
        if decoded_history_data != []:
            counter_serial_number = decoded_history_data[0]["tags"]["counter"]
            history_data["tags"]["counter"] = counter_serial_number
            history_data["fields"]["decoded_data"] = f"{decoded_history_data}"
        self.influx_client.write_points([history_data])

if __name__ == "__main__":
    from config import DB_HOST, DB_PORT
    import queue
    i = Influx("vega", DB_HOST, DB_PORT, queue.Queue())
