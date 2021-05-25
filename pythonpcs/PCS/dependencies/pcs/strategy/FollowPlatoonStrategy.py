from PCS.dependencies.pcs.strategy.DrivingStrategy import DrivingStrategy


class FollowPlatoonStrategy(DrivingStrategy):

    def __init__(self, vehicle_id: int, platoon_id: int):
        super().__init__(vehicle_id)
        # unique id of the platoon the vehicle should follow
        self.platoon_id: int = platoon_id

    def __str__(self):
        return "type: " + self.__class__.__name__ + ", platoon_id: " + str(self.platoon_id)
