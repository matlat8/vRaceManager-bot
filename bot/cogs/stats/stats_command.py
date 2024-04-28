import discord
from discord.ext import commands, tasks

# Local Imports
from .embeds import StatsEmbeds
from .queries import StatsQueries
from clickhouse import Clickhouse
from supa import SupaDB

class StatsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed = StatsEmbeds()
        self.supadb = SupaDB('postgres', 'public')
        
    @commands.command()
    async def stats(self, ctx, *args):
        if not args:
            await ctx.send(embed=self.embed.stats_help())
            return
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        msg = await self.bot.wait_for('message', check=check)
        await ctx.send(f'You said: {msg.content}')
        pass
    
    @commands.command()
    async def lapspertrack(self, ctx):
        # Prepare
        ch = Clickhouse()
        queries = StatsQueries(self.supadb, ch.client)
        
        # Get cust_id from discord ID
        cust_id = await queries.get_cust_id(ctx.author.id)
        print(cust_id)
        
        # Get data
        data = await queries.get_laps_driven_by_driver_group_by_track(cust_id[0])
        embed = self.embed.laps_per_track(data)
        await ctx.send(embed=embed)