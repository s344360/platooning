from PCS.dependencies.pcs.model.Vehicle import Vehicle
from PCS.dependencies.pcs.model.Platoon import Platoon
import PCS.dependencies.pcs.service.DataService as DataService
from PCS.dependencies.pcs.strategy.CreatePlatoonStrategy import CreatePlatoonStrategy
# from PCS.dependencies.pcs.strategy.FollowPlatoonStrategy import FollowPlatoonStrategy
from PCS.dependencies.pcs.strategy.JoinPlatoonStrategy import JoinPlatoonStrategy



"""
A planner implementation that can be used to plan adaptions for a CreatePlatoonStrategy
"""


def plan_adaption(vehicle: Vehicle):
    """
    Plan adaptions for the given vehicle regarding CreatePlatoonStrategy
    :param vehicle: the vehicle to adapt
    """
    strategy: CreatePlatoonStrategy = vehicle.driving_strategy

    # create platoon
    platoon: Platoon = DataService.create_platoon(strategy.platoon_velocity, strategy.platoon_lane)

    # switch to join strategy
    DataService.set_driving_strategy(vehicle.vehicle_id, JoinPlatoonStrategy(vehicle.vehicle_id, platoon.platoon_id))


