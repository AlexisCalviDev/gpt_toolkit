import pymysql
import pandas as pd
from sqlalchemy import create_engine

class MySQLConnector:

    def __init__(self,
                 sql_hostname,
                 sql_port,
                 sql_username,
                 sql_password,
                 sql_database
                 ):
        self.sql_hostname = sql_hostname
        self.sql_port = sql_port
        self.sql_username = sql_username
        self.sql_password = sql_password
        self.sql_database = sql_database

    def connect(self):
        self.conn = pymysql.connect(
            host=self.sql_hostname,
            user=self.sql_username,
            passwd=self.sql_password,
            port=self.sql_port,
            database=self.sql_database
        )
        print("Connected to MySQL database")
        return self.conn

    def disconnect(self):
        if hasattr(self, 'conn'):
            self.conn.close()
            print("Disconnected from MySQL database")

    def query_to_dataframe(self, query):
        data = pd.read_sql_query(query, self.conn)
        return data

    def df_to_mysql(self, df, table_name, if_exists='append'):
        conn_str = f'mysql+pymysql://{self.conn.user}:{self.conn.password}@{self.sql_hostname}:{self.sql_port}/{self.conn.db}'
        engine = create_engine(conn_str)
        df.to_sql(name=table_name, con=engine, if_exists=if_exists, index=False)
        print(f"DataFrame is written to MySQL table '{table_name}' successfully.")