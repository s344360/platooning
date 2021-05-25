from typing import List


from PCS.dependencies.pcs.exception.DifferentLaneIndexException import DifferentLaneIndexException
from PCS.dependencies.pcs.exception.MapException import MapException
from PCS.dependencies.pcs.knowledge.VehicleKnowledge import VehicleKnowledge
from PCS.dependencies.pcs.knowledge.exception.NoSuchVehicleException import NoSuchVehicleException
from PCS.dependencies.pcs.model.Platoon import Platoon
from PCS.dependencies.pcs.model.Vehicle import Vehicle
from PCS.dependencies.pcs.model.VehicleMovement import VehicleMovement
from PCS.dependencies.pcs.model.VehicleParameter import VehicleParameter
from PCS.dependencies.pcs.model.VehiclePosition import VehiclePosition
from PCS.dependencies.pcs.model.Comparator import lane_position_comparator
from PCS.dependencies.pcs.model.sumo.Edge import Edge
from PCS.dependencies.pcs.model.sumo.Lane import Lane
from PCS.dependencies.pcs.navigation.PLEXE.NoPathFoundException import NoPathFoundException
from PCS.dependencies.pcs.navigation.PLEXE import PLEXE21RoutingModule as RoutingModule
from PCS.dependencies.pcs.protocol.messages.FesasBeaconCheckinReq import FesasBeaconCheckinReq
from PCS.dependencies.pcs.protocol.messages.FesasBeaconStatus import FesasBeaconStatus
from PCS.dependencies.pcs.strategy.BasicDrivingStrategy import BasicDrivingStrategy
from PCS.dependencies.pcs.strategy.DrivingStrategy import DrivingStrategy
from PCS.dependencies.pcs.strategy.FollowPlatoonStrategy import FollowPlatoonStrategy
from PCS.dependencies.pcs.strategy.JoinPlatoonStrategy import JoinPlatoonStrategy
from PCS.dependencies.pcs.utils.Time import Time


# service layer that is used to access and change vehicle data. Always use this service to edit vehicle data,
# never change the vehicle objects manually!


vehicles_checking_out: List[int] = []
vehicle_knowledge: VehicleKnowledge = VehicleKnowledge()


# import the data of a Vehicle from a FesasBeaconCheckinReq
def create_vehicle_from_beacon(beacon: FesasBeaconCheckinReq):
    vehicle_id: int = beacon.vehicle_id
    if vehicle_exists(vehicle_id):
        # remove old data
        delete_vehicle(vehicle_id)
    if beacon.desired_velocity <= 0:
        desired_velocity: int = 80
    else:
        desired_velocity: int = int(beacon.desired_velocity * 3.6)
    vehicle: Vehicle = Vehicle(vehicle_id, beacon.vehicle_type, desired_velocity)
    # set the initial driving strategy
    vehicle.driving_strategy = BasicDrivingStrategy(vehicle.vehicle_id, 80)

    # create initial position data
    vehicle_position: VehiclePosition = VehiclePosition()
    vehicle_position.pos_x = beacon.position_x
    vehicle_position.pos_y = beacon.position_y
    vehicle_position.lane_index = beacon.lane
    vehicle_position.lane_id = ""
    vehicle.add_position(vehicle_position)

    # create initial movement data
    vehicle_movement: VehicleMovement = VehicleMovement()
    vehicle.add_movement(vehicle_movement)

    vehicle.rsu = beacon.rsu

    # save new vehicle
    vehicle_knowledge.save_vehicle(vehicle)


# delete a vehicle from the system/ the knowledge
def delete_vehicle(vehicle_id: int):
    vehicle: Vehicle = get_vehicle(vehicle_id)

    # remove from platoon? Might happen that the vehicle is still part of a platoon if the leave is not performed well
    for platoon in PlatoonService.get_nearby_platoons(vehicle, 1000):
        for v in platoon.vehicles:
            if vehicle_id == v:
                PlatoonService.remove_from_platoon(platoon.platoon_id, vehicle_id)

    # delete vehicle
    vehicle_knowledge.delete_vehicle(vehicle_id)
    vehicles_checking_out.remove(vehicle_id)


# get a vehicle by its unique id
def get_vehicle(vehicle_id: int) -> Vehicle:
    return vehicle_knowledge.get_vehicle(vehicle_id)


