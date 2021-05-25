from PCS.dependencies.pcs.strategy.DrivingStrategy import DrivingStrategy


# a strategy for a vehicle: Just follow the highway, no platooning
class BasicDrivingStrategy(DrivingStrategy):

    def __init__(self, vehicle_id: int, desired_velocity: int):
        super().__init__(vehicle_id)
        self.desired_velocity: int = desired_velocity

    def __str__(self):
        return "type: " + self.__class__.__name__ + ", desired velocity: " + str(self.desired_velocity)


# test area
"""
b = BasicDrivingStrategy(1, 1)
print(str(b))
"""
