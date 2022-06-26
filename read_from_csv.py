from datetime import datetime
from clickhouse_driver import Client
from database_clients.clickHouseClient import ClickHouseWriter

from config import CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_USER, CLICKHOUSE_DB_NAME, CLICKHOUSE_PASSWORD, PGSQL_DB_NAME, PGSQL_HOST, PGSQL_PASSWORD, PGSQL_PORT, PGSQL_USER


power_table_query = f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.power (`datetime` DateTime, `counter` UInt32, `phase_a` Nullable(Float64), `phase_b` Nullable(Float64), `phase_c` Nullable(Float64), `total` Nullable(Float64)) ENGINE = Log()"
traffic_table_query =  f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.traffic (`datetime` DateTime, `counter` UInt32, `traffic_plan_1` Nullable(Float64), `traffic_plan_2` Nullable(Float64), `traffic_plan_3` Nullable(Float64), `traffic_plan_4` Nullable(Float64), `total` Nullable(Float64), `current_traffic` Nullable(Int32)) ENGINE = Log()"

clickhouse_client = Client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, user=CLICKHOUSE_USER)

power_writer = ClickHouseWriter(clickhouse_client, power_table_query, max_inserts_count=1000, timeout_sec=30)
traffic_writer = ClickHouseWriter(clickhouse_client, traffic_table_query, max_inserts_count=1000, timeout_sec=30)

with open("E:/power.csv", "r") as power:
    raw = power.read()
    raws = raw.split("\n")[:-1]
    for r in raws:
        v = r.split(",")
        values = {
            "datetime": datetime.fromisoformat(v[0].replace('"',"")),
            "counter": int(v[1]),
            "total": float(v[2]),
            "phase_a": float(v[3]),
            "phase_b": float(v[4]),
            "phase_c": float(v[5])
        }
        power_writer.add_values(values)


with open("E:/traffic.csv", "r") as power:
    raw = power.read()
    raws = raw.split("\n")[:-1]
    for r in raws:
        v = r.split(",")
        values = {
            "datetime": datetime.fromisoformat(v[0].replace('"',"")),
            "counter":  int(v[1]),
            "traffic_plan_1": float(v[2]),
            "traffic_plan_2": float(v[3]),
            "traffic_plan_3": float(v[4]),
            "traffic_plan_4": float(v[5]),
            "total": float(v[6]),
            "current_traffic": int(v[7])
        }
        traffic_writer.add_values(values)


while True:
    pass