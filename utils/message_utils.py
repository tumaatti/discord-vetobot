from typing import List


def add_list_to_message(base: str, maps: List, bn: List):
    for i, m in enumerate(maps):
        banned = m.capitalize()
        if m.capitalize() in bn:
            banned = f'~~{m.capitalize()}~~'
        if i == len(maps) - 1:
            base += f'{banned}'
        else:
            base += f'{banned}, '

    return base


def construct_message_veto_list(PLAYERS):
    message = ''
    i = 0
    tmp = []
    for p in PLAYERS:
        tmp.append(len(str(p.name)))

    max_p = max(tmp)
    for p in PLAYERS:
        if i < len(PLAYERS) - 3:
            message += (
                f"Ban:  {p.name} {(max_p - len(p.name)) * ' ' } {p.mapveto}\n"
            )
            p.set_vetotype('ban')
        else:
            message += (
                f"Pick: {p.name} {(max_p - len(p.name)) * ' ' } {p.mapveto}\n"
            )
            p.set_vetotype('pick')
        i += 1

    return message


def construct_message_best_of_veto_list(PLAYERS, MAPS, num_of_maps):
    # MAP VETO memos for BoN
    # [0, 1] always ban
    # [2, 3] BO1: ban, BO3: Pick, BO5: Pick
    # [4, 5] BO1: ban, BO3: Ban,  BO5: Pick
    # [6]    BO1: dec, BO3: dec,  BO5: dec

    message = ''
    tmp = []
    for p in PLAYERS[:1]:
        tmp.append(len(str(p.name)))

    max_p = max(tmp)
    for i in range(0, 6):
        if (
            (i in [0, 1]) or
            (i in [2, 3] and num_of_maps == 1) or
            (i in [4, 5] and num_of_maps in [1, 3])
        ):
            message += (
                f"Ban:  {PLAYERS[i].name} "
                f"{(max_p - len(PLAYERS[i].name)) * ' ' } "
                f"{PLAYERS[i].mapveto}\n"
            )
            PLAYERS[i].set_vetotype('ban')
            # MAPS.remove(PLAYERS[i].mapveto.lower())

        else:
            message += (
                f"Pick: {PLAYERS[i].name} "
                f"{(max_p - len(PLAYERS[i].name)) * ' ' } "
                f"{PLAYERS[i].mapveto}\n"
            )
            PLAYERS[i].set_vetotype('pick')
            # MAPS.remove(PLAYERS[i].mapveto.lower())

    return message


def construct_vetoed_maps(PLAYERS, bn, pn):
    message = ''
    if len(bn) == 0:
        message += '\nBanned: --'
    else:
        message += add_list_to_message('\nBanned: ', bn, [])

    if len(pn) == 0:
        message += '\nPicked: --'
    else:
        message += add_list_to_message('\nPicked: ', pn, [])

    return message
