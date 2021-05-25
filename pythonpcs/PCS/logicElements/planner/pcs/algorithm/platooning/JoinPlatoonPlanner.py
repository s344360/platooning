from typing import List, Dict
import traceback

import PCS.dependencies.pcs.logging.LogManager as LogManager
from PCS.dependencies.pcs.knowledge.exception.NoSuchPlatoonException import NoSuchPlatoonException
from PCS.dependencies.pcs.model.Vehicle import Vehicle
from PCS.dependencies.pcs.model.Platoon import Platoon
import PCS.dependencies.pcs.navigation.PLEXE.PLEXE21RoutingModule as RoutingModule
import PCS.dependencies.pcs.service.DataService as DataService
from PCS.dependencies.pcs.strategy.FollowPlatoonStrategy import FollowPlatoonStrategy
from PCS.dependencies.pcs.strategy.BasicDrivingStrategy import BasicDrivingStrategy
from PCS.dependencies.pcs.strategy.JoinPlatoonStrategy import JoinPlatoonStrategy
from PCS.dependencies.pcs.model.VehicleParameter import VehicleParameter
from PCS.dependencies.pcs.knowledge.VehicleKnowledge import VehicleKnowledge
from PCS.dependencies.pcs.strategy.JoinPlatoonStrategy import JoinPlatoonStrategy
from PCS.dependencies.pcs.strategy.LeavePlatoonStrategy import LeavePlatoonStrategy
from PCS.dependencies.pcs.strategy.BasicDrivingStrategy import BasicDrivingStrategy
from PCS.dependencies.pcs.knowledge.PlatoonKnowledge import PlatoonKnowledge
from PCS.dependencies.pcs.protocol.messages.FesasBeaconDrivingParameters import FesasBeaconDrivingParameters
import PCS.logicElements.executor.pcs.ExecutorLogic as ExecutorLogic
import PCS.logicElements.planner.pcs.algorithm.BasicDrivingPlanner as JoinPlatoonPlanner



from os import path
import sys

sys.path.append(path.abspath('/home/sestudent/pythonplexe-MP_Johannes/plexe/'))

"""
A planner implementation used for planning adaptions for a JoinPlatoonStrategy
"""

"""
Distance a vehicle needs to reach to the last vehicle of a platoon before joining (=switching to CACC) when the 
vehicle is driving in the same lane as the platoon. If this value is too large , the probability is high that there
is another car between the joining one and the platoon which will lead to error (-> abort the join process)
"""
join_distance_same_lane: int = 100  # 100
"""
Distance a vehicle needs to reach to the last vehicle of a platoon before joining (=switching to CACC) when the 
vehicle is driving in another lane as the platoon. If this value is too large , the probability is high that there
is another car between the joining one and the platoon which will lead to error (-> abort the join process)
"""

join_distance_different_lane: int = 100  # 100

logging_class: str = "JoinPlatoonPlanner"
logger: LogManager.Logger = LogManager.get_logger(logging_class)

joinMiddlecars: List[Vehicle] = []
myDict = {}
test = 1

