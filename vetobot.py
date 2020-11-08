import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')

description = "A bot"

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix='!',
    description=description,
    intents=intents
)


@bot.event
async def on_ready():
    print('Logged in as', bot.user)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def veto(ctx, *args):
    if len(args) == 0:
        await ctx.send('gimme players')
        return
    elif len(args) > 5:
        await ctx.send('too many players')
        return
    argsl = list(args)
    message = (
        '```\n'
        'Maps: Anubis, Cache, Dust2, Inferno, Mirage, Nuke, '
        'Overpass, Train, Vertigo\n\n'
        'Veto order:\n'
    )
    for i in range(len(argsl)):
        vetoer = argsl.pop(random.randint(0, len(argsl) - 1))
        if i < len(args) - 3:
            message += f'Ban:  {vetoer}\n'
        else:
            message += f'Pick: {vetoer}\n'
    message += '```'

    await ctx.send(message)


bot.run(TOKEN)
