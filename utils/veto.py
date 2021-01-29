import List
import Tuple

from utils.player import Player


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

    def add_veto(self) -> Tuple[List[str], List[str], List[str], List[str]]:
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
