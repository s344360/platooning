from enum import Enum


class PlatooningMessageType(Enum):
    CHECKIN_REQ = 1
    CHECKOUT_REQ = 2
    STATUS = 3
    UPDATE = 4
    CHECKIN_ACK = 5
    CHECKOUT_ACK = 6
    COMMAND = 7
