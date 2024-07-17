import pymysql
import paramiko
import pandas as pd
from paramiko import SSHClient
from sshtunnel import SSHTunnelForwarder
from os.path import expanduser
from sqlalchemy import create_engine
import io

class MySQLSSHConnector:

    def __init__(self,
                 rsa_key_string,
                 sql_hostname,
                 sql_port,
                 ssh_host,
                 ssh_user,
                 ssh_port

                 ):
        self.mypkey = paramiko.RSAKey(file_obj=io.StringIO(rsa_key_string))
        self.sql_hostname = sql_hostname
        self.sql_port = sql_port
        self.ssh_host = ssh_host
        self.ssh_user = ssh_user
        self.ssh_port = ssh_port

        self.tunnel = SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_user,
            ssh_pkey=self.mypkey,
            remote_bind_address=(sql_hostname, sql_port)
        )

    def start_tunnel(self, sql_username,
                 sql_password,
                 sql_main_database):
        self.tunnel.start()
        print("SSH tunnel started")
        conn = pymysql.connect(
            host='127.0.0.1',
            user=sql_username,
            passwd=sql_password,
            port=self.tunnel.local_bind_port
        )
        return conn, self.tunnel.local_bind_port

    def stop_tunnel(self, conn):
        self.tunnel.stop()
        conn.close()

    def query_to_dataframe(self, query, conn):
        data = pd.read_sql_query(query, conn)
        return data

    def df_to_mysql(self, df, table_name, sql_username, sql_password, sql_main_database, if_exists='replace'):
        conn_str = f'mysql+pymysql://{sql_username}:{sql_password}@127.0.0.1:{self.tunnel.local_bind_port}/{sql_main_database}'
        engine = create_engine(conn_str)
        df.to_sql(name=table_name, con=engine, if_exists=if_exists, index=False)
        print(f"DataFrame is written to MySQL table '{table_name}' successfully.")



