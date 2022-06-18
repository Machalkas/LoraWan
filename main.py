from datetime import datetime
import queue
import time
from threading import Thread
import config
from dataClass import CounterData
from vegaClient import Vega
from clickhouse_driver import Client
from clickHouseClient import ClickHouseWriter

from config import CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_USER, CLICKHOUSE_DB_NAME, CLICKHOUSE_PASSWORD

power_table_query = f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.power (`datetime` DateTime, `counter` UInt32, `phase_a` Nullable(Float64), `phase_b` Nullable(Float64), `phase_c` Nullable(Float64), `total` Nullable(Float64)) ENGINE = MergeTree() PARTITION BY toMonday(datetime) PRIMARY KEY(datetime)"
traffic_table_query =  f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.traffic (`datetime` DateTime, `counter` UInt32, `traffic_plan_1` Nullable(Float64), `traffic_plan_2` Nullable(Float64), `traffic_plan_3` Nullable(Float64), `traffic_plan_4` Nullable(Float64), `total` Nullable(Float64), `current_traffic` Nullable(Float64)) ENGINE = MergeTree() PARTITION BY toMonday(datetime) PRIMARY KEY(datetime)"
history_table_query = f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.history (`datetime` DateTime, `tags` String, `fields` String) ENGINE=StripeLog()"

if __name__ == "__main__":
    vega_queue = queue.Queue()
    log_queue = queue.Queue()
    ws, logger = None, None
    clickhouse_client = Client(host=CLICKHOUSE_HOST,
                           port=CLICKHOUSE_PORT,
                           user=CLICKHOUSE_USER,
                           password=CLICKHOUSE_PASSWORD)

    clickhouse_client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DB_NAME}")
    power_writer = ClickHouseWriter(clickhouse_client, power_table_query, max_inserts_count=1000, timeout_sec=30)
    traffic_writer = ClickHouseWriter(clickhouse_client, traffic_table_query, max_inserts_count=1000, timeout_sec=30)
    # history_writer = ClickHouseWriter(clickhouse_client, history_table_query, timeout_sec=30, min_inserts_count=10, max_inserts_count=2000)
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
                        "total": counter_data.get("fields").get("total"),
                        "phase_a": counter_data.get("fields").get("phase_a"),
                        "phase_b": counter_data.get("fields").get("phase_b"),
                        "phase_c": counter_data.get("fields").get("phase_c")
                    }
                    power_writer.add_values(values)
                if counter_data.get("measurement") == "traffic":
                    values = {
                        "datetime": counter_data.get("time"),
                        "counter": counter_data.get("tags").get("counter"),
                        "total": counter_data.get("fields").get("total"),
                        "traffic_plan_1": counter_data.get("fields").get("traffic_plan_1"),
                        "traffic_plan_2": counter_data.get("fields").get("traffic_plan_2"),
                        "traffic_plan_3": counter_data.get("fields").get("traffic_plan_3"),
                        "traffic_plan_4": counter_data.get("fields").get("traffic_plan_4")
                    }
                    traffic_writer.add_values(values)

                # history_writer.add_values({
                #     "datetime": datetime.now(),
                #     "tags": str(counters_data.action),
                #     "fields": str(counters_data)
                # })


                