def plan_adaption(vehicle: Vehicle):

    strategy: JoinPlatoonStrategy = vehicle.driving_strategy
    try:
        platoon: Platoon = DataService.get_platoon(strategy.platoon_id)

        logger.debug(vehicle.vehicle_id, "Trying to join platoon {}", [str(strategy.platoon_id)])
        if platoon.is_empty():
            # if the platoon is empty, the vehicle can just "join" the platoon
            if vehicle.get_latest_position().lane_index == platoon.lane:
                # right now
                plan_join(vehicle, platoon)
                return
            else:
                # change lane first
                DataService.plan_lane(vehicle.vehicle_id, platoon.lane)
                DataService.plan_speed(vehicle.vehicle_id, platoon.velocity)
                return

        # calculate the distance between vehicle and platoon -> catchup or join?
        leader: Vehicle = DataService.get_vehicle(platoon.get_leader_id())
        platoon_end: Vehicle = DataService.get_vehicle(platoon.get_last_id())

        if RoutingModule.is_behind(vehicle, platoon_end):
            distance: float = RoutingModule.calculate_distance(vehicle, platoon_end)
            distance = abs(distance)
            logger.info(vehicle.vehicle_id, "distance to platoon end: {}m, platoon lane: {}, vehicle lane: {}",
                        [str(distance), str(platoon.lane), str(vehicle.get_latest_position().lane_index)])
            if platoon.lane != vehicle.get_latest_position().lane_index:
                logger.debug(vehicle.vehicle_id, "planJoinFromBackAndDifferentLane")
                #print("it's done 1",vehicle.vehicle_id)
                plan_join_from_back_and_different_lane(vehicle, platoon, platoon_end, distance)
            else:
                logger.debug(vehicle.vehicle_id, "planJoinFromBackAndSameLane")
                #print("it's done",vehicle.vehicle_id)
                plan_join_from_back_and_same_lane(vehicle, platoon, platoon_end, distance)
        elif RoutingModule.is_behind(vehicle, leader):
            distance_end: float = abs(RoutingModule.calculate_distance(vehicle, platoon_end))
            distance_leader: float = abs(RoutingModule.calculate_distance(vehicle, leader))
            logger.info(vehicle.vehicle_id, "Vehicle is between platoon end and platoon leader")
            logger.info(vehicle.vehicle_id, "distance to platoon end: {}m, distance to platoon leader: {}m, "
                                            "platoon lane: {}, vehicle lane: {}",
                        [str(distance_end), str(distance_leader), str(platoon.lane),
                         str(vehicle.get_latest_position().lane_index)])

            handle_in_between_position2(vehicle, platoon)

            #handle_in_between_position(vehicle, platoon)

        else:
            distance: float = RoutingModule.calculate_distance(vehicle, leader)
            distance = abs(distance)
            logger.info(vehicle.vehicle_id, "distance to platoon leader: {}m, platoon lane: {}, vehicle lane: {}",
                        [str(distance), str(platoon.lane), str(vehicle.get_latest_position().lane_index)])
            if platoon.lane != vehicle.get_latest_position().lane_index:
                logger.debug(vehicle.vehicle_id, "planJoinFromFrontAndDifferentLane")

                plan_join_from_front_and_different_lane(vehicle, platoon, leader, distance)
            else:
                logger.debug(vehicle.vehicle_id, "planJoinFromFrontAndSameLane")
                plan_join_from_front_and_same_lane(vehicle, platoon, leader, distance)

        ExecutorLogic.platoon_vehicles = platoon.vehicles

        return
    except NoSuchPlatoonException:
        logger.info(vehicle.vehicle_id, "abort join, platoon has been removed from the system")
    except Exception:
        logger.error(vehicle.vehicle_id, "unable to plan join adaption: {}", [traceback.format_exc()])

    logger.debug(vehicle.vehicle_id, "unable to join this platoon, switch to basic driving")
    DataService.set_driving_strategy(vehicle.vehicle_id,
                                     BasicDrivingStrategy(vehicle.vehicle_id, vehicle.desired_velocity))


def handle_in_between_position2(vehicle: Vehicle, platoon: Platoon):
    vehicle_is_in_myDict(vehicle,platoon)

    if vehicle.get_latest_position().lane_index > platoon.lane:
        update_message_sent_to_PCSComunnication(vehicle,platoon)

    elif vehicle.get_latest_position().lane_index < platoon.lane:
        update_message_sent_to_PCSComunnication(vehicle,platoon)

    else:
        logger.warn(vehicle.vehicle_id, "Vehicle is in between the platoon - just join it")
        plan_join(vehicle, platoon)


def update_message_sent_to_PCSComunnication(vehicle: Vehicle, platoon:Platoon):
    JoinPlatoonPlanner.test = 1
    for vehicle3 in joinMiddlecars:
        if vehicle3 == vehicle:
            JoinPlatoonPlanner.test = 0; break

    join_in_the_middle_vehicls(vehicle)

    if (JoinPlatoonPlanner.test == 1):
        vehicle.planned_adaptions[VehicleParameter.CACC] = 2  # in PCSCommunication 3 case for joinMiddle
        ExecutorLogic.vehicles_in_platoon = platoon.vehicles
        ExecutorLogic.joiner = vehicle.vehicle_id - 1
        find_right_position_in_platoon(vehicle, platoon)
        ExecutorLogic.myDict = myDict
        ExecutorLogic.platoon_lane = platoon.lane


#in case there is a vehicle on the right side of the platoon and another
# vehicle on the left side of the platoon then the second joiner should wait
def vehicle_is_in_myDict(vehicle: Vehicle,platoon:Platoon):
    index=0
    for key in myDict:
        index+=1
        if (vehicle.vehicle_id == int(key)):
            break
    for key in myDict:
        index-=1
        if(index==1):
            vehicle2 = DataService.get_vehicle(int(key))
            if (vehicle.get_latest_position().lane_index) == 2:
                if (vehicle2.get_latest_position().lane_index) <platoon.lane:
                    DataService.plan_speed(vehicle.vehicle_id, DataService.get_current_speed(platoon.platoon_id) + 15)
                    break

