from typing import Optional


import PCS.dependencies.pcs.logging.LogManager as LogManager
from PCS.dependencies.pcs.knowledge.exception.VehicleException import VehicleException
from PCS.dependencies.pcs.knowledge.exception.NoSuchVehicleException import NoSuchVehicleException
from PCS.dependencies.pcs.model.Vehicle import Vehicle
from PCS.dependencies.pcs.protocol.messages.FesasBeacon import FesasBeacon
from PCS.dependencies.pcs.protocol.messages.FesasBeaconCheckinReq import FesasBeaconCheckinReq
from PCS.dependencies.pcs.protocol.messages.FesasBeaconCheckoutReq import FesasBeaconCheckoutReq
from PCS.dependencies.pcs.protocol.messages.FesasBeaconStatus import FesasBeaconStatus
import PCS.dependencies.pcs.service.DataService as DataService
from PCS.dependencies.pcs.strategy.BasicDrivingStrategy import BasicDrivingStrategy
import PCS.logicElements.analyzer.pcs.AnalyzerLogic as AnalyzerLogic


logging_class: str = "MonitorLogic"
logger: LogManager.Logger = LogManager.get_logger(logging_class)


def call_logic(data):
    # check if the data is received in the right format
    if isinstance(data, FesasBeacon):
        logger.debug(0, "received data of type {}", [data.__class__.__name__])
        # process the beacon from Plexe
        affected_vehicle: Optional[int] = process_beacon(data)

        if affected_vehicle is not None:
            # forward to analyzer
            return AnalyzerLogic.call_logic(affected_vehicle)
        else:
            return 'no data'


def process_beacon(beacon: FesasBeacon) -> Optional[int]:
    """
    Processes an incoming beacon from Plexe
    :param beacon: The beacon of the process
    :return: the affected vehicle or None
    """
    if isinstance(beacon, FesasBeaconCheckinReq):
        return process_fesas_beacon_checkin_req(beacon)
    if isinstance(beacon, FesasBeaconCheckoutReq):
        return process_fesas_beacon_checkout_req(beacon)
    if isinstance(beacon, FesasBeaconStatus):
        return process_fesas_beacon_status(beacon)
    return None


def process_fesas_beacon_checkin_req(beacon: FesasBeaconCheckinReq):
    """
    Process a beacon from Plexe of type FesasBeaconCheckinReq
    :param beacon: The beacon of the process
    """
    vehicle_id: int = beacon.vehicle_id
    
    logger.debug(vehicle_id, "process checkin beacon, seqNo {}", [str(beacon.sequence_number)])

    # vehicle already checked in?
    if DataService.vehicle_exists(vehicle_id):
        raise VehicleException("Vehicle already checked in: " + str(vehicle_id))

    # perform checkin by creating vehicle data
    DataService.create_vehicle_from_beacon(beacon)

    # we do not want the analyzer to do something yet. Wait for the first status beacon!
    # Thus no vehicle is affected by the checkin request.
    return None


def process_fesas_beacon_checkout_req(beacon: FesasBeaconCheckoutReq) -> int:
    """
    Process a beacon from Plexe of type FesasBeaconCheckoutReq
    :param beacon: The beacon of the process
    :return: the affected vehicle
    """
    vehicle_id: int = beacon.vehicle_id

    try:
        vehicle: Vehicle = DataService.get_vehicle(vehicle_id)
        # make sure the vehicle is driving in BasicDrivingStrategy and is not part of a platoon.
        # If not, plan it (and leave a platoon e.g.)
        if not isinstance(vehicle.driving_strategy, BasicDrivingStrategy) \
                or vehicle.get_latest_position().platoon_id > 0:
            logger.info(vehicle_id, "plan checkout")
            # mark vehicle as checking out
            DataService.plan_checkout(vehicle_id)
    except NoSuchVehicleException:
        # already checked out
        pass

    return vehicle_id


def process_fesas_beacon_status(beacon: FesasBeaconStatus) -> Optional[int]:
    """
    Process a beacon from Plexe of type FesasBeaconStatus
    :param beacon: The beacon of the process
    :return: the affected vehicle or None (if no vehicle is affected)
    """
    vehicle_id: int = beacon.vehicle_id

    logger.debug(vehicle_id, "process status beacon, seqNo {}", [str(beacon.sequence_number)])
    if not DataService.is_checking_out(vehicle_id):
        try:
            DataService.update_vehicle_from_beacon(beacon)
            return vehicle_id
        except NoSuchVehicleException:
            # illegal vehicle id received / already checking out. Might happen due to network latency
            pass
    else:
        # vehicle is checking out. Will be controlled as long as its not in basic driving mode or the platoon_id
        # is not 0 which means that it is still part of a platoon
        try:
            vehicle: Vehicle = DataService.get_vehicle(vehicle_id)
            if not isinstance(vehicle.driving_strategy, BasicDrivingStrategy) \
                    or vehicle.get_latest_position().platoon_id > 0:
                return vehicle_id
            else:
                # vehicle is in basic driving mode and not part of a platoon. We can remove it now from the system.
                # Further beacons from the vehicle will be ignored (unless a checkin)
                DataService.delete_vehicle(vehicle_id)
                logger.info(vehicle_id, "vehicle checked out")
        except NoSuchVehicleException:
            # illegal vehicle id received / already checking out. Might happen due to network latency
            pass
    return None
