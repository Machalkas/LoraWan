import queue
import time
from threading import Thread
import config
from dataClass import CounterData
from vegaClient import Vega
from clickhouse_driver import Client
from clickHouseClient import ClickHouseWriter

from config import CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_USER, CLICKHOUSE_DB_NAME


if __name__ == "__main__":
    vega_queue = queue.Queue()
    log_queue = queue.Queue()
    ws, logger = None, None
    clickhouse_client = Client(host=CLICKHOUSE_HOST,
                           port=CLICKHOUSE_PORT,
                           user=CLICKHOUSE_USER)
    clickhouse_client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DB_NAME}")

    power_writer = ClickHouseWriter(clickhouse_client, f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.power (`datetime` DateTime, `counter` UInt32, `phase_a` Float64, `phase_b` Float64, `phase_c` Float64, `total` Float64) ENGINE = MergeTree() PARTITION BY toYYYYMMDD(datetime) PRIMARY KEY(datetime)")
    traffic_writer = ClickHouseWriter(clickhouse_client, f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.traffic (`datetime` DateTime, `counter` UInt32, `traffic_plan_1` Float64, `traffic_plan_2` Float64, `traffic_plan_3` Float64, `traffic_plan_4` Float64, `total` Float64) ENGINE = MergeTree() PARTITION BY toYYYYMMDD(datetime) PRIMARY KEY(datetime)")
    history_writer = ClickHouseWriter(clickhouse_client, f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.history (`datetime` DateTime, `tags` String, `fields` String) ENGINE=StripeLog()", timeout_sec=30, min_inserts_count=10, max_inserts_count=500)
    while True:
        if ws is None:
            print("📡🟢Start vega")
            ws = Thread(target=Vega,
                        args=(config.VEGA_URL,
                              config.VEGA_LOGIN,
                              config.VEGA_PASS,
                              config.DELAY,
                              config.DEV_UPDATE_DELAY,
                              vega_queue,
                              log_queue),
                        daemon=True,
                        name="VegaThread")
            ws.start()
        if not ws.is_alive():
            print("📡🔴Stop vega")
            ws = None
            time.sleep(5)
        
        if not vega_queue.empty():
            counters_data: CounterData = vega_queue.get()
            for counter_data in counters_data.get():
                if counter_data.get("measurement") == "power":
                    values = {
                        "datetime": counter_data.get("time"),
                        "counter": counter_data.get("tags").get("counter"),
                        "total": counter_data.get("tags").get("total"),
                        "phase_a": counter_data.get("tags").get("phase_a"),
                        "phase_b": counter_data.get("tags").get("phase_b"),
                        "phase_c": counter_data.get("tags").get("phase_c")
                    }
                    power_writer.add_values(values)
                if counter_data.get("measurement") == "traffic":
                    values = {
                        "datetime": counter_data.get("time"),
                        "counter": counter_data.get("tags").get("counter"),
                        "total": counter_data.get("tags").get("total"),
                        "traffic_plan_1": counter_data.get("tags").get("traffic_plan_1"),
                        "traffic_plan_2": counter_data.get("tags").get("traffic_plan_2"),
                        "traffic_plan_3": counter_data.get("tags").get("traffic_plan_3"),
                        "traffic_plan_4": counter_data.get("tags").get("traffic_plan_4")
                    }
                    traffic_writer.add_values(values)

                history_writer.add_values({
                    "tags": str(counters_data.action),
                    "fields": str(counters_data)
                })


                

