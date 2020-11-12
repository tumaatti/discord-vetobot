import os
import random


import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.message_utils import construct_vetoed_maps
from utils.message_utils import construct_message_veto_list
from utils.message_utils import add_list_to_message

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

VETO_RUNNING = False
MAPS = (
    'anubis',
    'cache',
    'dust2',
    'inferno',
    'mirage',
    'nuke',
    'overpass',
    'train',
    'vertigo',
)
NUM_OF_PLAYERS = 0
PLAYERS = []
VETOED = 0

MESSAGE_HEADER = '```\n'
MESSAGE_HEADER += add_list_to_message(MESSAGE_HEADER, MAPS)
MESSAGE_HEADER += '\n\nVeto order:\n'


class Player:
    global MAPS

    def __init__(self, name: str):
        self.name = name
        self.mapveto = ''
        self.vetotype = ''

    def __str__(self):
        return f'{self.name} {self.mapveto}'

    def add_map(self, mapveto: str):
        if mapveto in MAPS:
            self.mapveto = mapveto.capitalize()

    def set_vetotype(self, vetotype: str):
        self.vetotype = vetotype


def end_veto():
    global PLAYERS
    global VETO_RUNNING
    global VETOED
    VETO_RUNNING = False
    VETOED = 0
    PLAYERS = []


@bot.event
async def on_ready():
    print('Logged in as', bot.user)


@bot.command(help='Pong')
async def ping(ctx):
    await ctx.send('pong')


@bot.command(help='Abort current veto')
async def vetostop(ctx):
    end_veto()
    await ctx.send('veto aborted')


@bot.command(help='Veto on your turn')
async def veto(ctx, vetomap):
    global PLAYERS
    global MAPS
    global MESSAGE_HEADER
    global VETOED
    global VETO_RUNNING

    if not VETO_RUNNING:
        await ctx.send('no active veto')
        return

    vetoer = str(ctx.author).lower()
    vetoer, _ = vetoer.split('#')
    print(vetoer)
    print(PLAYERS[VETOED])

    if vetoer != PLAYERS[VETOED].name.lower():
        await ctx.send('incorrect vetoer')
        return

    if vetoer == PLAYERS[VETOED].name.lower() and vetomap.lower() in MAPS:
        PLAYERS[VETOED].add_map(vetomap.lower())
        VETOED += 1

    message = MESSAGE_HEADER
    message += construct_message_veto_list(PLAYERS)
    message += construct_vetoed_maps(PLAYERS)
    message += '```'
    await ctx.send(message)
    if VETOED == NUM_OF_PLAYERS:
        end_veto()


@bot.command(
    name='vetostart',
    pass_sontext=True,
    help='<user> <user> ... Start veto with discord usernames',
)
async def start_veto(ctx, *args: discord.User):
    global MAPS
    global MESSAGE_HEADER
    global NUM_OF_PLAYERS
    global PLAYER
    global VETO_RUNNING

    if VETO_RUNNING:
        await ctx.send(
            'veto already running use !veto + map_name to veto!'
        )
        return

    message = MESSAGE_HEADER
    if len(args) == 0:
        await ctx.send('gimme players')
        return

    elif len(args) > 5:
        await ctx.send('too many players')
        return

    VETO_RUNNING = True
    NUM_OF_PLAYERS = len(args)
    argsl = list(args)
    for i in range(NUM_OF_PLAYERS):
        rnd = random.randint(0, len(argsl) - 1)
        # original username: tumaatti#1111
        username, _ = str(argsl.pop(rnd)).split('#')
        PLAYERS.append(Player(username))

    message += construct_message_veto_list(PLAYERS)
    message += '```'
    await ctx.send(message)


bot.run(TOKEN)
