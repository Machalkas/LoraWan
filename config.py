import os

INFLUX_DB_NAME = "vega"
INFLUX_HOST = "192.168.0.123"
INFLUX_PORT = 8086

MYSQL_HOST = os.getenv("MYSQL_HOST") or "localhost"
MYSQL_USER = os.getenv("MYSQL_USER") or "root"
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD") or "root"
MYSQL_DB_NAME = os.getenv("MYSQL_DB_NAME") or "vega"

PGSQL_HOST = os.getenv("PGSQL_HOST") or "localhost"
PGSQL_PORT = os.getenv("PGSQL_PORT") or "5432"
PGSQL_USER = os.getenv("PGSQL_USER") or "admin"
PGSQL_PASSWORD = os.getenv("PGSQL_PASSWORD") or "admin"
PGSQL_DB_NAME = os.getenv("PGSQL_DB_NAME") or "vega"

CLICKHOUSE_DB_NAME = "vega"
CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = "9000"
CLICKHOUSE_USER = "default"
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD") or None

VEGA_URL = "ws://192.168.0.128:8002"
VEGA_PASS = "router"
VEGA_LOGIN = "router"
DELAY = 15*60
DEV_UPDATE_DELAY = 60*30

DEBUG = True
