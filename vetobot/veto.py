import copy
from typing import List
from typing import Tuple

from _map import Map
from player import Player


class Veto:
    def __init__(
        self,
        channel: str,
        server: str,
        veto_running: int,
        maps: List[Map],
        players: List[Player],
    ):
        self.maps = maps
        self.channel = channel
        self.server = server
        self.veto_running = veto_running
        self.players = players
        self.vetoed = 0
        self.banned_maps: List[Map] = []
        self.picked_maps: List[Map] = []

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
        banned: List[str] = []

        for p in self.players:
            if not p.mapveto:
                continue
            if p.vetotype == 'ban':
                banned.append(p.mapveto)
            elif p.vetotype == 'pick':
                picked.append(p.mapveto)

        # remove duplicates from lists
        banned_unique = list(set(banned))
        picked_unique = list(set(picked))

        return banned, picked, banned_unique, picked_unique

    def veto_map(self, vetomap, vetoer):
        if vetoer != self.players[self.vetoed].name.lower():
            return 'incorrect vetoer'

        if self.veto_running in (10, 20):
            if (
                vetomap.lower().capitalize() in self.banned_maps and
                self.players[self.vetoed].vetotype == 'pick'
            ):
                return 'map banned'

            if (
                vetoer == self.players[self.vetoed].name.lower()
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
                        pu = pu.capitalize()
                        self.picked_maps.append(f'~~{pu}~~')

            message = self.add_list_to_message('', self.maps, self.banned_maps)
            message += self.construct_message_veto_list()
            message += self.construct_vetoed_maps()

            return message

        if (
            vetomap.lower().capitalize() in self.banned_maps or
            vetomap.lower().capitalize() in self.picked_maps
        ):
            return 'map already selected'

        if (
            vetoer == self.players[self.vetoed].name.lower()
        ):
            self.players[self.vetoed].add_map(vetomap.lower())
            self.vetoed += 1

        self.banned_maps, self.picked_maps, _, _ = self.sort_picks_and_bans()

        # on the last veto, add the last unbanned/unpicked map to picked list
        vetos = copy.copy(self.banned_maps)
        vetos.extend(self.picked_maps)
        if len(vetos) == 6:
            tmp = copy.copy(self.maps)
            for i in vetos:
                if i.lower() in tmp:
                    tmp.remove(i.lower())
            self.picked_maps.append(tmp[0])

        message = self.add_list_to_message('', self.maps, vetos)
        message += self.construct_message_best_of_veto_list()
        message += self.construct_vetoed_maps()

        return message

    def add_list_to_message(
        self, base: str, maps: List, banned_maps: List,
    ) -> str:
        for i, _map in enumerate(maps):
            _map = _map
            if _map in banned_maps:
                _map = f'~~{_map}~~'

            if i == len(maps) - 1:
                base += f'{_map}'
            else:
                base += f'{_map}, '

        return base

    def construct_message_veto_list(self) -> str:
        message = '```\n\nVeto order:\n'
        i = 0
        tmp = []
        for p in self.players:
            tmp.append(len(str(p.name)))

        max_p = max(tmp)
        for p in self.players:
            if i < len(self.players) - 3 and self.veto_running == 10:
                message += (
                    f"Ban:  {p.name} {(max_p - len(p.name)) * ' ' }"
                    f'{p.mapveto}\n'
                )
                # TODO: move set_vetotype out of message handling
                p.set_vetotype('ban')
            else:
                message += (
                    f"Pick: {p.name} {(max_p - len(p.name)) * ' ' } "
                    f'{p.mapveto}\n'
                )
                p.set_vetotype('pick')
            i += 1

        message += '```'

        return message

    def construct_message_best_of_veto_list(self) -> str:
        # MAP VETO memos for BoN
        # [0, 1] always ban
        # [2, 3] BO1: ban, BO3: Pick, BO5: Pick
        # [4, 5] BO1: ban, BO3: Ban,  BO5: Pick
        # [6]    BO1: dec, BO3: dec,  BO5: dec

        message = '```\n\nVeto order:\n'
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

        message += '```'

        return message

    def construct_vetoed_maps(self) -> str:
        if len(self.banned_maps) == 0:
            message = '\nBanned: --'
        else:
            message = self.add_list_to_message(
                '\nBanned: ', self.banned_maps, [],
            )

        if len(self.picked_maps) == 0:
            message += '\nPicked: --'
        else:
            message += self.add_list_to_message(
                '\nPicked: ', self.picked_maps, [],
            )

        return message
