import discord
from discord.ext import commands
import json
from supa import Supa
import os
import arrow

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.statslogic = StatsLogic()

    @commands.command()
    async def stats(self, ctx, *args):
        if not args:
            await ctx.send(embed=self.Embeds().stats_help())
            return
        
        command = args[0].lower()
        if command == 'officialpoints':
            await self.get_official_points(ctx)
            
        else:
            await ctx.send(embed=self.Embeds().stats_help())
        
    async def get_official_points(self, ctx):
        data = StatsLogic().get_champ_points()
        await ctx.send(embed=self.Embeds().champ_points(data))
        
        
    class Embeds:
        @staticmethod
        def champ_points(data):
            embed=discord.Embed(title=f"iRacing Official Championship Points", description="Current team championship points standings.", color=0x00ff00)
            embed.set_footer(text=StatsLogic().format_date(data[0]['week_start']))
            rank = 0
            for row in data:
                rank += 1
                embed.add_field(name=f'{rank}.) {row["driver_name"]}', value=row['total_champ_points'], inline=False)
            return embed
        
        @staticmethod
        def stats_help():
            embed=discord.Embed(title="Stats Command Help", description="View various team iRacing statistics. View how to use the stats commands", color=0x00ff00)
            embed.add_field(name="!stats officialpoints", value="Compare who is putting up the most official iRacing series points across all disciplines", inline=False)
            return embed
        
class StatsLogic:
    def __init__(self):
        self.supa = Supa(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY')).get_supabase()
    
    def get_champ_points(self):
        data = self.supa.table('v_lw_driver_champpoints').select('*').execute()
        
        return data.data
    
    def format_date(self, date):
        date = arrow.get(date)
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        day = date.day
        suffix = suffixes.get(day if day < 20 else day % 10, 'th')
        return date.format(f'dddd, MMMM D{suffix} YYYY')
    