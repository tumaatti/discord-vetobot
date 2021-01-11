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

# VETO_RUNNING CODES
# 0 - not running
# 1 - BO1 veto
# 3 - BO3 veto
# 5 - BO5 veto
# 10 - normal casual veto


class Player:
    def __init__(self, name: str):
        self.name = name
        self.mapveto = ''
        self.vetotype = ''

    def __str__(self):
        return f'{self.name} {self.mapveto}'

    def add_map(self, mapveto: str):
        self.mapveto = mapveto.capitalize()

    def set_vetotype(self, vetotype: str):
        self.vetotype = vetotype


class Veto:
    def __init__(
        self,
        channel: str,
        server: str,
        veto_running: int,
        maps: List[str],
        players: List[Player],
    ):
        self.maps = maps
        self.channel = channel
        self.server = server
        self.veto_running = veto_running
        self.players = players
        self.vetoed = 0
        self.banned_maps: List[str] = []
        self.picked_maps: List[str] = []

    def __str__(self):
        return (
            f'{self.channel} {self.server} '
            f'veto running: {self.veto_running} '
            f'vetoed: {self.vetoed}'
        )

    def add_veto(self):
        self.vetoed += 1


RUNNING_VETOS: List[Veto] = []
BANNED: List[str]
PICKED: List[str]


def end_veto(ctx):
    global RUNNING_VETOS

    for i, r in enumerate(RUNNING_VETOS):
        if r.channel == ctx.channel.name and r.server == ctx.guild.name:
            RUNNING_VETOS.pop(i)


def start_veto(ctx, users):
    global RUNNING_VETOS

    num_of_players = len(users)
    maps = [
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

    for i in RUNNING_VETOS:
        if i.channel == ctx.channel.name and i.server == ctx.guild.name:
            return 'veto already running!'

    if num_of_players == 0:
        return 'gimme players'

    elif num_of_players > 5:
        return 'too many players'

    message = ''
    message = add_list_to_message(message, maps, [])
    message += '```\n\nVeto order:\n'

    players: List[Player] = []
    for i in range(num_of_players):
        rnd = random.randint(0, num_of_players - 1)
        # original username: tumaatti#1111
        username = str(users.pop(rnd))
        if '#' in username:
            username, _ = username.split('#')
        players.append(Player(username))
        num_of_players -= 1

    veto = Veto(
        ctx.channel.name,
        ctx.guild.name,
        10,
        maps,
        players,
    )

    RUNNING_VETOS.append(veto)

    message += construct_message_veto_list(veto)
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

    global RUNNING_VETOS

    maps = [
        'dust2',
        'inferno',
        'mirage',
        'nuke',
        'overpass',
        'train',
        'vertigo',
    ]

    num_of_players = len(users)

    for i in RUNNING_VETOS:
        if i.channel == ctx.channel.name and i.server == ctx.guild.name:
            return 'veto already running on this channel'

    if num_of_players != 2:
        return 'need 2 players for veto!'

    message = ''
    message = add_list_to_message(message, maps, [])
    message += '```\n\nVeto order:\n'

    rnd = random.randint(0, num_of_players - 1)
    starter = str(users.pop(rnd))
    second = str(users[0])
    if '#' in starter:
        starter, _ = starter.split('#')
        second, _ = second.split('#')

    players = [
        Player(starter), Player(second),
        Player(starter), Player(second),
        Player(starter), Player(second),
    ]

    veto = Veto(
        ctx.channel.name,
        ctx.guild.name,
        num_of_maps,
        maps,
        players,
    )

    RUNNING_VETOS.append(veto)

    message += construct_message_best_of_veto_list(veto)
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
    end_veto(ctx)
    await ctx.send('veto aborted')


def casual_veto(veto, vetomap, vetoer):
    global RUNNING_VETOS

    if (
        vetomap.lower().capitalize() in veto.banned_maps and
        veto.players[veto.vetoed].vetotype == 'pick'
    ):
        return 'map banned'

    if (
        vetoer == veto.players[veto.vetoed].name.lower() and
        vetomap.lower() in veto.maps
    ):
        veto.players[veto.vetoed].add_map(vetomap.lower())
        veto.add_veto()

    picked = []
    picked_unique = []
    banned = []
    banned_unique = []
    for p in veto.players:
        if not p.mapveto:
            continue
        if p.vetotype == 'ban':
            if p.mapveto not in banned:
                banned_unique.append(p.mapveto)
            banned.append(p.mapveto)
        elif p.vetotype == 'pick':
            if p.mapveto not in picked:
                picked_unique.append(p.mapveto)
            picked.append(p.mapveto)

    veto.banned_maps = []
    if len(banned) != 0:
        for bu in banned_unique:
            if banned.count(bu) % 2 != 0:
                veto.banned_maps.append(bu)

    veto.picked_maps = []
    if len(picked) != 0:
        for pu in picked_unique:
            if picked.count(pu) % 2 != 0:
                veto.picked_maps.append(pu)
            else:
                veto.picked_maps.append(f'~~{pu.capitalize()}~~')

    message = ''
    message = add_list_to_message(message, veto.maps, veto.banned_maps)
    message += '```\n\nVeto order:\n'
    message += construct_message_veto_list(veto)
    message += '```'
    message += construct_vetoed_maps(veto)

    return message


def best_of_veto(veto, vetomap, vetoer):
    global RUNNING_VETOS

    if (
        vetomap.lower().capitalize() in veto.banned_maps or
        vetomap.lower().capitalize() in veto.picked_maps
    ):
        return 'map already selected'

    if (
        vetoer == veto.players[veto.vetoed].name.lower() and
        vetomap.lower() in veto.maps
    ):
        if vetomap in veto.maps:
            veto.players[veto.vetoed].add_map(vetomap.lower())
            veto.add_veto()
        else:
            return 'map not available'

    veto.banned_maps = []
    veto.picked_maps = []
    for p in veto.players:
        if not p.mapveto:
            continue
        if p.vetotype == 'ban':
            veto.banned_maps.append(p.mapveto)
        elif p.vetotype == 'pick':
            veto.picked_maps.append(p.mapveto)

    # on the last veto, add the map unbanned/unpicked map to picked list
    vetos = copy.copy(veto.banned_maps)
    vetos.extend(veto.picked_maps)
    if len(vetos) == 6:
        tmp = copy.copy(veto.maps)
        for i in vetos:
            if i.lower() in tmp:
                tmp.remove(i.lower())
        veto.picked_maps.append(tmp[0])

    message = ''
    message += add_list_to_message(message, veto.maps, vetos)
    message += '```\n\nVeto order:\n'
    message += construct_message_best_of_veto_list(veto)
    message += '```'
    message += construct_vetoed_maps(veto)

    return message


@bot.command(help='Veto on your turn')
async def veto(ctx, vetomap):
    global RUNNING_VETOS

    for i in RUNNING_VETOS:
        if i.channel == ctx.channel.name and i.server == ctx.guild.name:
            veto = i
            break
    else:
        await ctx.send('no active veto on this channel')
        return

    vetoer = str(ctx.author).lower()
    vetoer, _ = vetoer.split('#')

    if vetoer != veto.players[veto.vetoed].name.lower():
        await ctx.send('incorrect vetoer')
        return

    if veto.veto_running == 10:
        message = casual_veto(veto, vetomap, vetoer)
    else:
        message = best_of_veto(veto, vetomap, vetoer)
    await ctx.send(message)
    if veto.vetoed == len(veto.players):
        end_veto(ctx)


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