# get a list of vehicles driving between two given
def get_vehicles_between(vehicle1: Vehicle, vehicle2: Vehicle) -> List[Vehicle]:
    if vehicle1.get_latest_position().lane_index is not vehicle2.get_latest_position().lane_index:
        raise DifferentLaneIndexException("unable to calculate vehicle distance between vehicle1 and vehicle2",
                                          vehicle1, vehicle2)
    if vehicle1.vehicle_id == vehicle2.vehicle_id:
        return []
    if not RoutingModule.is_behind(vehicle1, vehicle2):
        # switch vehicles (vehicle1 should be behind vehicle2)
        vehicle1, vehicle2 = vehicle2, vehicle1
    # if the vehicles are driving on the same lane, we can just check the vehicles driving on the same lane and
    # remove vehicles behind vehicle1 and in front of vehicle2
    if vehicle1.get_latest_position().lane_id == vehicle2.get_latest_position().lane_id:
        vehicle1_lane_position = vehicle1.get_latest_position().lane_position
        vehicle2_lane_position = vehicle2.get_latest_position().lane_position
        result = [x for x in get_vehicles_by_lane(vehicle1.get_latest_position().lane_id)
                  if vehicle1_lane_position < x.get_latest_position().lane_position < vehicle2_lane_position]
        return sorted(result, key=lane_position_comparator)

    # if the vehicles are not driving on the same lane, we need to collect all lanes
    # between the two vehicles and merge the vehicles there
    try:
        edges_between: List[Edge] = \
            RoutingModule.get_edges_between(RoutingModule.get_cur_edge(vehicle1), RoutingModule.get_cur_edge(vehicle2))
    except NoPathFoundException as e:
        raise MapException(repr(e))

    # extract lanes from the edges between the two vehicles
    lane_index = vehicle1.get_latest_position().lane_index
    lanes_between: List[Lane] = []
    for edge in edges_between:
        if len(edge.lanes) >= lane_index:
            lanes_between.append(edge.lanes[lane_index])
        else:
            # if there is a gap in the lane, abort operation. e.g. v1 and v2 driving on the lane index 3,
            # but part of the highway between the two vehicles only has 2 lanes instead of 3
            raise MapException("unable to find lanes between vehicle " + str(vehicle1.vehicle_id) + " and " +
                               str(vehicle2.vehicle_id) +
                               ": edge " + edge.edge_id + " has no lane with index " + str(lane_index))

    vehicles_between: List[Vehicle] = []

    # Part 1: add all vehicles between vehicle1 and the end of the current lane of vehicle1
    vehicle1_lane = RoutingModule.get_cur_lane(vehicle1)
    vehicle2_lane = RoutingModule.get_cur_lane(vehicle2)
    vehicle1_lane_position = vehicle1.get_latest_position().lane_position
    vehicle2_lane_position = vehicle2.get_latest_position().lane_position
    temp = [x for x in get_vehicles_by_lane(vehicle1_lane.lane_id)
            if vehicle1_lane_position < x.get_latest_position().lane_position]
    vehicles_between.extend(sorted(temp, key=lane_position_comparator))

    # Part 2: add all vehicles that are driving on the lanes between the current lane of vehicle1
    # and the current lane of vehicle2
    for lane in lanes_between:
        vehicles_between.extend(get_vehicles_by_lane(lane.lane_id))

    # Part 3: add all vehicles between the beginning of the current lane of vehicle2 and vehicle2 itself
    temp = [x for x in get_vehicles_by_lane(vehicle2_lane.lane_id)
            if x.get_latest_position().lane_position < vehicle2_lane_position]
    vehicles_between.extend(sorted(temp, key=lane_position_comparator))

    return vehicles_between


# get a list of all vehicles driving at a given lane
# returns the list of vehicles sorted in their driving order (last vehicle will be the first element)
def get_vehicles_by_lane(lane_id: str) -> List[Vehicle]:
    vehicle_list = [x for x in vehicle_knowledge.get_vehicles() if x.get_latest_position() is not None and
                    x.get_latest_position().lane_id == lane_id]
    return sorted(vehicle_list, key=lane_position_comparator)


# check whether or not a vehicle is currently checking out from the system
# returns true if the vehicle sent a checkout request before
def is_checking_out(vehicle_id: int) -> bool:
    return vehicle_id in vehicles_checking_out


# plan the adaption of a certain parameter
# vehicle_id = vehicle to adapt, parameter = the parameter to adapt, value = the new value of the parameter
def plan_adaption(vehicle_id: int, parameter: VehicleParameter, value):
    vehicle: Vehicle = vehicle_knowledge.get_vehicle(vehicle_id)
    vehicle.planned_adaptions[parameter] = value
    vehicle_knowledge.save_vehicle(vehicle)


# mark a vehicle for the checkout process
def plan_checkout(vehicle_id: int):
    if vehicle_id not in vehicles_checking_out:
        vehicles_checking_out.append(vehicle_id)


# plan a certain lane for a vehicle
def plan_lane(vehicle_id: int, lane: int):
    vehicle: Vehicle = vehicle_knowledge.get_vehicle(vehicle_id)
    if vehicle.get_latest_position() is None or vehicle.get_latest_position().lane_index is not lane:
        plan_adaption(vehicle_id, VehicleParameter.LANE, lane)


