import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

import driver as driver
from cogs.stats import Stats
from version import __version__

#load_dotenv()
TOKEN = os.environ.get('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

async def setup():
    activity = discord.Activity(name=f"{os.environ.get('DISCORD_COMMAND_PREFIX')}driver help - v{__version__}", type=discord.ActivityType.listening)
    bot = commands.Bot(command_prefix=os.environ.get('DISCORD_COMMAND_PREFIX'), intents=intents, activity=activity)
    await bot.add_cog(Stats(bot))
    
    return bot

bot = asyncio.run(setup())

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

bot.add_command(driver.driver)
bot.run(TOKEN)

