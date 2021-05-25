class VehiclePosition:
    def __init__(self):
        # time of this position data
        self.time: int = None
        # x-coordinate
        self.pos_x: float = None
        # y-coordinate
        self.pos_y: float = None
        # unique id of te current lane
        self.lane_id: str = None
        # index of the current lane (0 = very right lane), 1, 2, ...
        self.lane_index: int = None
        # position of the vehicle regarding the current lane
        self.lane_position: float = None
        # unique if of the platoon the vehicle is in
        self.platoon_id: int = None
        # index of the lane the PCS planned for this vehicle in the last step, -1 means the vehicle decides for itself
        self.planned_lane: int = None
