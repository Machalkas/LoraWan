import sqlite3
from utils import logger, log_exceptions

db_connection = None

def auto_commit(func):
    def wrapper(self, *args, **kargs):
        global db_connection
        func_result = func(self, *args, **kargs)
        db_connection.commit()
        return func_result
    return wrapper


class SqliteClient:  # TODO rewrite to mysql client
    def __init__(self, create_table_query: str = None, table_columns: str = None, table_name: str = None, db_path: str = "db.sqlite3") -> None:
        if create_table_query is None and (table_columns is None or table_name is None):
            raise ValueError("create_table_query and table_args can't both be None")
        elif create_table_query is not None:
            columns = create_table_query.split("(")[1]
            self.table_columns = [c.split()[0] for c in columns.split(",")]
            self.table_name = create_table_query.split("(")[0].split()[-1]
        else:
            self.table_columns = table_columns
            self.table_name = table_name

        self.db_path = db_path
        global db_connection
        if db_connection is None:
            db_connection = sqlite3.connect(db_path)
            logger.important("create sqlite connection")
        self.cursor = db_connection.cursor()
        if create_table_query:
            self.cursor.execute(create_table_query)
            db_connection.commit()
            logger.info("create sqlite tables")
    

class Counters(SqliteClient):

    @auto_commit
    @log_exceptions
    def clear_table(self) -> None:
        self.cursor.execute("DELETE FROM counters")        

    @auto_commit
    # @log_exceptions
    def save_devices(self, devices: list) -> None:
        values_list = []
        for device in devices:
            # f"({', '.join([str(device[val]) for val in device.keys()])}), "
            values_list.append(tuple([str(device[val]) for val in device.keys()]))

        sql_query = f"sqlite save_devices query: 'insert into {self.table_name}({', '.join([f'{k}' for k in devices[0].keys()])}) values ({', '.join(['?']*len(devices[0].keys()))})'"
    
        logger.debug(sql_query)
        self.clear_table()
        self.cursor.executemany(sql_query, values_list)
    @log_exceptions
    def get_devices(self) -> list:
        self.cursor.execute(f"select * from {self.table_name}")
        return self.cursor.fetchall()



if __name__ == "__main__":
    c = Counters("create table if not exists counters (kek text, pek text)")
    c.save_devices([{"kek":"2", "pek":"3"}, {"kek":"2", "pek":"3"}])
    print(c.get_devices())
    c.save_devices([{"kek":"qwerty", "pek":"123"}])
    print(c.get_devices())
    
