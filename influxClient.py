import queue
import threading
from influxdb import InfluxDBClient
import pymysql
from dataClass import CounterData

from config import INFLUX_HOST
from globals import logger


class Influx:
    def __init__(self, db_name: str, db_host: str, port: str, queue: queue,
                 log_queue: queue) -> None:
        self.queue = queue
        self.log_queue = log_queue
        self.db_name = db_name
        try:
            self.influx_client = InfluxDBClient(host=db_host, port=port)
            logger.info(f"Create influx database: {db_name}")
            self.influx_client.create_database(db_name)
            self.influx_client.switch_database(db_name)
        except Exception as ex:
            logger.error(f"DB Error: {ex}")
        self.run()

    def run(self):
        influx_thread = threading.current_thread()
        while not getattr(influx_thread, "stop", False):
            if not self.queue.empty():
                try:
                    raw_data = self.queue.get()
                    if raw_data.action is CounterData.GET_DEV:
                        logger.important("Write devices to mysql")
                        self.write_devices(raw_data)

                    data = raw_data.get()
                    if data != []:
                        logger.info(f"Write points ({len(data)})")
                        self.influx_client.write_points(data)
                    
                    self.write_history(raw_data)
                except Exception as ex:
                    logger.error(f"DB Error: {ex}")

    def write_devices(self, counter_data: CounterData) -> None:
        if counter_data.devices is None:
            return

        counters = counter_data.devices
        counters_string = ""
        for counter in counters:
            counters_string += f"('{counter.get('id')}', '{counter.get('name')}'),"
        counters_string = counters_string[:-1]
        counters_string += ";"

        mysql_connection = pymysql.connect(host=INFLUX_HOST, user='pyvega', password='qwedsa123', database='vega')
        with mysql_connection:
            db_cursor = mysql_connection.cursor()
            db_cursor.execute("TRUNCATE TABLE counters")
            db_cursor.execute(f"insert into counters (dev_id, dev_name) values {counters_string}")
            mysql_connection.commit()

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
    from config import DB_HOST, INFLUX_PORT
    import queue
    i = Influx("vega", INFLUX_HOST, INFLUX_PORT, queue.Queue())
