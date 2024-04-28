

class StatsQueries:
    def __init__(self, supadb, ch):
        self.supadb = supadb
        self.ch = ch
        
    def latest_five_races(self, cust_id: int, limit: int):
        sql = """
        select distinct subsession_id,
               series_name,
               start_time
        from iracing.lap_data ld
        left join iracing.series_entries se
            on ld.subsession_id = se.subsession_id
        where cust_id = {cust_id}
        and simsession_number = 0
        order by start_time desc
        limit {limit}
        """.format(cust_id=cust_id, limit=limit)
        results = self.ch.query(sql)
        return results.result_rows
    
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
    
    async def get_cust_id(self, discord_id):
        sql = """
        SELECT iracing_number
        FROM drivers
        WHERE discord_user_id = %s
        LIMIT 1
        """
        conn = self.supadb.conn()
        cur = conn.cursor()
        
        cur.execute(sql, (discord_id,))
        result = cur.fetchone()
        return result
