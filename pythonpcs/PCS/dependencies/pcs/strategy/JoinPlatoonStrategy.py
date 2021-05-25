from PCS.dependencies.pcs.strategy.DrivingStrategy import DrivingStrategy


# a strategy for a vehicle: join an existing platoon
class JoinPlatoonStrategy(DrivingStrategy):

    def __init__(self, vehicle_id: int, platoon_id: int):
        super().__init__(vehicle_id)
        # unique id of the platoon the vehicle should join
        self.platoon_id: int = platoon_id
        self.max_velocity: float = None
        self.set_lifetime(30000)

    def __str__(self):
        return "type: " + self.__class__.__name__ + ", platoon_id: " + str(self.platoon_id)
