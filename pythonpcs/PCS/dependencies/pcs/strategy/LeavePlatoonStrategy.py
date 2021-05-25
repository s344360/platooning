from PCS.dependencies.pcs.strategy.DrivingStrategy import DrivingStrategy


# a strategy for a vehicle: Leave the current platoon
class LeavePlatoonStrategy(DrivingStrategy):

    def __init__(self, vehicle_id: int, platoon_id: int):
        super().__init__(vehicle_id)
        # unique id of the platoon the vehicle should leave
        self.platoon_id: int = platoon_id

    def __str__(self):
        return "type: " + self.__class__.__name__
