import pandas as pd

class EventQueries():
    def __init__(self, db, ch):
        self.db = db
        self.ch = ch

    async def set_notification_channel(self, channel_id, guild_id):
        conn = self.db.conn()
        cur = conn.cursor()
        query = "UPDATE guilds SET official_channel_id = %s WHERE guild_id = %s"
        cur.execute(query, (channel_id, guild_id,))
        conn.commit()
        
    async def get_laps_driven_by_driver_group_by_track(self, cust_id):
        sql = """
        select count(*) as laps_driven,
               track_name
        from 
            iracing.series_entries se
        LEFT JOIN
            iracing.lap_data ld
        ON se.subsession_id = ld.subsession_id
        WHERE ld.cust_id = {cust_id}
        group by track_name
        """.format(cust_id=cust_id)
        result = self.ch.query(sql)
        return result.result_rows
