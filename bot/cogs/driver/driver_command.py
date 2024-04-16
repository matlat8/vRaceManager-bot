# Package imports
from discord.ext import commands, tasks

import os
import pandas

# Import locals
from supa import SupaDB, Supa
from .queries import DriverQueries
from .embeds import DriverEmbed
from iracing import iRacing


class DriverCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supadb = SupaDB('postgres', 'public')
        self.queries = DriverQueries(self.supadb)
        self.iracing = iRacing()
        self.embed = DriverEmbed()
        
    
    @commands.command()
    async def latestraces(self, ctx, *args):
        # Get the drivers ID 
        driver_id = await self.queries.get_driver_by_discordid(ctx.author.id)
        print(driver_id)

        if not driver_id:
            await ctx.send('You have not registered your iRacing driver ID. Use the `driver register (iRacing ID)` command to register.')
            
        data = await self.iracing.get_member_recent_races(driver_id)   
        print(data)
        embed = self.embed.member_recent_race(data['races'][0])
        await ctx.send(embed=embed)
        
    def get_driver_id(self, discord_id) -> int:
        driver_id = self.supa.table('drivers').select('iracing_number').eq('discord_user_id', discord_id).execute()
        if not driver_id.data:
            return None
        return driver_id.data[0]['iracing_number']
        
        
    