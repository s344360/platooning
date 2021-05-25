from typing import List, Union, Optional


from PCS.dependencies.pcs.model.Platoon import Platoon
from PCS.dependencies.pcs.knowledge.exception.NoSuchPlatoonException import NoSuchPlatoonException
from PCS.dependencies.pcs.model.Vehicle import Vehicle
import PCS.dependencies.pcs.service.DataService as DataService
from PCS.dependencies.pcs.strategy.BasicDrivingStrategy import BasicDrivingStrategy
from PCS.dependencies.pcs.strategy.CreatePlatoonStrategy import CreatePlatoonStrategy
from PCS.dependencies.pcs.strategy.DrivingStrategy import DrivingStrategy
from PCS.dependencies.pcs.strategy.JoinPlatoonStrategy import JoinPlatoonStrategy
from PCS.dependencies.pcs.strategy.FollowPlatoonStrategy import FollowPlatoonStrategy
from PCS.dependencies.pcs.strategy.LeavePlatoonStrategy import LeavePlatoonStrategy


def generate_strategy(vehicle: Vehicle) -> Optional[DrivingStrategy]:
    if isinstance(vehicle.driving_strategy, BasicDrivingStrategy):
        platoon: Platoon = find_best_platoon(vehicle)
        if platoon is None:
            if "truck" in vehicle.vehicle_type:
                platoon_speed: int = 70
                platoon_lane: int = 0
            else:
                platoon_speed: int = vehicle.desired_velocity
                platoon_lane: int = 1
            return CreatePlatoonStrategy(vehicle.vehicle_id, platoon_lane, platoon_speed)
        else:
            return JoinPlatoonStrategy(vehicle.vehicle_id, platoon.platoon_id)
    elif isinstance(vehicle.driving_strategy, FollowPlatoonStrategy):
        strategy: FollowPlatoonStrategy = vehicle.driving_strategy
        platoon: Platoon = DataService.get_platoon(strategy.platoon_id)
        if better_platoon_exists(vehicle, platoon):
            return LeavePlatoonStrategy(vehicle.vehicle_id, platoon.platoon_id)
    elif isinstance(vehicle.driving_strategy, JoinPlatoonStrategy):
        strategy: JoinPlatoonStrategy = vehicle.driving_strategy
        try:
            platoon: Platoon = DataService.get_platoon(strategy.platoon_id)
            if platoon.is_full() or better_platoon_exists(vehicle, platoon):
                return BasicDrivingStrategy(vehicle.vehicle_id, vehicle.desired_velocity)
        except NoSuchPlatoonException:
            return BasicDrivingStrategy(vehicle.vehicle_id, vehicle.desired_velocity)
#NEW SNETENCE
#    elif isinstance(vehicle.driving_strategy, JoinPlatoonInTheMiddleStrategy):
#        strategy: JoinPlatoonInTheMiddleStrategy = vehicle.driving_strategy
#        try:
#            platoon: Platoon = DataService.get_platoon(strategy.platoon_id)
#            if platoon.is_full() or better_platoon_exists(vehicle, platoon):
#                return BasicDrivingStrategy(vehicle.vehicle_id, vehicle.desired_velocity)
#        except NoSuchPlatoonException:
#            return BasicDrivingStrategy(vehicle.vehicle_id, vehicle.desired_velocity)
    return None


def find_best_platoon(vehicle: Vehicle) -> Union[Platoon, None]:
    platoons: List[Platoon] = DataService.get_nearby_platoons(vehicle, 1000.0)
    best_platoon = Platoon(-1)
    best_platoon.velocity = -1
    for platoon in platoons:        #nach Geschwindigkeit bester Platoon suchen
        if best_platoon.velocity < platoon.velocity <= vehicle.desired_velocity and not platoon.is_full():
            best_platoon = platoon
    if best_platoon.platoon_id == -1:
        return None
    else:
        return best_platoon


def better_platoon_exists(vehicle: Vehicle, old_platoon: Platoon) -> bool:

    if len(old_platoon.vehicles) > 1:
    
        return False
    platoons: List[Platoon] = DataService.get_nearby_platoons(vehicle, 1000.0)  # 1000
    best_platoon = Platoon(-1)
    best_platoon.velocity = -1
    for platoon in platoons:
        if best_platoon.velocity < platoon.velocity <= vehicle.desired_velocity and not platoon.is_full() \
                and platoon.platoon_id != old_platoon.platoon_id:
            best_platoon = platoon
    if best_platoon.platoon_id == -1:
        return False
    else:
        return True
