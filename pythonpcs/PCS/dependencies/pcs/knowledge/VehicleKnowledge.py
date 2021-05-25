from typing import List, Dict


from PCS.dependencies.pcs.model.Vehicle import Vehicle
from PCS.dependencies.pcs.knowledge.exception.NoSuchVehicleException import NoSuchVehicleException
from PCS.dependencies.pcs.knowledge.exception.VehicleException import VehicleException


# knowledge that holds vehicle data, should only be accessed via a DataService
class VehicleKnowledge:
    def __init__(self):
        self.vehicles: Dict[int, Vehicle] = {}

    # delete a vehicle from the knowledge
    def delete_vehicle(self, vehicle_id: int):
        try:
            del self.vehicles[vehicle_id]
        except KeyError:
            print("Key not found")

    # get a vehicle by its unique ID or throw a NoSuchValueException if now vehicle was found
    def get_vehicle(self, vehicle_id: int) -> Vehicle:
        if vehicle_id in self.vehicles:
            return self.vehicles[vehicle_id]
        else:
            raise NoSuchVehicleException(str(vehicle_id))

    # get the list of all stored vehicles
    def get_vehicles(self) -> List[Vehicle]:
        return list(self.vehicles.values())

    # save a vehicle in the knowledge
    def save_vehicle(self, vehicle: Vehicle):
        # print("save vehicle: " + str(vehicle))
        if vehicle.vehicle_id <= 0:     # | vehicle.vehicle_id in self.vehicles:
            # do not accept vehicles without a unique id > 0
            raise VehicleException("illegal vehicle id")
        else:
            self.vehicles[vehicle.vehicle_id] = vehicle
