import pymysql
from utils import logger, log_exceptions
from config import MYSQL_HOST, MYSQL_DB_NAME, MYSQL_PASSWORD, MYSQL_USER


def mysql_connect(func):
    def wrapper(self, *args, **kargs):
        mysql_connection = pymysql.connect(host=self.db_url, user=self.db_user, password=self.db_password, database=self.database)
        return func(self,  mysql_connection=mysql_connection, *args, **kargs)
    return wrapper


class MysqlClient:
    def __init__(self,
                 db_url: str,
                 db_user: str,
                 db_password: str,
                 database: str = "default",
                 create_table_query: str = None,
                 table_columns: str = None,
                 table_name: str = None) -> None:
        if create_table_query is None and (table_columns is None or table_name is None):
            raise ValueError("create_table_query and (table_columns or table_name) can't both be None")
        elif create_table_query is not None:
            columns = create_table_query.split("(")[1]
            self.table_columns = [c.split()[0] for c in columns.split(",")]
            self.table_name = create_table_query.split("(")[0].split()[-1]
        else:
            self.table_columns = table_columns
            self.table_name = table_name
        self.db_url = db_url
        self.db_user = db_user
        self.db_password = db_password
        self.database = database

        if create_table_query:
            mysql_connection = pymysql.connect(host=db_url, user=db_user, password=db_password, database=database)
            with mysql_connection:
                cur = mysql_connection.cursor()
                cur.execute(create_table_query)
                mysql_connection.commit()
        logger.info(f"create table {self.table_name}")
    
    def save(self, data) -> None:
        raise Exception("Save method was newer override")
    
    def get(self, data) -> None:
        raise Exception("Get method was newer override")


class Counters(MysqlClient):

    def wrap_string(self, string: str):
        return f"'{string}'"

    @mysql_connect
    @log_exceptions
    def save(self, counters: list, mysql_connection) -> None:
        counters_string = ""
        for counter in counters:
            counters_string += f"({', '.join([self.wrap_string(counter.get(t_key)) for t_key in self.table_columns])}),"
        counters_string = counters_string[:-1]
        sql_query = f"insert into {self.table_name} ({', '.join(self.table_columns)}) values {counters_string};"
        
        logger.debug(f"sql query: \"{sql_query}\"")

        with mysql_connection:
            cur = mysql_connection.cursor()
            cur.execute(f"TRUNCATE TABLE {self.table_name}")
            cur.execute(sql_query)
            mysql_connection.commit()
        logger.info(f"save devices to db ({len(counters)})")


if __name__ == "__main__":
    c = Counters(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB_NAME, "create table if not exists counters (kek text, pek int)")
    c.save([{"kek":"2", "pek":"3"}, {"kek":"2", "pek":"3"}])
    c.save([{"kek":"qwerty", "pek":"123"}])
    
