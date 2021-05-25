from PCS.dependencies.pcs.model.Vehicle import Vehicle
import PCS.dependencies.pcs.service.DataService as DataService
from PCS.dependencies.pcs.strategy.BasicDrivingStrategy import BasicDrivingStrategy




"""
A planner implementation that can be used to plan adaptions for a BasicDrivingStrategy
"""


def plan_adaption(vehicle: Vehicle):
    """
    Plan adaptions for the given vehicle regarding BasicDrivingStrategy
    :param vehicle: the vehicle to adapt
    """
    driving_strategy: BasicDrivingStrategy = vehicle.driving_strategy

    if vehicle.get_latest_movement() is not None:
        # just drive at the desired speed and let the vehicles decide which lane to use
        DataService.plan_speed(vehicle.vehicle_id, driving_strategy.desired_velocity)
        DataService.plan_lane(vehicle.vehicle_id, -1)
