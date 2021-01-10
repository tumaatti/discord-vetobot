import copy
import os
import random
from typing import List

import discord.utils
from discord.ext import commands
from dotenv import load_dotenv

from utils.message_utils import add_list_to_message
from utils.message_utils import construct_message_best_of_veto_list
from utils.message_utils import construct_message_veto_list
from utils.message_utils import construct_vetoed_maps

load_dotenv()
TOKEN = os.getenv('TOKEN')

description = 'A bot https://github.com/tumaatti/discord-vetobot'

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix='!',
    description=description,
    intents=intents,
)

BANNED = []
PICKED = []

# VETO_RUNNING
# 0 - not running
# 1 - BO1 veto
# 3 - BO3 veto
# 5 - BO5 veto
# 10 - normal casual veto

VETO_RUNNING = 0

PLAYERS = []
VETOED = 0

MAPS = []


class Veto:
    def __init__(
        self,
        channel: str,
        server: str,
        veto_running: int,
        maps: List[str],
        players: List[object],
    ):
        self.maps = maps
        self.channel = channel
        self.server = server
        self.veto_running = veto_running
        self.vetoed = 0

    def add_veto(self, map, player):
        self.vetoed += 0


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
    global BANNED
    global PICKED
    global PLAYERS
    global VETO_RUNNING
    global VETOED
    VETO_RUNNING = 0
    VETOED = 0
    PLAYERS = []
    BANNED = []
    PICKED = []


def start_veto(ctx, users):
    global MAPS
    global PLAYER
    global VETO_RUNNING

    num_of_players = len(users)
    MAPS = [
        'anubis',
        'cache',
        'dust2',
        'inferno',
        'mirage',
        'nuke',
        'overpass',
        'train',
        'vertigo',
    ]

    if VETO_RUNNING:
        return 'veto already running! use !veto <map_name> to veto!'

    if num_of_players == 0:
        return 'gimme players'

    elif num_of_players > 5:
        return 'too many players'

    message = ''
    message = add_list_to_message(message, MAPS, [])
    message += '```\n\nVeto order:\n'

    VETO_RUNNING = 10
    for i in range(num_of_players):
        rnd = random.randint(0, num_of_players - 1)
        # original username: tumaatti#1111
        username = str(users.pop(rnd))
        if '#' in username:
            username, _ = username.split('#')
        PLAYERS.append(Player(username))
        num_of_players -= 1

    message += construct_message_veto_list(PLAYERS)
    message += '```'

    return message


def start_best_of_veto(ctx, users: List[str], num_of_maps: int):
    # system for BO1
    # maps: dust2, inferno, mirage, nuke, overpass, train, vertigo
    #       ban,   ban,     ban,    ban , ban,      ban,   decider
    #       0      1        2       3     4         5      6

    # system for BO3
    # maps: dust2, inferno, mirage, nuke, overpass, train, vertigo
    #       ban,   ban,     pick,   pick, ban,      ban,   decider
    #       0      1        2       3     4         5      6

    # system for BO5
    # maps: dust2, inferno, mirage, nuke, overpass, train, vertigo
    #       ban,   ban,     pick,   pick, pick,     pick,  decider
    #       0      1        2       3     4         5      6

    global PLAYERS
    global MAPS
    global VETO_RUNNING

    MAPS = [
        'dust2',
        'inferno',
        'mirage',
        'nuke',
        'overpass',
        'train',
        'vertigo',
    ]

    num_of_players = len(users)

    if VETO_RUNNING:
        return 'veto already running'

    if num_of_players != 2:
        return 'need 2 players for veto!'

    message = ''
    message = add_list_to_message(message, MAPS, [])
    message += '```\n\nVeto order:\n'

    VETO_RUNNING = num_of_maps
    rnd = random.randint(0, num_of_players - 1)
    starter = str(users.pop(rnd))
    second = str(users[0])
    if '#' in starter:
        starter, _ = starter.split('#')
        second, _ = second.split('#')

    PLAYERS = [
        Player(starter), Player(second),
        Player(starter), Player(second),
        Player(starter), Player(second),
    ]

    message += construct_message_best_of_veto_list(
        PLAYERS,
        MAPS,
        num_of_maps,
    )
    message += '```'

    return message


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


