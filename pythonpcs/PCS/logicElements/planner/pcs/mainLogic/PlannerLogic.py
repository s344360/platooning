import traceback


import PCS.dependencies.pcs.logging.LogManager as LogManager
from PCS.dependencies.pcs.model.Vehicle import Vehicle
from PCS.dependencies.pcs.strategy.BasicDrivingStrategy import BasicDrivingStrategy
from PCS.dependencies.pcs.strategy.LeavePlatoonStrategy import LeavePlatoonStrategy
from PCS.dependencies.pcs.strategy.JoinPlatoonStrategy import JoinPlatoonStrategy
from PCS.dependencies.pcs.strategy.FollowPlatoonStrategy import FollowPlatoonStrategy
from PCS.dependencies.pcs.strategy.CreatePlatoonStrategy import CreatePlatoonStrategy

import PCS.dependencies.pcs.service.DataService as DataService
import PCS.logicElements.planner.pcs.algorithm.BasicDrivingPlanner as BasicDrivingPlanner
import PCS.logicElements.planner.pcs.algorithm.platooning.CreatePlatoonPlanner as CreatePlatoonPlanner
import PCS.logicElements.planner.pcs.algorithm.platooning.FollowPlatoonPlanner as FollowPlatoonPlanner
import PCS.logicElements.planner.pcs.algorithm.platooning.JoinPlatoonPlanner as JoinPlatoonPlanner
import PCS.logicElements.planner.pcs.algorithm.platooning.LeavePlatoonPlanner as LeavePlatoonPlanner

import PCS.logicElements.executor.pcs.ExecutorLogic as ExecutorLogic



"""
The central planning logic which creates new plans to adjust the system state. Based on the analyzer data, 
this logic calls the correct high-level planning algorithms. Their results are later on composed in a single plan
"""


logging_class: str = "PlannerLogic"
logger: LogManager.Logger = LogManager.get_logger(logging_class)


def call_logic(data):
    vehicle: Vehicle = DataService.get_vehicle(data)
    logger.debug(vehicle.vehicle_id, "Vehicle {} follows {}", [str(vehicle.vehicle_id),
                                                              vehicle.driving_strategy.__class__.__name__])
    try:
        if isinstance(vehicle.driving_strategy, BasicDrivingStrategy):
            BasicDrivingPlanner.plan_adaption(vehicle)
        elif isinstance(vehicle.driving_strategy, CreatePlatoonStrategy):
            CreatePlatoonPlanner.plan_adaption(vehicle)
        elif isinstance(vehicle.driving_strategy, FollowPlatoonStrategy):
            FollowPlatoonPlanner.plan_adaption(vehicle)
        elif isinstance(vehicle.driving_strategy, JoinPlatoonStrategy):
            JoinPlatoonPlanner.plan_adaption(vehicle)
        elif isinstance(vehicle.driving_strategy, LeavePlatoonStrategy):
            LeavePlatoonPlanner.plan_adaption(vehicle)
        else:
            if vehicle.driving_strategy is None:
                strategy_type: str = "None"
            else:
                strategy_type: str = vehicle.driving_strategy.__class__.__name__
            logger.error(vehicle.vehicle_id, "unable to plan actions for vehicle, strategy type not supported: {}",
                         [strategy_type])
    except Exception:
        logger.error(vehicle.vehicle_id, "error while planning adaptation: {}", [traceback.format_exc()])
    return ExecutorLogic.call_logic(data)
