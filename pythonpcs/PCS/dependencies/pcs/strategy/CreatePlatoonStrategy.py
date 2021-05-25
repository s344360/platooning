from PCS.dependencies.pcs.strategy.DrivingStrategy import DrivingStrategy


# a strategy of a vehicle: vehicle should create a new platoon
class CreatePlatoonStrategy(DrivingStrategy):

    def __init__(self, vehicle_id: int, platoon_lane: int, platoon_velocity):
        super().__init__(vehicle_id)
        # target lane of the new platoon
        self.platoon_lane: int = platoon_lane
        # target velocity of the new platoon
        self.platoon_velocity: int = platoon_velocity

    def __str__(self):
        return "type: " + self.__class__.__name__ + ", platoon_velocity: " + str(self.platoon_velocity) + \
               ", platoon_lane: " + str(self.platoon_lane)
