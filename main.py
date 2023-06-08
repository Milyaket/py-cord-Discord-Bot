import discord, os
from discord.ext import commands

# This bot made with py-cord 2.4.1 by Milyaket#9669
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# All cog folders comes here
cogs = ["Ticket_System"]

for cog in cogs:
    for file in os.listdir(cog):
        if file.endswith(".py"):
            bot.load_extension(f"{cog}.{file[:-3]}")

@bot.event
async def on_ready():
    print(bot.user.name + " is online.")



# Run your bot
bot.run(token=os.getenv("TOKEN"))