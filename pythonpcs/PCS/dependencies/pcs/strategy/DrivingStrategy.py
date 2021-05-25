import time
from typing import Union



class DrivingStrategy:

    def __init__(self, vehicle_id: Union[int, str]):
        self.current_time = lambda: int(round(time.time() * 1000))
        # unique id of the vehicle that follows this strategy
        self.vehicle_id: int = int(vehicle_id)
        # timestamp when the strategy was started
        self.timestamp_create: int = self.current_time()
        # timestamp when the strategy will expire/the vehicle will give up on its current strategy
        # -1 for infinite strategies
        self.timestamp_expire: int = -1
        self.platoon_id: str = None
        # whether the vehicle that follows this strategy is catching up to an platoon or not
        self.is_catching_up: bool = None

    # whether the strategy is expired and should be changed or not
    # true is expired
    def is_expired(self) -> bool:
        if self.timestamp_expire == -1:
            return False
        if self.current_time() >= self.timestamp_expire:
            return True
        return False

    def set_lifetime(self, lifetime: int):
        self.timestamp_expire = self.timestamp_create + lifetime

    def __str__(self):
        return "type: " + self.__class__.__name__
