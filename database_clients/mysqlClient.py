import pymysql
from database_clients import DBClient, mysql_connect
from utils import logger, log_exceptions
from config import MYSQL_HOST, MYSQL_DB_NAME, MYSQL_PASSWORD, MYSQL_USER



class Counters(DBClient):

    def connect(self, host, port, user, password, database) -> pymysql.Connection:
        return pymysql.connect(host=host, port=port, user=user, password=password, database=database)

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
    
