class PlatooningPosition:
    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y

    def __eq__(self, other) -> bool:
        if isinstance(other, PlatooningPosition):
            return (self.y == other.y) and (self.x == other.x)
        else:
            return False
