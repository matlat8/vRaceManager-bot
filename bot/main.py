import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

import driver as driver
from cogs.stats import Stats
from version import __version__

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

#bot = commands.Bot(intents=intents, command_prefix=os.environ.get('DISCORD_COMMAND_PREFIX'))

## Add other commands
#bot.add_cog(Stats(bot))




#bot.run(TOKEN)

async def setup():
    bot = commands.Bot(command_prefix=os.environ.get('DISCORD_COMMAND_PREFIX'), intents=intents)
    await bot.add_cog(Stats(bot))
    
    return bot

bot = asyncio.run(setup())

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=f"{os.environ.get('DISCORD_COMMAND_PREFIX')}driver help - v{__version__}"))
    print(f'{bot.user} has connected to Discord!')

bot.add_command(driver.driver)
bot.run(TOKEN)

