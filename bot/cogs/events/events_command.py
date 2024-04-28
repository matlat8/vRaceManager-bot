import discord
from discord.ext import commands, tasks

# Import locals
from .queries import EventQueries
from supa import SupaDB
from clickhouse import Clickhouse

class EventCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.supadb = SupaDB('postgres', 'public')
        self.ch = Clickhouse()
        self.queries = EventQueries(self.supadb, self.ch)
        
        
    @commands.command()
    async def racelapdata(self, ctx, *args):
        if not args:
            await ctx.send('You must specify a subsession ID')
        
        
        await ctx.send('This is a placeholder command for the racelapdata command.')
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setnotificationchannel(self, ctx, *args):
        notification_options = ['hosted','official']
        if not args:
            await ctx.send(f'You must provide a notification type. Valid types: {", ".join(notification_options)}')
            return
        if args[0] not in notification_options:
            await ctx.send(f'Invalid notification type. Valid types: {", ".join(notification_options)}')
            return
        
        await self.queries.set_notification_channel(ctx.channel.id, ctx.guild.id)
        await ctx.send('This is a placeholder command for the setnotificationchannel command.')
