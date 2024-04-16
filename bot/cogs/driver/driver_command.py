# Package imports
import discord
from discord.ext import commands, tasks

import os
import pandas


# Import locals
from supa import SupaDB, Supa
from .queries import DriverQueries
from .embeds import DriverEmbed
from .charts import DriverCharts
from iracing import iRacing


class DriverCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supadb = SupaDB('postgres', 'public')
        self.queries = DriverQueries(self.supadb)
        self.iracing = iRacing()
        self.embed = DriverEmbed()
        self.charts = DriverCharts()
        
    
    @commands.command()
    async def latestrace(self, ctx, *args):
        # Get the drivers ID 
        driver_id = await self.queries.get_driver_by_discordid(ctx.author.id)
        print(driver_id)

        if not driver_id:
            await ctx.send('You have not registered your iRacing driver ID. Use the `driver register (iRacing ID)` command to register.')
            
        # Get their most recent race
        data = await self.iracing.get_member_recent_races(driver_id)   
        subsession_id = data['races'][0]['subsession_id']
        # Create the embed to end
        embed = self.embed.member_recent_race(data['races'][0])
        # Get the drivers lap data
        lap_data = await self.queries.get_subsession_lapdata_for_custid(subsession_id, driver_id[0])
        await ctx.send(embed=embed)
        filename = self.charts.create_laptime_chart(lap_data, ctx)
        await ctx.send(file=discord.File(filename))
        os.remove(filename)
        
    def get_driver_id(self, discord_id) -> int:
        driver_id = self.supa.table('drivers').select('iracing_number').eq('discord_user_id', discord_id).execute()
        if not driver_id.data:
            return None
        return driver_id.data[0]['iracing_number']
        
        
    