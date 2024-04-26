import pandas as pd

class EventQueries():
    def __init__(self, db):
        self.db = db

    async def set_notification_channel(self, channel_id, guild_id):
        conn = self.db.conn()
        cur = conn.cursor()
        query = "UPDATE guilds SET official_channel_id = %s WHERE guild_id = %s"
        cur.execute(query, (channel_id, guild_id,))
        conn.commit()
