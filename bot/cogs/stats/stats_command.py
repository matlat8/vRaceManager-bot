import discord
from discord.ext import commands, tasks

# Local Imports
from .embeds import StatsEmbeds

class StatsCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed = StatsEmbeds()
        
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