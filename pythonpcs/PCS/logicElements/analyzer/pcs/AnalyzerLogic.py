import importlib
import json
from pathlib import Path
from typing import Optional


import PCS.dependencies.pcs.logging.LogManager as LogManager
from PCS.dependencies.pcs.model.Vehicle import Vehicle
from PCS.dependencies.pcs.knowledge.exception.NoSuchVehicleException import NoSuchVehicleException
import PCS.dependencies.pcs.service.DataService as DataService
from PCS.dependencies.pcs.strategy.BasicDrivingStrategy import BasicDrivingStrategy
from PCS.dependencies.pcs.strategy.DrivingStrategy import DrivingStrategy
from PCS.dependencies.pcs.strategy.FollowPlatoonStrategy import FollowPlatoonStrategy
from PCS.dependencies.pcs.strategy.LeavePlatoonStrategy import LeavePlatoonStrategy
import PCS.logicElements.planner.pcs.mainLogic.PlannerLogic as PlannerLogic



logging_class: str = "AnalyzerLogic"
logger: LogManager.Logger = LogManager.get_logger(logging_class)


def load_strategy_planning_algorithm():
    """
    loading the right strategy planning algorithm based on a config file (json)
    :return: the module of the algorithm
    """
    # go back until pythonpcs in file directory
    cwd = Path.cwd()

    while str(cwd.name) != 'pythonpcs':
        cwd = cwd.parent
     
    # load config.json into a dictionary

    path_to_config = cwd / 'StrategyPlanningAlgorithms/algorithmConfig.json'
    
    config = json.loads(open(path_to_config).read())
    return importlib.import_module("StrategyPlanningAlgorithms.Algorithms." + str(config["algorithmName"]))


strategy_planning_algorithm = load_strategy_planning_algorithm()


def analyze_vehicle_strategy(vehicle_id: int) -> Optional[int]:
    """
    Analyze the strategy of a vehicle and adjust it if required.
    :param vehicle_id: The id of the Vehicle to process
    :return: the id of the vehicle if the strategy was changed
    """

   

    try:
        vehicle: Vehicle = DataService.get_vehicle(vehicle_id)
        
    except NoSuchVehicleException:
        # vehicle checked out and was already removed from the knowledge
        return None
    
    if "_noplatooning" in vehicle.vehicle_type:
        
        
        # do not analyze / plan anything for non-platooning vehicles, just assign basic driving
        if vehicle.driving_strategy is None:
             
            DataService.set_driving_strategy(vehicle.vehicle_id,
                                             BasicDrivingStrategy(vehicle.vehicle_id, vehicle.desired_velocity))
        else:
            # only send the strategy once, because it will never change for non-platoon vehicles
            # return None
            pass
    elif DataService.is_checking_out(vehicle_id):
        
        # The vehicle is trying to check out from the system. The goal of this process is a BasicDrivingStrategy for
        # the vehicle in order to allow a smooth, crash-free checkout. In this case we change the current strategy
        # in a way that we achieve such a basic driving strategy and do not use the selected platooning algorithm
        # for this vehicle anymore
        if isinstance(vehicle.driving_strategy, FollowPlatoonStrategy):
            # vehicle follows a platoon -> lets leave it
            DataService.set_driving_strategy(vehicle_id,
                                             LeavePlatoonStrategy(vehicle_id, vehicle.driving_strategy.platoon_id))
        else:
            # for all other strategies: just switch to basic driving (e.g. cancel a join process)
            DataService.set_driving_strategy(vehicle_id,
                                             BasicDrivingStrategy(vehicle_id, vehicle.desired_velocity))
    else:
  
        # execute the platooning algorithm
        new_strategy: DrivingStrategy = strategy_planning_algorithm.generate_strategy(vehicle)
        if new_strategy is not None:
            logger.debug(vehicle_id, "Vehicle {} follows new strategy: {}", [str(vehicle_id),
                                                                             new_strategy.__class__.__name__])
            DataService.set_driving_strategy(vehicle_id, new_strategy)
    return vehicle_id


def call_logic(data):
    affected_vehicle = analyze_vehicle_strategy(data)
    if affected_vehicle is None:
        return 'no data'
    else:
        return PlannerLogic.call_logic(affected_vehicle)
