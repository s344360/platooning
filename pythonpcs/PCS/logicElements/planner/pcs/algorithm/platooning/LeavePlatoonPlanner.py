import PCS.dependencies.pcs.logging.LogManager as LogManager
from PCS.dependencies.pcs.model.Vehicle import Vehicle
import PCS.dependencies.pcs.service.DataService as DataService
from PCS.dependencies.pcs.strategy.BasicDrivingStrategy import BasicDrivingStrategy
from PCS.dependencies.pcs.strategy.LeavePlatoonStrategy import LeavePlatoonStrategy


"""
A planner implementation used to plan adaptions for a LeavePlatoonStrategy
"""


logging_class: str = "LeavePlatoonPlanner"
logger: LogManager.Logger = LogManager.get_logger(logging_class)


def plan_adaption(vehicle: Vehicle):
    """
    Plan adaptions for the given vehicle regarding LeavePlatoonStrategy
    :param vehicle: the vehicle to adapt
    """
    strategy: LeavePlatoonStrategy = vehicle.driving_strategy

    logger.info(vehicle.vehicle_id, "perform platoon-leave")

    # remove the vehicle from the platoon
    DataService.remove_from_platoon(strategy.platoon_id, vehicle.vehicle_id)

    # switch to normal driving
    DataService.set_driving_strategy(vehicle.vehicle_id,
                                     BasicDrivingStrategy(vehicle.vehicle_id, vehicle.desired_velocity))
