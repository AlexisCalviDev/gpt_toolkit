import pymysql
import pandas as pd
from sqlalchemy import create_engine
import json
from urllib.parse import quote_plus
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
        self.conn = pymysql.connect(
            host=self.sql_hostname,
            user=self.sql_username,
            passwd=self.sql_password,
            port=self.sql_port,
            database=self.sql_database
        )
        print("Connected to MySQL database")

    def disconnect(self):
        if hasattr(self, 'conn'):
            self.conn.close()
            print("Disconnected from MySQL database")

    def query_to_dataframe(self, query):
        data = pd.read_sql_query(query, self.conn)
        return data

    def json_to_df(self, json_data):
        # Si json_data est une chaîne JSON, on la convertit en dictionnaire
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except json.JSONDecodeError:
                raise ValueError("La chaîne d'entrée n'est pas un JSON valide.")

        # Vérifier que json_data est un dictionnaire
        if not isinstance(json_data, dict):
            raise ValueError("L'entrée doit être un dictionnaire ou une chaîne JSON représentant un objet.")

        # Créer un DataFrame à partir du dictionnaire
        df = pd.DataFrame([json_data])

        return df

    def df_to_mysql(self, df, table_name, if_exists='append'):
        conn_str = f'mysql+pymysql://{self.conn.user}:{self.conn.password}@{self.sql_hostname}:{self.sql_port}/{self.conn.db}'
        engine = create_engine(conn_str)
        df.to_sql(name=table_name, con=engine, if_exists=if_exists, index=False)
        print(f"DataFrame is written to MySQL table '{table_name}' successfully.")

    def json_to_mysql(self, json_data, table_name, if_exists='append'):
        df = self.json_to_df(json_data)
        conn_str = f'mysql+pymysql://{self.sql_username}:{quote_plus(self.sql_password)}@{self.sql_hostname}:{self.sql_port}/{self.sql_database}'
        print(f"Connecting to: mysql+pymysql://{self.sql_username}:****@{self.sql_hostname}:{self.sql_port}/{self.sql_database}")
        engine = create_engine(conn_str)
        df.to_sql(name=table_name, con=engine, if_exists=if_exists, index=False)
        print(f"JSON is written to MySQL table '{table_name}' successfully.")