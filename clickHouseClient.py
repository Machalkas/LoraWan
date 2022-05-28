from clickhouse_driver import Client
from config import CLICKHOUSE_DB_NAME, CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_USER, CLICKHOUSE_PASSWORD


clickhouse_client = Client(host=CLICKHOUSE_HOST,
                           port=CLICKHOUSE_PORT,
                           user=CLICKHOUSE_USER)

clickhouse_client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DB_NAME}")
clickhouse_client.execute(f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.power (`datetime` DateTime, `counter` UInt32, `phase_a` Float64, `phase_b` Float64, `phase_c` Float64, `total` Float64) ENGINE = MergeTree() PARTITION BY toYYYYMMDD(datetime) PRIMARY KEY(datetime)")
clickhouse_client.execute(f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.traffic (`datetime` DateTime, `counter` UInt32, `traffic_plan_1` Float64, `traffic_plan_2` Float64, `traffic_plan_3` Float64, `traffic_plan_4` Float64, `total` Float64) ENGINE = MergeTree() PARTITION BY toYYYYMMDD(datetime) PRIMARY KEY(datetime)")
clickhouse_client.execute(f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.logs (`datetime` DateTime, `tags` String, `fields` String) ENGINE=StripeLog()")
x = clickhouse_client.execute("show databases")

print(x)