#find the right position in platoon and save it
def find_right_position_in_platoon(vehicle: Vehicle, platoon: Platoon):
    for i in range(1, len(platoon.vehicles)):
        if RoutingModule.is_behind(DataService.get_vehicle(platoon.vehicles[i]), vehicle):
            myDict[vehicle.vehicle_id] = [i,i-1]
            break


# save vehicles which wanna join platoon in the middle in a List
def join_in_the_middle_vehicls(vehicle: Vehicle):
    vehicle3: Vehicle

    test = 1
    if len(joinMiddlecars) == 0:
        joinMiddlecars.insert(0, vehicle)
    for vehicle3 in joinMiddlecars:
        if vehicle3 == vehicle:
            test = 0
            break

    if (test == 1):
        length = len(joinMiddlecars)
        joinMiddlecars.insert(length, vehicle)


def handle_in_between_position(vehicle: Vehicle, platoon: Platoon):
    if vehicle.get_latest_position().lane_index > platoon.lane:
        logger.info(vehicle.vehicle_id, "Vehicle is left to the platoon it wants to join - overtake platoon")
        DataService.plan_lane(vehicle.vehicle_id, platoon.lane + 1)
        DataService.plan_speed(vehicle.vehicle_id, DataService.get_current_speed(platoon.platoon_id) + 10)
    elif vehicle.get_latest_position().lane_index < platoon.lane:
        logger.info(vehicle.vehicle_id, "Vehicle is right to the platoon it wants to join - fall behind platoon")
        DataService.plan_lane(vehicle.vehicle_id, platoon.lane - 1)
        DataService.plan_speed(vehicle.vehicle_id, DataService.get_current_speed(platoon.platoon_id) - 5)
    else:
        logger.warn(vehicle.vehicle_id, "Vehicle is in between the platoon - just join it")
        plan_join(vehicle, platoon)


def plan_catchup(vehicle: Vehicle, platoon: Platoon, distance: float):
    """
    Plan the catchup process to a platoon.
    :param vehicle: The vehicle to adapt.
    :param platoon: The platoon to catch up to.
    :param distance: The current distance between the vehicle and the platoon
    """
    logger.info(vehicle.vehicle_id, "plan catchup")
    # plan speed depending on distance
    speed_dif: int = 30
    if distance < 200:
        speed_dif = 15
        if distance < 100:
            speed_dif = 10
            if distance < 50:
                speed_dif = 5
    DataService.plan_lane(vehicle.vehicle_id, -1)
    DataService.plan_speed(vehicle.vehicle_id, DataService.get_current_speed(platoon.platoon_id) + speed_dif)


def plan_fallback(vehicle: Vehicle, platoon: Platoon, distance: float):
    """
    Plan a fall back maneuver to join a platoon
    :param vehicle: The vehicle to adapt.
    :param platoon: The platoon to join.
    :param distance: The distance between the vehicle and the platoon.
    """
    logger.info(vehicle.vehicle_id, "plan fallback")
    # plan speed difference depending on distance
    speed_diff: int = 15
    if distance < 200:
        speed_diff = 10
        if distance < 100:
            speed_diff = 5
            if distance < 50:
                speed_diff = 3
    DataService.plan_lane(vehicle.vehicle_id, -1)
    speed: int = DataService.get_current_speed(platoon.platoon_id) - speed_diff
    speed = max(60, speed)  # drive min 60 on highways
    DataService.plan_speed(vehicle.vehicle_id, speed)

def plan_join(vehicle: Vehicle, platoon: Platoon):
    """
    Plan the join process of a vehicle.
    :param vehicle: The Vehicle to adapt.
    :param platoon: The platoon to join.
    """
    logger.info(vehicle.vehicle_id, "plan join")
    DataService.plan_platoon(vehicle.vehicle_id, platoon.platoon_id)
    DataService.set_driving_strategy(vehicle.vehicle_id, FollowPlatoonStrategy(vehicle.vehicle_id, platoon.platoon_id))

