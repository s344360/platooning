from enum import Enum


class PlatooningCommandType(Enum):
    DRIVING_PARAMETERS = 1
    EXIT = 2
    LEAVE = 3
    JOIN = 4
    LEAD = 5
    ROUTE = 6
    PLATOON_UPDATE = 7
