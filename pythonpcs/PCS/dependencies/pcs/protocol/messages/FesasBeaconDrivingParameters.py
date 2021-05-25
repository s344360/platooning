from PCS.dependencies.pcs.protocol.messages.FesasBeacon import FesasBeacon

from typing import List, Dict

class FesasBeaconDrivingParameters(FesasBeacon):
    def __init__(self):
        FesasBeacon.__init__(self)
        self.lane: int = None
        self.velocity: int = None
        self.cacc: int = None
        self.leader_id: int = None
        self.front_id: int = None
        self.own_position: int = None
        self.platoon_id: int = None
        self.Faked_cacc: int = None
        self.vehicles_in_platoon: List = []
        self.joiner: int = None
        self.myDict: Dict = {}
        self.platoon_lane: int=None
        self.platoon_vehicles: List = []

