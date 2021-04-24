class Map:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f'{self.name.capitalize()}'

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return other.__str__().lower() == self.__str__().lower()
