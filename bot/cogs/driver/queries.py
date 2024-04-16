import pandas as pd

class DriverQueries():
    def __init__(self, db):
        self.db = db

    async def get_driver_by_discordid(self, discord_id):
        conn = self.db.conn()
        cur = conn.cursor()
        query = "SELECT iracing_number FROM drivers WHERE discord_user_id = %s"
        cur.execute(query, (discord_id,))
        return cur.fetchone()

    async def get_driver_by_name(self, name):
        query = "SELECT * FROM drivers WHERE name = $1"
        return await self.db.fetchrow(query, name)

    async def get_driver_by_id(self, driver_id):
        query = "SELECT * FROM drivers WHERE id = $1"
        return await self.db.fetchrow(query, driver_id)

    async def get_drivers(self):
        query = "SELECT * FROM drivers"
        return await self.db.fetch(query)

    async def get_driver_by_team(self, team_id):
        query = "SELECT * FROM drivers WHERE team_id = $1"
        return await self.db.fetch(query, team_id)

    async def get_driver_latest_race(self, discord_id):
        conn = self.db.conn()
        cur = conn.cursor()
        query = """
        SELECT
            subsession_id
        FROM series_entries se
            left join drivers d
                on se.cust_id = d.iracing_number
        WHERE d.discord_user_id = '{discord_id}'
        --AND se.has_lapdata = TRUE --might enable this in the future for another feature.
        ORDER BY se.created_at desc
        LIMIT 1""".format(discord_id=discord_id)
        cur.execute(query)
        return cur.fetchone()
        
    async def get_subsession_lapdata_for_custid(self, subsession_id, cust_id) -> pd.DataFrame:
        conn = self.db.conn()
        cur = conn.cursor()
        sql = """
        select
            lap_number,
            display_name,
            lap_time / 10000::float as lap_time,
            lap_events,
            lap_position,
            interval / 10000::float as interval,
            fastest_lap
        from lap_data
            where subsession_id = {subsession}
            AND simsession_number in (0)
            AND lap_number >= 1
            AND cust_id = {cust_id}
        order by 
            simsession_number, lap_number
            """.format(subsession=subsession_id, cust_id=cust_id)
            
        df = pd.read_sql_query(sql, conn)
            
        return df