import asyncio
from cgi import test
from queue import Queue
from typing import Optional
from clickhouse_driver import Client
import threading

from config import CLICKHOUSE_DB_NAME, CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_USER, CLICKHOUSE_PASSWORD


clickhouse_client = Client(host=CLICKHOUSE_HOST,
                           port=CLICKHOUSE_PORT,
                           user=CLICKHOUSE_USER)

clickhouse_client.execute(f"CREATE DATABASE IF NOT EXISTS {CLICKHOUSE_DB_NAME}")
clickhouse_client.execute(f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.power (`datetime` DateTime, `counter` UInt32, `phase_a` Float64, `phase_b` Float64, `phase_c` Float64, `total` Float64) ENGINE = MergeTree() PARTITION BY toYYYYMMDD(datetime) PRIMARY KEY(datetime)")
clickhouse_client.execute(f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.traffic (`datetime` DateTime, `counter` UInt32, `traffic_plan_1` Float64, `traffic_plan_2` Float64, `traffic_plan_3` Float64, `traffic_plan_4` Float64, `total` Float64) ENGINE = MergeTree() PARTITION BY toYYYYMMDD(datetime) PRIMARY KEY(datetime)")
clickhouse_client.execute(f"CREATE TABLE IF NOT EXISTS {CLICKHOUSE_DB_NAME}.logs (`datetime` DateTime, `tags` String, `fields` String) ENGINE=StripeLog()")

class ClickHouseDriver:
    async_loop = None
    event_loop_thread = None
    quety_queue = Queue(maxsize=0)

    def __init__(self):
        if self.async_loop is None:
            self.async_loop = asyncio.new_event_loop()
        if self.event_loop_thread is None or self.event_loop_thread.is_alive() is False:
            self.event_loop_thread = threading.Thread(target=self.event_loop, args=(self.async_loop,))
            self.event_loop_thread.daemon = True
            self.event_loop_thread.start()
    
    def event_loop(self, loop: asyncio.AbstractEventLoop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.test(1))
    
    async def clickhouse_query_executor(self):
        if not self.quety_queue.empty():
            query_dict = self.quety_queue.get()
            clickhouse_client.execute(query_dict["query"], query_dict["values"], types_check=True) # TODO: make client a class var
        await asyncio.sleep(1)


    # async def test(self, val):
    #     while True:
    #         await asyncio.sleep(1)
    #         print(f"the time has come {val}")
    
    # def add_task(self, val):
    #     # self.async_loop.call_soon_threadsafe(self.test, val)
    #     asyncio.ensure_future(self.test(val), loop=self.async_loop)

    async def writer_checker(self, max_inserts, min_inserts, timeout):
        ...
        
    def add_writer_checker(self, **kwargs):
        asyncio.ensure_future(self.writer_checker(**kwargs), loop=self.async_loop)

class ClickHouseWriter(ClickHouseDriver):
    def __init__(self,
                 table: str,
                 values_names: list,
                 min_inserts_count: Optional[int] = None,
                 max_inserts_count: int = 100,
                 timeout_sec: int = 10
                 ):
        self.max_inserts_count = max_inserts_count
        self.min_inserts_count = min_inserts_count
        self.timeout_sec = timeout_sec
        self.query = f"INSERT INTO {table} ({', '.join(values_names)}) VALUES"
        self.values_names = values_names
        self.values_list = []
    
    def add_values(self, values: dict):
        if type(values) is dict and set([*values]) != set(self.values_names):
            raise Exception("Keys do not match")
        self.values_list.append(values)
        if len(self.values_list) >= self.max_inserts_count:
            ...
    
    def write(self, client: Client):
        client.execute(self.query, self.values_list, types_check=True)
    

if __name__ == "__main__":
    from datetime import datetime
    test = ClickHouseWriter(table=f"{CLICKHOUSE_DB_NAME}.logs", values_names=["datetime", "tags", "fields"])
    for i in range(1000):
        test.add_values({"datetime": datetime.now(), "tags1": f"tag_{i}", "fields": f"field_{i}"})

    test.write(clickhouse_client)