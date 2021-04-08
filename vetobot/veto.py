import copy
from typing import List
from typing import Tuple

from player import Player


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
                if p.mapveto not in picked and self.veto_running in (10, 20):
                    picked_unique.append(p.mapveto)
                picked.append(p.mapveto)

        return banned, picked, banned_unique, picked_unique

    def veto_map(self, vetomap, vetoer):
        if vetoer != self.players[self.vetoed].name.lower():
            return 'incorrect vetoer'

        if self.veto_running == 10 or self.veto_running == 20:
            if (
                vetomap.lower().capitalize() in self.banned_maps and
                self.players[self.vetoed].vetotype == 'pick'
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
            message = self.add_list_to_message(
                message, self.maps, self.banned_maps,
            )
            message += '```\n\nVeto order:\n'
            message += self.construct_message_veto_list()
            message += '```'
            message += self.construct_vetoed_maps()

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
            message += self.add_list_to_message(message, self.maps, vetos)
            message += '```\n\nVeto order:\n'
            message += self.construct_message_best_of_veto_list()
            message += '```'
            message += self.construct_vetoed_maps()

            return message

    def add_list_to_message(self, base: str, maps: List, bn: List) -> str:
        for i, m in enumerate(maps):
            banned = m.capitalize()
            if banned in bn:
                banned = f'~~{banned}~~'
            if i == len(maps) - 1:
                base += f'{banned}'
            else:
                base += f'{banned}, '

        return base

    def construct_message_veto_list(self) -> str:
        message = ''
        i = 0
        tmp = []
        for p in self.players:
            tmp.append(len(str(p.name)))

        max_p = max(tmp)
        for p in self.players:
            if i < len(self.players) - 3 and self.veto_running == 10:
                message += (
                    f"Ban:  {p.name} {(max_p - len(p.name)) * ' ' }"
                    f"{p.mapveto}\n"
                )
                p.set_vetotype('ban')
            else:
                message += (
                    f"Pick: {p.name} {(max_p - len(p.name)) * ' ' } "
                    f"{p.mapveto}\n"
                )
                p.set_vetotype('pick')
            i += 1

        return message

    def construct_message_best_of_veto_list(self) -> str:
        # MAP VETO memos for BoN
        # [0, 1] always ban
        # [2, 3] BO1: ban, BO3: Pick, BO5: Pick
        # [4, 5] BO1: ban, BO3: Ban,  BO5: Pick
        # [6]    BO1: dec, BO3: dec,  BO5: dec

        message = ''
        tmp = []
        for p in self.players[:1]:
            tmp.append(len(str(p.name)))

        max_p = max(tmp)
        for i in range(0, 6):
            if (
                (i in [0, 1]) or
                (i in [2, 3] and self.veto_running == 1) or
                (i in [4, 5] and self.veto_running in [1, 3])
            ):
                message += (
                    f'Ban:  {self.players[i].name} '
                    f"{(max_p - len(self.players[i].name)) * ' ' } "
                    f'{self.players[i].mapveto}\n'
                )
                self.players[i].set_vetotype('ban')

            else:
                message += (
                    f'Pick: {self.players[i].name} '
                    f"{(max_p - len(self.players[i].name)) * ' ' } "
                    f'{self.players[i].mapveto}\n'
                )
                self.players[i].set_vetotype('pick')

        return message

    def construct_vetoed_maps(self) -> str:
        message = ''
        if len(self.banned_maps) == 0:
            message += '\nBanned: --'
        else:
            message += self.add_list_to_message(
                '\nBanned: ', self.banned_maps, []
            )

        if len(self.picked_maps) == 0:
            message += '\nPicked: --'
        else:
            message += self.add_list_to_message(
                '\nPicked: ', self.picked_maps, []
            )

        return message
