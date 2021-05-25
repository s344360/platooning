from PCS.dependencies.pcs.protocol.messages.FesasBeacon import FesasBeacon


class FesasBeaconCheckinReq(FesasBeacon):
    def __init__(self):
        FesasBeacon.__init__(self)
        self.current_velocity: float = None
        self.desired_velocity: float = None
        self.planned_velocity: float = None
        self.lane: int = None
        self.platoon_id: int = None
        self.position_x: float = None
        self.position_y: float = None
        self.vehicle_type: str = None
