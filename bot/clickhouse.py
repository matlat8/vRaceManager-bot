import clickhouse_connect
import os


class Clickhouse:
    def __init__(self):
        self.client = clickhouse_connect.get_client(host=os.environ.get('CLICKHOUSE_HOST'), port=os.environ.get('CLICKHOUSE_PORT'), user=os.environ.get('CLICKHOUSE_USER'), password=os.environ.get('CLICKHOUSE_PASSWORD'))

    def close(self):
        self.cursor.close()
        self.conn.close()