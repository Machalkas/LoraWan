import asyncio
from datetime import datetime
import queue
import time
from threading import Thread
import config
from utils.dataClass import CounterData
from vegaClient import Vega
from utils import logger
from clients.mqtt_client import MqttClient

import config

# power_table_query = f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.power (`datetime` DateTime, `counter` UInt32, `phase_a` Nullable(Float64), `phase_b` Nullable(Float64), `phase_c` Nullable(Float64), `total` Nullable(Float64)) ENGINE = Log()"
# traffic_table_query =  f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.traffic (`datetime` DateTime, `counter` UInt32, `traffic_plan_1` Nullable(Float64), `traffic_plan_2` Nullable(Float64), `traffic_plan_3` Nullable(Float64), `traffic_plan_4` Nullable(Float64), `total` Nullable(Float64), `current_traffic` Nullable(Int32)) ENGINE = Log()"
# history_table_query = f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.history (`datetime` DateTime, `tags` String, `fields` String) ENGINE=Log()"

async def main():
    logger.header("iot vega broker")

    vega_queue = queue.Queue()
    mqtt_client = MqttClient(
        handler=None,
        host=config.MQTT_HOST,
        port=config.MQTT_PORT,
        username=config.MQTT_USERNAME,
        password=config.MQTT_PASSWORD,
        topics_to_subscribe=config.MQTT_TOPICS_TO_SUBSCRIBE
    )
    asyncio.get_event_loop().create_task(mqtt_client.connect())
    await asyncio.sleep(1)
    ws = None
    # pgsql_client = Counters(PGSQL_HOST, PGSQL_PORT, PGSQL_USER, PGSQL_PASSWORD, PGSQL_DB_NAME, "create table if not exists counters (devEui text, devName text)")
    
    # clickhouse_client = Client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, user=CLICKHOUSE_USER)

    # clickhouse_client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DB_NAME}")
    # power_writer = ClickHouseWriter(clickhouse_client, power_table_query, max_inserts_count=1000, timeout_sec=30)
    # traffic_writer = ClickHouseWriter(clickhouse_client, traffic_table_query, max_inserts_count=1000, timeout_sec=30)
    # history_writer = ClickHouseWriter(clickhouse_client, history_table_query, timeout_sec=30, min_inserts_count=10, max_inserts_count=2000)
    while True:
        if ws is None:
            logger.success("vega start")
            ws = Thread(target=Vega,
                        args=(config.VEGA_URL,
                              config.VEGA_LOGIN,
                              config.VEGA_PASS,
                              config.DATA_READ_DELAY,
                              config.COUNTERS_UPDATE_DELAY,
                              vega_queue),
                        daemon=True,
                        name="VegaThread")
            ws.start()
        if not ws.is_alive():
            logger.warning("vega stop")
            ws = None
            await asyncio.sleep(5)
            continue
        
        if not vega_queue.empty():
            counters_data: CounterData = vega_queue.get()
            if counters_data.action == counters_data.GET_DEVICES:
                # pgsql_client.save(counters_data.devices)
                await mqtt_client.publish(f"device/update_energy_meters", counters_data.devices)
            for counter_data in counters_data.get():
                if counter_data.get("measurement") == "power":
                    values = {
                        "metric": "power",
                        "datetime": datetime.strftime(counter_data.get("time"), config.DT_FORMAT),
                        "counter": counter_data.get("tags").get("counter"),
                        "total": counter_data.get("fields").get("total"),
                        "phase_a": counter_data.get("fields").get("phase_a"),
                        "phase_b": counter_data.get("fields").get("phase_b"),
                        "phase_c": counter_data.get("fields").get("phase_c")
                    }
                    # power_writer.add_values(values)
                    await mqtt_client.publish(f"device/save_statistic", values)
                if counter_data.get("measurement") == "traffic":
                    values = {
                        "metric": "traffic",
                        "datetime": datetime.strftime(counter_data.get("time"), config.DT_FORMAT),
                        "counter": counter_data.get("tags").get("counter"),
                        "total": counter_data.get("fields").get("total"),
                        "traffic_plan_1": counter_data.get("fields").get("traffic_plan_1"),
                        "traffic_plan_2": counter_data.get("fields").get("traffic_plan_2"),
                        "traffic_plan_3": counter_data.get("fields").get("traffic_plan_3"),
                        "traffic_plan_4": counter_data.get("fields").get("traffic_plan_4"),
                        "current_traffic": counter_data.get("fields").get("current_traffic")
                    }
                    # traffic_writer.add_values(values)
                    await mqtt_client.publish(f"device/save_statistic", values)

        await asyncio.sleep(.2)
                # history_writer.add_values({
                #     "datetime": datetime.now(),
                #     "tags": str(counters_data.action),
                #     "fields": str(counters_data)
                # })

if __name__ == "__main__":
    asyncio.run(main())
                

