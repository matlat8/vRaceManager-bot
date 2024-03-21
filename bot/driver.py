import discord
from discord.ext import commands
import os

from supa import Supa
from iracing import iRacing

    
@commands.command()
async def driver(ctx, action: str, id, *args: str):
    if not id.isdigit():
        await ctx.send('Error: ID must be a number.')
        return
    
    id = int(id)
    
    if action == 'register':
        await ctx.send(f'Registering driver with ID {id}')
        await create_driver(ctx, id)
    else:
        await ctx.send('Invalid Action')
    
    
async def create_driver(ctx, iracing_number):
    
    ir = iRacing()
    print('running create driver')
    
    if not await ir.does_driver_exist(iracing_number):
        await ctx.send('Driver does not exist in iRacing database.')
        return
    
    driver = await ir.get_driver(iracing_number) 
    
    await ctx.send(f'Hello {driver[0]["display_name"]}!')
    
    #data, count = supa.table('drivers') \
    #                  .insert({
    #                      "discord_userid": ctx.author.id,
    #                      "iracing_number": iracing_number
    #                  })
