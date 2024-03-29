# import packages
from discord.ext import commands
import os

# import locals
from iracing import iRacing
from supa import Supa

class TeamsCog(commands.Cog):
    def __init__(self, bot):
        self.iracing = iRacing()
        self.bot = bot
        self.supa = Supa(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY')).get_supabase()

    @commands.has_permission(administrator=True)
    @commands.Command()
    async def createteam(self, ctx, *args):
        if ctx.author == self.bot.user:
            return
        if not args:
            await ctx.send('Not Implemented.')
            return
        
        self.supa.table('guilds').upsert({
            'guild_id': ctx.guild.id,
        })
        
        team_name = ' '.join(args[1:])
        self.supa.table('teams').insert({
            'team_name': team_name,
            'owner_id': ctx.author.id
        }).execute()        
            
    async def create_hosted_event(ctx, subsession_id):
        
        pass
        
        