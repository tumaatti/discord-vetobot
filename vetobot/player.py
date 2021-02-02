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
