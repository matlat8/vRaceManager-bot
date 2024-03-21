import os
from supabase import create_client, Client


class Supa:
    def __init__(self, url: str, key: str):
        self.url = url
        self.key = key
        self.supabase = create_client(url, key)

    def get_supabase(self) -> Client:
        return self.supabase
