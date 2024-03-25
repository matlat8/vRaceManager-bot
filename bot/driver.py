import discord
from discord.ext import commands
import os
import arrow

from supa import Supa
from iracing import iRacing

    
    
class Command:
    def execute(self, ctx, *args):
        raise NotImplementedError
    
class RegisterDriverCommand(Command):
    def __init__(self, ctx):
        self.iracing = iRacing()
        self.supa = Supa(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY')).get_supabase()
        self.ctx = ctx
    
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
    
    async def lookup(self, search_term):
        result = self.supa.table('drivers').select('iracing_number', 'driver_name') \
                                           .eq('driver_name', search_term) \
                                           .eq('guild_id', self.ctx.guild.id) \
                                           .execute()
        driver_data = await self.iracing.get_driver(search_term)
        cust_id = driver_data[0]["cust_id"]
        driver_profile = await self.iracing.get_driver_profile(cust_id)
        embed = self.Embed().driver_lookup(driver_profile)
        print(driver)
        await self.ctx.send(embed=embed)
    
    async def perform_lookup(self, ctx, search_term):
        pass
        
    class Embed:
        def driver_lookup(self, driver_profile):    
            
            description_1 = f"Member Since: {driver_profile['member_info']['member_since']}\n"
            description_2 = f"Last Seen: {arrow.get(driver_profile['member_info']['last_login']).format('YYYY-MM-DD HH:mm')}\n"
            description_3 = f"iRacing ID: {driver_profile['member_info']['cust_id']}\n"
            description_4 = f"Club: {driver_profile['member_info']['club_name']}"
            description = description_1 + description_2 + description_3 + description_4
            
            embed=discord.Embed(title=driver_profile['member_info']['display_name'], description=description, color=0x00ff00)
            
            for license in driver_profile['member_info']['licenses']:
                embed.add_field(name=f"{license['category_name']}", value=f"SR: {license['group_name']} {license['safety_rating']} | IR: {license['irating']}", inline=False)
            
            return embed
        
        async def return_help_message(self):
            embed=discord.Embed(title="Driver Command Help", description="Register and manage your iRacing driver information.", color=0x00ff00)
            
            lookup_value_1 = "Show driver information like iR/SR, iRacing ID, etc.\n"
            lookup_value_2 = f"**Usage: ** *{os.environ.get('DISCORD_COMMAND_PREFIX')}driver lookup (iRacing ID or driver name)*"
            lookup_value = lookup_value_1 + lookup_value_2
            
            embed.add_field(name="Lookup", value=lookup_value, inline=False)
            
            register_value_1 = "Register your iRacing driver information with the bot to show on team leaderboard and enter events.\n"
            register_value_2 = f"**Usage: ** *{os.environ.get('DISCORD_COMMAND_PREFIX')}driver register (iRacing ID)*"
            register_value = register_value_1 + register_value_2
            
            embed.add_field(name="Register", value=register_value, inline=False)
            return embed
    
class Driver():
    def __init__(self, iracing, supa):
        self.iracing = iracing
        self.supa = supa
    



@commands.command()
async def driver(ctx, *args: str):
    command = RegisterDriverCommand(ctx)
    
    # no args are present
    if not args:
        await ctx.send(embed=await command.Embed().return_help_message())
        return
    # if the first argument is register
    if args[0] == 'register':
        await command.execute(ctx, args[1])
    # if the first argument is lookup
    if args[0] == 'lookup':
        lookup_string = ' '.join(args[1:])
        await command.lookup(lookup_string)
        #await ctx.send('Lookup command not implemented yet.')
    else:
        await ctx.send(embed=await command.Embed().return_help_message())
    


