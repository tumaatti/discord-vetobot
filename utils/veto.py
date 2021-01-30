import copy

from typing import List
from typing import Tuple

from utils.player import Player
from utils.message_utils import add_list_to_message
from utils.message_utils import construct_message_veto_list
from utils.message_utils import construct_message_best_of_veto_list
from utils.message_utils import construct_vetoed_maps


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

    def sort_picks_and_bans(self) -> (
        Tuple[List[str], List[str], List[str], List[str]]
    ):
        picked: List[str] = []
        picked_unique: List[str] = []

        banned: List[str] = []
        banned_unique: List[str] = []

        for p in self.players:
            if not p.mapveto:
                continue
            if p.vetotype == 'ban':
                if p.mapveto not in banned and self.veto_running == 10:
                    banned_unique.append(p.mapveto)
                banned.append(p.mapveto)
            elif p.vetotype == 'pick':
                if p.mapveto not in picked and self.veto_running == 10:
                    picked_unique.append(p.mapveto)
                picked.append(p.mapveto)

        return banned, picked, banned_unique, picked_unique

    def veto_map(self, vetomap, vetoer):
        if vetoer != self.players[self.vetoed].name.lower():
            return 'incorrect vetoer'

        if self.veto_running == 10:
            if (
                vetomap.lower().capitalize() in self.banned_maps and
                self.player[self.vetoed].vetotype == 'pick'
            ):
                return 'map banned'

            if (
                vetoer == self.players[self.vetoed].name.lower() and
                vetomap.lower() in self.maps
            ):
                self.players[self.vetoed].add_map(vetomap.lower())
                self.vetoed += 1

            (
                banned,
                picked,
                banned_unique,
                picked_unique,
            ) = self.sort_picks_and_bans()

            self.banned_maps = []
            if len(banned) != 0:
                for bu in banned_unique:
                    if banned.count(bu) % 2 != 0:
                        self.banned_maps.append(bu)

            self.picked_maps = []
            if len(picked) != 0:
                for pu in picked_unique:
                    if picked.count(pu) % 2 != 0:
                        self.picked_maps.append(pu)
                    else:
                        self.picked_maps.append(f'~~{pu.capitalize()}~~')

            message = ''
            message = add_list_to_message(message, self.maps, self.banned_maps)
            message += '```\n\nVeto order:\n'
            message += construct_message_veto_list(self)
            message += '```'
            message += construct_vetoed_maps(self)

            return message

        else:
            if (
                vetomap.lower().capitalize() in self.banned_maps or
                vetomap.lower().capitalize() in self.picked_maps
            ):
                return 'map already selected'

            if (
                vetoer == self.players[self.vetoed].name.lower() and
                vetomap.lower() in self.maps
            ):
                if vetomap in self.maps:
                    self.players[self.vetoed].add_map(vetomap.lower())
                    self.vetoed += 1
                else:
                    return 'map not in maps list'

            (
                self.banned_maps,
                self.picked_maps,
                _,
                _,
            ) = self.sort_picks_and_bans()

            # on the last veto, add the last unbanned/unpicked map to picked
            # list
            vetos = copy.copy(self.banned_maps)
            vetos.extend(self.picked_maps)
            if len(vetos) == 6:
                tmp = copy.copy(self.maps)
                for i in vetos:
                    if i.lower() in tmp:
                        tmp.remove(i.lower())
                self.picked_maps.append(tmp[0])

            message = ''
            message += add_list_to_message(message, self.maps, vetos)
            message += '```\n\nVeto order:\n'
            message += construct_message_best_of_veto_list(self)
            message += '```'
            message += construct_vetoed_maps(self)

            return message
