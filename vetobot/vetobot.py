import argparse
import os
import random
from typing import List

import discord.utils
from discord.ext import commands
from dotenv import load_dotenv
from player import Player
from veto import Veto

load_dotenv()
TOKEN = os.getenv('TOKEN')
FUCK_NUKE = False

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
# 20 - normal casual veto with all picks


def end_veto(ctx):
    global RUNNING_VETOS

    for i, r in enumerate(RUNNING_VETOS):
        if r.channel == ctx.channel.name and r.server == ctx.guild.name:
            RUNNING_VETOS.pop(i)


def start_veto(ctx, users: List[discord.User], veto_type: int) -> str:
    global RUNNING_VETOS
    global FUCK_NUKE

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
    if FUCK_NUKE:
        maps.remove('nuke')

    for i in RUNNING_VETOS:
        if i.channel == ctx.channel.name and i.server == ctx.guild.name:
            return 'veto already running!'

    if num_of_players == 0:
        return 'gimme players'

    elif num_of_players > 5:
        return 'too many players'

    random.shuffle(users)
    players: List[Player] = []
    for u in users:
        players.append(Player(u))

    veto = Veto(
        ctx.channel.name,
        ctx.guild.name,
        veto_type,
        maps,
        players,
    )

    RUNNING_VETOS.append(veto)

    message = veto.add_list_to_message('', maps, [])
    message += veto.construct_message_veto_list()

    return message


def start_best_of_veto(
    ctx,
    users: List[discord.User],
    num_of_maps: int,
) -> str:
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

    random.shuffle(users)
    starter = users[0].name
    second = users[1].name

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

    message = veto.add_list_to_message('', maps, [])
    message += veto.construct_message_best_of_veto_list()

    return message


@bot.event
async def on_ready() -> None:
    print('Logged in as', bot.user)


@bot.command(help='Pong')
async def ping(ctx):
    await ctx.send('pong')


@bot.command(help='Abort current veto')
async def vetostop(ctx):
    end_veto(ctx)
    await ctx.send('veto aborted')


@bot.command(help='Veto on your turn')
async def veto(ctx, vetomap: str) -> None:
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

    if vetomap not in veto.maps:
        await ctx.send('map not in map pool')
        return

    message = veto.veto_map(vetomap, vetoer)
    await ctx.send(message)
    if veto.vetoed == len(veto.players):
        end_veto(ctx)


@bot.command(
    name='vetostart',
    pass_sontext=True,
    help='<user> <user> ... Start veto with discord usernames',
)
async def vetostart(ctx, *args: discord.User):
    tmp = list(args)
    users = []
    for u in tmp:
        users.append(u.name)
    message = start_veto(ctx, users, 10)
    await ctx.send(message)


@bot.command(
    name='vetostartp',
    pass_sontext=True,
    help='<user> <user> ... Start veto with discord usernames',
)
async def vetostartp(ctx, *args: discord.User):
    tmp = list(args)
    users = []
    for u in tmp:
        users.append(u.name)
    message = start_veto(ctx, users, 20)
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

    message = start_veto(ctx, users, 10)
    await ctx.send(message)


@bot.command(
    help=(
        '<voice channelname> Start veto with users in voice channel with '
        'all picks'
    ),
)
async def vetostartvp(ctx, channel_name):
    voice_channel = discord.utils.get(
        ctx.guild.voice_channels,
        name=channel_name,
    )
    users = []
    for m in voice_channel.members:
        users.append(m.name)

    message = start_veto(ctx, users, 20)
    await ctx.send(message)


@bot.command(help='<user> <user> Start veto for best of 1 series')
async def bo1(ctx, *args: discord.User):
    users = list(args)
    message = start_best_of_veto(ctx, users, 1)
    await ctx.send(message)


@bot.command(help='<user> <user> Start veto for best of 3 series')
async def bo3(ctx, *args: discord.User):
    users = list(args)
    message = start_best_of_veto(ctx, users, 3)
    await ctx.send(message)


@bot.command(help='<user> <user> Start veto for best of 5 series')
async def bo5(ctx, *args: discord.User):
    users = list(args)
    message = start_best_of_veto(ctx, users, 5)
    await ctx.send(message)

parser = argparse.ArgumentParser()
parser.add_argument(
    '--fucknuke',
    action='store_true',
    help='Remove Nuke from casual veto',
)
args = parser.parse_args()

if args.fucknuke:
    FUCK_NUKE = True

RUNNING_VETOS: List[Veto] = []

bot.run(TOKEN)
