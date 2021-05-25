from typing import List
import traceback


import PCS.dependencies.pcs.logging.LogManager as LogManager
from PCS.dependencies.pcs.model.Vehicle import Vehicle
from PCS.dependencies.pcs.model.VehicleParameter import VehicleParameter
import PCS.dependencies.pcs.protocol.messages.FesasBeacon as FesasBeacon
from PCS.dependencies.pcs.protocol.messages.FesasBeaconDrivingParameters import FesasBeaconDrivingParameters
import PCS.dependencies.pcs.service.DataService as DataService
import PCS.logicElements.effector.pcs.EffectorLogic as EffectorLogic


"""
It unregisters vehicles from the knowledge if they leave the segment.
"""

vehicles_in_platoon: List=[]
joiner: int = 0
myDict = {}
platoon_lane = 0
platoon_vehicles: List = []
logging_class: str = "ExecutorLogic"
logger: LogManager.Logger = LogManager.get_logger(logging_class)



def call_logic(data):
    vehicle: Vehicle = DataService.get_vehicle(data)
    beacons: List[FesasBeacon.FesasBeacon] = create_beacons(vehicle)
   
    if len(beacons) > 0:
        reply = []
        for beacon in beacons:
            logger.debug(vehicle.vehicle_id, "send beacon of type {}", [beacon.__class__.__name__])
            reply.append(EffectorLogic.call_logic(beacon))
        return reply
    else:
        return 'no data'


def create_beacons(vehicle: Vehicle) -> List[FesasBeacon.FesasBeacon]:
    beacons: List[FesasBeacon.FesasBeacon] = []
    if len(vehicle.planned_adaptions) > 0:
        d_p: FesasBeaconDrivingParameters = FesasBeaconDrivingParameters()
        beacons.append(d_p)
        d_p.rsu = vehicle.rsu
        d_p.vehicle_id = vehicle.vehicle_id
        d_p.sequence_number = FesasBeacon.last_sequence_number
        FesasBeacon.last_sequence_number += 1
        d_p.cacc = 0
        d_p.front_id = 0
        d_p.leader_id = 0
        d_p.own_position = 0
        d_p.platoon_id = 0
        d_p.velocity = vehicle.desired_velocity
        d_p.lane = -1
        d_p.vehicles_in_platoon= vehicles_in_platoon
        d_p.joiner = joiner
        d_p.myDict = myDict
        d_p.platoon_lane = platoon_lane
        d_p.platoon_vehicles = platoon_vehicles


        # adjust beacon by applying planned adaptions
        try:
            for key, value in vehicle.planned_adaptions.items():
                if key == VehicleParameter.VELOCITY:
                    d_p.velocity = int(value)
                elif key == VehicleParameter.LANE:
                    d_p.lane = int(value)
                elif key == VehicleParameter.PLATOON_FRONT_ID:
                    d_p.front_id = int(value)
                elif key == VehicleParameter.PLATOON_ID:
                    d_p.platoon_id = int(value)
                elif key == VehicleParameter.PLATOON_LEADER_ID:
                    d_p.leader_id = int(value)
                elif key == VehicleParameter.PLATOON_OWN_POSITION:
                    d_p.own_position = int(value)
                elif key == VehicleParameter.CACC:
                    d_p.cacc = int(value)
        except Exception:
            logger.error(vehicle.vehicle_id, "error: {}", [traceback.format_exc()])
    else:
        logger.debug(vehicle.vehicle_id, "no adaptions planned, skip sending beacon")

    return beacons


# test area


