import psycopg2
from database_clients import DBClient, db_connect
from utils import logger, log_exceptions
from config import PGSQL_HOST, PGSQL_DB_NAME, PGSQL_PASSWORD, PGSQL_PORT, PGSQL_USER



class Counters(DBClient):
    def __init__(self,
                 host: str,
                 port: int,
                 db_user: str,
                 db_password: str,
                 database: str = "default",
                 create_table_query: str = None,
                 table_columns: str = None,
                 table_name: str = None) -> None:
        super().__init__(host, port, db_user, db_password, database, create_table_query, table_columns, table_name)
        if create_table_query:
            self.create_tables(create_table_query=create_table_query)

    def connect(self, host, port, user, password, database):
        return psycopg2.connect(host=host, user=user, password=password, dbname=database)

    def wrap_string(self, string: str):
        return f"'{string}'"

    @db_connect
    @log_exceptions
    def save(self, counters: list, db_connection) -> None:
        counters_string = ""
        for counter in counters:
            counters_string += f"({', '.join([self.wrap_string(counter.get(t_key)) for t_key in self.table_columns])}),"
        counters_string = counters_string[:-1]
        sql_query = f"insert into {self.table_name} ({', '.join(self.table_columns)}) values {counters_string};"
        logger.debug(f"sql query: \"{sql_query}\"")
        with db_connection:
            cur = db_connection.cursor()
            cur.execute(f"TRUNCATE TABLE {self.table_name}")
            cur.execute(sql_query)
            db_connection.commit()
        logger.info(f"save devices to db ({len(counters)})")
    
    @db_connect
    @log_exceptions
    def create_tables(self, db_connection, create_table_query):
        with db_connection:
            cur = db_connection.cursor()
            cur.execute(create_table_query)
            db_connection.commit()
        logger.info(f"create table {self.table_name}")


if __name__ == "__main__":
    c = Counters(PGSQL_HOST, PGSQL_PORT, PGSQL_USER, PGSQL_PASSWORD, PGSQL_DB_NAME, "create table if not exists counters (kek text, pek int)")
    c.save(counters=[{"kek":"2", "pek":"3"}, {"kek":"2", "pek":"3"}])
    c.save(counters=[{"kek":"qwerty", "pek":"123"}])
    

"""
docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=iotlab -e POSTGRES_USER=admin -e POSTGRES_DB=vega -e PGDATA=/var/lib/postgresql/data/pgdata -v /home/iotlab/postgres:/var/lib/postgresql/data postgres
"""