from PCS.dependencies.pcs.protocol.dataTypes.PlatooningPosition import PlatooningPosition
from typing import List


class PlatooningRoute:
    def __init__(self, route: List[PlatooningPosition] = None):
        if route is None:
            self.route: List[PlatooningPosition]
        else:
            self.route: List[PlatooningPosition] = route

    def add_platooning_position_to_route(self, position: PlatooningPosition):
        self.route.append(position)

    def contains_platooning_position(self, position: PlatooningPosition) -> bool:
        return position in self.route

    def delete_platooning_position_from_route(self, position: PlatooningPosition) -> bool:
        if position in self.route:
            self.route.remove(position)
            return True
        else:
            return False
