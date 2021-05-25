from typing import List


import PCS.dependencies.pcs.logging.LogManager as LogManager
from PCS.dependencies.pcs.model.Vehicle import Vehicle
from PCS.dependencies.pcs.model.Platoon import Platoon
import PCS.dependencies.pcs.service.DataService as DataService
from PCS.dependencies.pcs.strategy.FollowPlatoonStrategy import FollowPlatoonStrategy
from PCS.dependencies.pcs.strategy.LeavePlatoonStrategy import LeavePlatoonStrategy
from PCS.dependencies.pcs.strategy.BasicDrivingStrategy import BasicDrivingStrategy


"""
A planner implementation for planning adaptions for a FollowPlatoonStrategy
"""


logging_class: str = "FollowPlatoonPlanner"
logger: LogManager.Logger = LogManager.get_logger(logging_class)


def plan_adaption(vehicle: Vehicle):
    """
    Plan adaptions for the give vehicle regarding FollowPlatoonStrategy
    :param vehicle: the vehicle to adapt
    """
    strategy: FollowPlatoonStrategy = vehicle.driving_strategy

    platoon: Platoon = DataService.get_platoon(strategy.platoon_id)

    # check if a platooning vehicle left the platoon lane (e.g. if it had to avoid a crash),
    # if yes make it leave the platoon
    if platoon.lane != vehicle.get_latest_position().lane_index:
        logger.info(vehicle.vehicle_id, "leave platoon because I left the platoon lane!")
        DataService.set_driving_strategy(vehicle.vehicle_id,
                                         LeavePlatoonStrategy(vehicle.vehicle_id, platoon.platoon_id))
        return

    # check for non-platooning vehicles within the platoon and stop platooning in this case to prevent crashes.
    # Otherwise, CACC will make a platooning-vehicle to crash into a non-platoon vehicle.
    # (This check is not required for the leader vehicle of the platoon.)
    if platoon.get_leader_id() != vehicle.vehicle_id:
        platoon_leader: Vehicle = DataService.get_vehicle(platoon.get_front_id(vehicle.vehicle_id))
        vehicles_between: List[Vehicle] = DataService.get_vehicles_between(vehicle, platoon_leader)
        if len(vehicles_between) > 0:
            bet: str = ""
            for v in vehicles_between:
                bet += str(v) + "; "
            logger.info(vehicle.vehicle_id, "leave platoon because there is a vehicle between me and the platoon! "
                                            "Vehicles between: {}", [bet])
            DataService.set_driving_strategy(vehicle.vehicle_id,
                                             LeavePlatoonStrategy(vehicle.vehicle_id, platoon.platoon_id))
            return

    # plan to follow the platoon
    DataService.plan_platoon(vehicle.vehicle_id, platoon.platoon_id)
