from typing import Dict


class VehicleInformation:
    def __init__(self, platoon_id: int, planned_lane: int, planned_velocity: float):
        self.platoon_id: int = platoon_id
        self.planned_lane: int = planned_lane
        self.planned_velocity: float = planned_velocity
        self.platoon_leader_id: str = None
        self.front_vehicle_id: str = None


# saves all vehicles in a dict: vehicle_id -> VehicleInformation
all_vehicles: Dict[str, VehicleInformation] = {}
