from typing import List


from PCS.dependencies.pcs.knowledge.PlatoonKnowledge import PlatoonKnowledge
from PCS.dependencies.pcs.knowledge.exception.NoSuchVehicleException import NoSuchVehicleException
from PCS.dependencies.pcs.model.Platoon import Platoon
from PCS.dependencies.pcs.model.Vehicle import Vehicle
import PCS.dependencies.pcs.navigation.PLEXE.PLEXE21RoutingModule as RoutingModule
from PCS.dependencies.pcs.navigation.PLEXE.NoPathFoundException import NoPathFoundException


platoon_knowledge: PlatoonKnowledge = PlatoonKnowledge()
next_available_platoon_id: int = 1


# add a vehicle to an existing platoon
def add_to_platoon(platoon_id: int, vehicle_id: int):
    platoon: Platoon = get_platoon(platoon_id)
    vehicle: Vehicle = VehicleService.get_vehicle(vehicle_id)
    if platoon.get_leader_id() != 0 \
            and RoutingModule.is_behind(vehicle, VehicleService.get_vehicle(platoon.get_leader_id())):
        # vehicle is behind leader -> join from back
        platoon.vehicles.append(vehicle_id)
    else:
        # vehicle is in front of leader -> join from front
        platoon.vehicles.insert(0, vehicle_id)
    save_platoon(platoon)


# create a new platoon with the next available id
# velocity = speed of the platoon in km/h, lane = the kane index to use for the platoon
# returns the new platoon
def create_platoon(velocity: int, lane: int) -> Platoon:
    platoon: Platoon = Platoon(next_available_platoon_id)
    platoon.velocity = velocity
    platoon.lane = lane
    platoon_knowledge.save_platoon(platoon)
    return platoon


# delete an existing platoon from the knowledge
def delete_platoon(platoon: Platoon):
    platoon_knowledge.delete_platoon(platoon)


# Get the current speed of a platoon (or 0 if the platoon is empty).
# This might vary from the planned speed of the platoon because of the current traffic situation.
def get_current_speed(platoon_id: int) -> int:
    platoon: Platoon = get_platoon(platoon_id)
    if platoon.is_empty():
        # platoon is empty, cannot determine platoon speed
        return 0
    else:
        # return the speed of the leader
        leader: Vehicle = VehicleService.get_vehicle(platoon.get_leader_id())
        return round(leader.get_latest_movement().velocity)


# get a list of all platoons within a certain radius
def get_nearby_platoons(vehicle: Vehicle, radius: float) -> List[Platoon]:
    platoons: List[Platoon] = []
    for platoon in platoon_knowledge.get_platoons():
        if not platoon.is_empty():
            check_platoon(platoon)
            leader: Vehicle = VehicleService.get_vehicle(platoon.get_leader_id())
            try:
                distance: float = abs(RoutingModule.calculate_distance(vehicle, leader))
                if distance < radius:
                    platoons.append(platoon)
            except NoPathFoundException:
                pass
    return platoons


# check the vehicles of a platoon. Removes unknown vehicles that left the system without a proper checkout process.
# This might happen if the route of a vehicle is not defined correctly.
def check_platoon(platoon: Platoon):
    for vehicle_id in platoon.vehicles:
        try:
            VehicleService.get_vehicle(vehicle_id)
        except NoSuchVehicleException:
            remove_from_platoon(platoon.platoon_id, vehicle_id)


# get a platoon by its unique id
def get_platoon(platoon_id: int) -> Platoon:
    return platoon_knowledge.get_platoon(platoon_id)


# remove a vehicle from a platoon
def remove_from_platoon(platoon_id: int, vehicle_id: int):
    platoon: Platoon = get_platoon(platoon_id)
    platoon.vehicles = [x for x in platoon.vehicles if x != vehicle_id]
    if platoon.is_empty():
        delete_platoon(platoon)
    else:
        save_platoon(platoon)


# save all changes made to a platoon
def save_platoon(platoon: Platoon):
    platoon_knowledge.save_platoon(platoon)


# Attention: cyclic imports
import PCS.dependencies.pcs.service.VehicleService as VehicleService