import discord
from discord.ext import commands
import os

from supa import Supa
from iracing import iRacing

    
    
class Command:
    def execute(self, ctx, *args):
        raise NotImplementedError
    
class RegisterDriverCommand(Command):
    def __init__(self, iracing, supa):
        self.iracing = iracing
        self.supa = supa
    
    async def execute(self, ctx, id):
        await ctx.send(f'Registering driver with ID {id}')
        if not id.isdigit():
            await ctx.send('Error: ID must be a number.')
        id = int(id)
        await self.create_driver(ctx, id)
        
    async def update_db_driver(self, ctx, driver):
        self.supa.table('drivers').update({
            "iracing_number": driver[0]["cust_id"],
            "driver_name": driver[0]["display_name"]
        }).eq('guild_id', ctx.guild.id).eq('discord_user_id', ctx.author.id).execute()
        await ctx.send('Driver information updated.')
        
    async def create_driver(self, ctx, iracing_number):
        
        if not await self.iracing.does_driver_exist(iracing_number):
            await ctx.send('Driver does not exist in iRacing database.')
            return
        
        driver = await self.iracing.get_driver(iracing_number)
        
        print(driver)
        
        
        
        existing_driver = None #self.supa.table('drivers').select().eq('guild_id', ctx.guild.id).eq('discord_user_id', ctx.author.id).execute()
        
        if existing_driver:
            # If such a record exists, update it
            await self.update_db_driver(ctx, driver)
        else:
            data, count = self.supa.table('drivers') \
                                .upsert({
                                    "guild_id": ctx.guild.id,
                                    "discord_user_id": ctx.author.id,
                                    "iracing_number": iracing_number,
                                    "driver_name": driver[0]["display_name"]
                                }).execute()
            try:
                await ctx.author.edit(nick=driver[0]["display_name"])
            except discord.errors.Forbidden as e:
                print(e)
                await ctx.send('I do not have permission to change your nickname.')
            await ctx.send('Driver registered.')
            
    async def return_help_message(self):
        embed=discord.Embed(title="Driver Command Help", description="Register and manage your iRacing driver information.", color=0x00ff00)
        embed.add_field(name="Register", value="driver register (iRacing ID)", inline=False)
        return embed
    

@commands.command()
async def driver(ctx, *args: str):
    ir = iRacing()
    supa = Supa(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY')).get_supabase()
    command = RegisterDriverCommand(ir, supa)
    
    if not args:
        await ctx.send(embed=await command.return_help_message())
        return
    if args[0] == 'register':
        await command.execute(ctx, args[1])
    else:
        await ctx.send(embed=await command.return_help_message())
    