# plan all platoon parameters for a vehicle
# vehicle_id = the vehicle to adapt, platoon_id = the platoon of the vehicle
def plan_platoon(vehicle_id: int, platoon_id: int):
    if platoon_id == -1:
        # disable platooning for this vehicle
        plan_adaption(vehicle_id, VehicleParameter.PLATOON_ID, platoon_id)
        return
    platoon: Platoon = PlatoonService.get_platoon(platoon_id)
    if vehicle_id not in platoon.vehicles:
        PlatoonService.add_to_platoon(platoon_id, vehicle_id)
    plan_adaption(vehicle_id, VehicleParameter.PLATOON_ID, platoon_id)
    plan_adaption(vehicle_id, VehicleParameter.PLATOON_LEADER_ID, platoon.get_leader_id())
    plan_adaption(vehicle_id, VehicleParameter.PLATOON_OWN_POSITION, platoon.get_position(vehicle_id))
    plan_adaption(vehicle_id, VehicleParameter.PLATOON_FRONT_ID, platoon.get_front_id(vehicle_id))
    plan_adaption(vehicle_id, VehicleParameter.LANE, platoon.lane)
    if platoon.get_leader_id() == vehicle_id:
        plan_adaption(vehicle_id, VehicleParameter.VELOCITY, platoon.velocity)
        plan_adaption(vehicle_id, VehicleParameter.CACC, 0)
    else:
        plan_adaption(vehicle_id, VehicleParameter.VELOCITY, platoon.velocity + 5)
        plan_adaption(vehicle_id, VehicleParameter.CACC, 1)


# plan a certain speed for a vehicle (speed in km/h)
def plan_speed(vehicle_id: int, speed: int):
    vehicle: Vehicle = vehicle_knowledge.get_vehicle(vehicle_id)
    if vehicle.get_latest_movement() is None:
        plan_adaption(vehicle_id, VehicleParameter.VELOCITY, speed)
    else:
        if vehicle.get_latest_movement().velocity != speed:
            plan_adaption(vehicle_id, VehicleParameter.VELOCITY, speed)


# reset all planned adaptions for a certain vehicle
def reset_planned_adaption(vehicle_id: int):
    vehicle: Vehicle = vehicle_knowledge.get_vehicle(vehicle_id)
    vehicle.planned_adaptions.clear()
    vehicle_knowledge.save_vehicle(vehicle)


# change the driving strategy of a vehicle
def set_driving_strategy(vehicle_id: int, strategy: DrivingStrategy):
    vehicle: Vehicle = vehicle_knowledge.get_vehicle(vehicle_id)

    # check if strategy is valid
    if isinstance(strategy, JoinPlatoonStrategy):
        if isinstance(vehicle.driving_strategy, FollowPlatoonStrategy):
            # cannot switch to join strategy, leave current platoon first
            return
    if isinstance(strategy, BasicDrivingStrategy):
        if isinstance(vehicle.driving_strategy, FollowPlatoonStrategy):
            # cannot switch to basic driving strategy, leave current platoon first
            return

    # switch to new strategy and reset adaptions
    reset_planned_adaption(vehicle_id)
    vehicle.driving_strategy = strategy
    vehicle_knowledge.save_vehicle(vehicle)


def update_vehicle_from_beacon(beacon: FesasBeaconStatus):

    try:
        vehicle: Vehicle = get_vehicle(beacon.vehicle_id)
    except NoSuchVehicleException:
        # the checkin beacon seems to be not registered. Maybe, the beacon is lost because
        # of a high system load during the simulation. So we just create a fake checkin to fix this
        # (should be replaced with a reliable checkin protocol)
        vehicle: Vehicle = Vehicle(beacon.vehicle_id, "unknown", 80)
        set_driving_strategy(vehicle.vehicle_id, BasicDrivingStrategy(vehicle.vehicle_id, 80))

    # add a new position record
    vehicle_position: VehiclePosition = VehiclePosition()
    vehicle_position.time = beacon.current_time
    vehicle_position.pos_x = beacon.position_x
    vehicle_position.pos_y = beacon.position_y
    vehicle_position.lane_index = beacon.lane
    vehicle_position.lane_id = beacon.lane_id
    vehicle_position.lane_position = beacon.lane_position
    vehicle.add_position(vehicle_position)

    # add a new movement record
    vehicle_movement: VehicleMovement = VehicleMovement()
    vehicle_movement.time = beacon.current_time
    vehicle_movement.cruise_control = beacon.cruise_control
    vehicle_movement.velocity = beacon.current_velocity
    vehicle_movement.planned_velocity = beacon.planned_velocity
    vehicle.add_movement(vehicle_movement)

    vehicle.rsu = beacon.rsu

    # update sim time?
    if Time.simulation_time != beacon.current_time:
        Time.simulation_time = beacon.current_time

    # save changes
    vehicle_knowledge.save_vehicle(vehicle)


# check whether a vehicle exists
def vehicle_exists(vehicle_id: int) -> bool:
    try:
        return isinstance(vehicle_knowledge.get_vehicle(vehicle_id), Vehicle)
    except NoSuchVehicleException:
        return False


# Attention: cyclic imports
import PCS.dependencies.pcs.service.PlatoonService as PlatoonService