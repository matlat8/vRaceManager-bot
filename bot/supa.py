import os
from supabase import create_client, Client
import psycopg2


class Supa:
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.supabase = create_client(url, key)

    def get_supabase(self) -> Client:
        return self.supabase

class SupaDB:
    def __init__(self, db: str, schema: str):
        self.db = db
        self.schema = schema
        self.user = os.environ.get('DB_USER')
        self.password = os.environ.get('DB_PASSWORD')
        self.host = os.environ.get('DB_HOST')
        self.port = os.environ.get('DB_PORT')
        
    def conn(self):
        connection = psycopg2.connect(database=self.db, user=self.user, password=self.password, host=self.host, port=self.port)
        
        return connection
        
         