def plan_join_from_back_and_different_lane(vehicle: Vehicle, platoon: Platoon, platoon_end: Vehicle, distance: float):
    """
    Plan a join process if the vehicle is behind the platoon and driving on a different lane index.
    :param vehicle: The vehicle to adapt.
    :param platoon: The platoon to join.
    :param platoon_end: The last vehicle of the platoon.
    :param distance: The current distance between the vehicle and the platoon.
    """
    if distance > join_distance_different_lane:  # or distance < 5
        logger.debug(vehicle.vehicle_id, "distance {} too large for join, wait.. (max: {})",
                     [str(distance), str(join_distance_different_lane)])
        plan_catchup(vehicle, platoon, distance)
        return

    # if DataService.is_lane_change_safe(vehicle.vehicle_id, platoon.lane):
    # set speed to a little less than the platoon speed and try to switch lane to the platoons lane
    DataService.plan_speed(vehicle.vehicle_id, platoon.velocity - 5)
    DataService.plan_lane(vehicle.vehicle_id, platoon.lane)
    logger.debug(vehicle.vehicle_id, "fall back with low delta and tay to change to platoon lane")

def plan_join_from_back_and_same_lane(vehicle: Vehicle, platoon: Platoon, platoon_end: Vehicle, distance: float):
    """
    Plan a join process if the vehicle is behind the platoon and driving on the same lane index
    :param vehicle: The vehicle to adapt.
    :param platoon: The platoon to join.
    :param platoon_end: The last vehicle of the platoon.
    :param distance: The current distance between the vehicle and the platoon
    """
    if distance > join_distance_same_lane:
        # distance too big
        logger.debug(vehicle.vehicle_id, "distance {} too large for join, wait.. (max: {})",
                     [str(distance), str(join_distance_same_lane)])
        plan_catchup(vehicle, platoon, distance)
        return

    # check for vehicles between the platoon and the vehicle
    logger.debug(vehicle.vehicle_id, "list vehicles between vehicle and platoon...")
    vehicles_between: List[Vehicle] = DataService.get_vehicles_between(vehicle, platoon_end)
    if len(vehicles_between) == 0:
        logger.debug(vehicle.vehicle_id, "no vehicles between vehicle and platoon, start join")
        plan_join(vehicle, platoon)
    else:
        # there is a vehicle between the platoon and the join vehicle. Continue catchup...
        # This will lead the vehicle to try to overtake the vehicle or join from front
        logger.debug(vehicle.vehicle_id, "{} vehicles between vehicle and platoon, continue catchup",
                     [str(len(vehicles_between))])
        plan_catchup(vehicle, platoon, distance)

def plan_join_from_front_and_different_lane(vehicle: Vehicle, platoon: Platoon,
                                            platoon_leader: Vehicle, distance: float):
    """
    Plan a join process if the vehicle is driving in front of the platoon and on a different lane index.
    :param vehicle: The vehicle to adapt.
    :param platoon: The platoon to join.
    :param platoon_leader: The leading vehicle of the platoon.
    :param distance: The distance between vehicle and platoon.
    """
    if distance > join_distance_different_lane:
        # distance too big
        logger.debug(vehicle.vehicle_id, "distance {} too large for join, wait..", [str(distance)])
        plan_fallback(vehicle, platoon, distance)
        return

    # set the speed to a little more than the platoon and try to switch lane to the platoons lane
    DataService.plan_speed(vehicle.vehicle_id, platoon.velocity + 5)
    DataService.plan_lane(vehicle.vehicle_id, platoon.lane)
    logger.debug(vehicle.vehicle_id, "catch up with low delta and tay to change to platoon lane")

def plan_join_from_front_and_same_lane(vehicle: Vehicle, platoon: Platoon, platoon_leader: Vehicle, distance: float):
    """
    Plan a join process if the vehicle is driving in front of the platoon and on the same lane index.
    :param vehicle: The vehicle to adapt.
    :param platoon: The platoon to join.
    :param platoon_leader: The leading vehicle of the platoon.
    :param distance: The distance between vehicle and platoon.
    """
    if distance > join_distance_same_lane:
        # distance too big
        logger.debug(vehicle.vehicle_id, "distance {} too large for join, wait..", [str(distance)])
        plan_fallback(vehicle, platoon, distance)
        return

    # check for vehicles between the platoon and the vehicle
    vehicles_between: List[Vehicle] = DataService.get_vehicles_between(vehicle, platoon_leader)
    if len(vehicles_between) == 0:
        print("ich war hier + vehicle id",vehicle.vehicle_id)

        logger.debug(vehicle.vehicle_id, "no vehicles between vehicle and platoon, start join")
        plan_join(vehicle, platoon)
    else:
        # There is a vehicle between the platoon and the join vehicle. Continue fall back...
        # This will hopefully lead the vehicle in between to overtake the vehicle
        # so there is space for joining the platoon.
        logger.debug(vehicle.vehicle_id, "{} vehicles between vehicle and platoon, continue fallback",
                     [str(len(vehicles_between))])
        plan_fallback(vehicle, platoon, distance)