def casual_veto(vetomap, vetoer):
    global PLAYERS
    global BANNED
    global VETOED

    if (
        vetomap.lower().capitalize() in BANNED and
        PLAYERS[VETOED].vetotype == 'pick'
    ):
        return 'map banned'

    if vetoer == PLAYERS[VETOED].name.lower() and vetomap.lower() in MAPS:
        PLAYERS[VETOED].add_map(vetomap.lower())
        VETOED += 1

    picked = []
    BANNED = []
    for p in PLAYERS:
        if not p.mapveto:
            continue
        if p.vetotype == 'ban':
            BANNED.append(p.mapveto)
        elif p.vetotype == 'pick':
            picked.append(p.mapveto)

    banned_unique = list(set(BANNED))
    picked_unique = list(set(picked))
    bn = []
    if len(BANNED) != 0:
        for bu in list(banned_unique):
            if BANNED.count(bu) % 2 != 0:
                bn.append(bu)

    pn = []
    if len(picked) != 0:
        for pu in list(picked_unique):
            if picked.count(pu) % 2 != 0:
                pn.append(pu)
            else:
                pn.append(f'~~{pu.capitalize()}~~')

    message = ''
    message = add_list_to_message(message, MAPS, bn)
    message += '```\n\nVeto order:\n'
    message += construct_message_veto_list(PLAYERS)
    message += '```'
    message += construct_vetoed_maps(PLAYERS, bn, pn)

    return message


def best_of_veto(vetomap, vetoer):
    global BANNED
    global MAPS
    global PICKED
    global PLAYERS
    global VETOED

    if (
        vetomap.lower().capitalize() in BANNED or
        vetomap.lower().capitalize() in PICKED
    ):
        return 'map already selected'

    if vetoer == PLAYERS[VETOED].name.lower() and vetomap.lower() in MAPS:
        PLAYERS[VETOED].add_map(vetomap.lower())
        VETOED += 1

    BANNED = []
    PICKED = []
    for p in PLAYERS:
        if not p.mapveto:
            continue
        if p.vetotype == 'ban':
            BANNED.append(p.mapveto)
        elif p.vetotype == 'pick':
            PICKED.append(p.mapveto)

    vetos = copy.copy(BANNED)
    vetos.extend(PICKED)
    if len(vetos) == 6:
        tmp = copy.copy(MAPS)
        for i in vetos:
            if i.lower() in tmp:
                tmp.remove(i.lower())
        PICKED.append(tmp[0])

    message = ''
    message += add_list_to_message(message, MAPS, vetos)
    message += '```\n\nVeto order:\n'
    message += construct_message_best_of_veto_list(PLAYERS, MAPS, VETO_RUNNING)
    message += '```'
    message += construct_vetoed_maps(PLAYERS, BANNED, PICKED)

    return message


@bot.command(help='Veto on your turn')
async def veto(ctx, vetomap):
    global BANNED
    global PLAYERS
    global MAPS
    global VETOED
    global VETO_RUNNING

    if not VETO_RUNNING:
        await ctx.send('no active veto')
        return

    vetoer = str(ctx.author).lower()
    vetoer, _ = vetoer.split('#')

    if vetoer != PLAYERS[VETOED].name.lower():
        await ctx.send('incorrect vetoer')
        return

    if VETO_RUNNING == 10:
        message = casual_veto(vetomap, vetoer)
    else:
        message = best_of_veto(vetomap, vetoer)
    await ctx.send(message)
    if VETOED == len(PLAYERS):
        end_veto()


@bot.command(
    name='vetostart',
    pass_sontext=True,
    help='<user> <user> ... Start veto with discord usernames',
)
async def vetostart(ctx, *args: discord.User):
    users = list(args)
    message = start_veto(ctx, users)
    await ctx.send(message)


@bot.command(
    help='<voice channelname> Start veto with users in voice channel',
)
async def vetostartv(ctx, channel_name):
    voice_channel = discord.utils.get(
        ctx.guild.voice_channels,
        name=channel_name,
    )
    users = []
    for m in voice_channel.members:
        users.append(m.name)

    message = start_veto(ctx, users)
    await ctx.send(message)


@bot.command(help='<user> <user> Start veto for best of 3 series')
async def bo3(ctx, *args: discord.User):
    users = list(args)
    message = start_best_of_veto(ctx, users, 3)
    await ctx.send(message)


bot.run(TOKEN)
