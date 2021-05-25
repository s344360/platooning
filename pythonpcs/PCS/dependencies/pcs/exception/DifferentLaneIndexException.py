from PCS.dependencies.pcs.model.Vehicle import Vehicle


class DifferentLaneIndexException(Exception):
    def __init__(self, message: str, vehicle1: Vehicle, vehicle2: Vehicle):
        super().__init__("vehicle " + str(vehicle1.vehicle_id) + " and " + str(vehicle2.vehicle_id) +
                         " do not drive on the same lane index. " + message)
