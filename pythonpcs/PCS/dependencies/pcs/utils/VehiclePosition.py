# this class represents the position of a vehicle on the highway
class VehiclePosition:
    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y

    def __eq__(self, other) -> bool:
        if isinstance(other, VehiclePosition):
            return (self.y == other.y) and (self.x == other.x)
        else:
            return False
