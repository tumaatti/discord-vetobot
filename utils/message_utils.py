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
