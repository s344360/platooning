from PCS.dependencies.pcs.protocol.messages.FesasBeacon import FesasBeacon


class FesasBeaconStatus(FesasBeacon):
    def __init__(self):
        FesasBeacon.__init__(self)
        self.current_velocity: float = None
        self.cruise_control: str = None
        self.current_time: int = None
        self.lane_id: str = None
        self.lane_position: float = None
        self.planned_lane: int = None
        self.planned_velocity: float = None
        self.lane: int = None
        self.platoon_id: int = None
        self.position_x: float = None
        self.position_y: float = None
