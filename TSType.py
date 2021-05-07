from enum import Enum, unique


@unique
class TSType(Enum):
    def __str__(self):
        return str(self.value)

    PROHIBICION = 1
    PELIGRO = 2
    STOP = 3
