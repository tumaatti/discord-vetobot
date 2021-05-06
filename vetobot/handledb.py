import datetime
import sqlite3


class db:
    def __init__(self, name):
        self.name = name

    def createdb(self):
        con = sqlite3.connect(self)

        cur = con.cursor()
        tbl = '''\
            CREATE TABLE vetos (
            date text,
            server text,
            channel text,
            player text,
            mapveto text,
            vetotype text
            )
        '''
        cur.execute(tbl)
        con.commit()
        con.close()

    def write_data_to_db(self, veto):
        con = sqlite3.connect(self.name)
        cur = con.cursor()

        try:
            cur.execute('SELECT * FROM vetos')
        except sqlite3.OperationalError:
            db.createdb(self.name)

        today = datetime.date.today()

        date = f'{today.year}-{today.month}-{today.day}'
        server = veto.server
        channel = veto.channel

        for p in veto.players:
            player = p.name
            mapveto = p.mapveto
            vetotype = p.vetotype
            ins = (
                f'INSERT INTO vetos VALUES ('
                f"'{date}',"
                f"'{server}',"
                f"'{channel}',"
                f"'{player}',"
                f"'{mapveto}',"
                f"'{vetotype}'"
                f')'
            )
            cur.execute(ins)

        con.commit()
        con.close()
