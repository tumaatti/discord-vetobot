from typing import List


def add_list_to_message(base: str, maps: List):
    for i, m in enumerate(maps):
        if i == len(maps) - 1:
            base += f'{m.capitalize()}'
        else:
            base += f'{m.capitalize()}, '

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


def construct_vetoed_maps(PLAYERS):
    banned = []
    banned_unique = []
    picked = []
    picked_unique = []
    for p in PLAYERS:
        if not p.mapveto:
            continue
        if p.vetotype == 'ban':
            banned.append(p.mapveto)
        elif p.vetotype == 'pick':
            picked.append(p.mapveto)

    banned_unique = list(set(banned))
    picked_unique = list(set(picked))

    print('picked unique: ', picked_unique)
    print('banned unique: ', banned_unique)
    if len(picked_unique) != 0:
        print(picked.count(picked_unique[0]))

    # TODO: miten saa yliviivattua noi mitkä ei oo enää käytössä:
    # ~~yliviivattu~~

    message = '\n'
    if len(banned) != 0:
        message += add_list_to_message('\nBanned: ', banned)
    if len(picked) != 0:
        message += add_list_to_message('\nPicked: ', picked)

    return message
