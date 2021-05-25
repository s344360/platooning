from typing import Optional
import traceback


import PCS.dependencies.pcs.logging.LogManager as LogManager
import PCS.logicElements.monitor.pcs.MonitorLogic as MonitorLogic
from PCS.dependencies.pcs.protocol.exception.FesasBeaconParseException import FesasBeaconParseException
from PCS.dependencies.pcs.protocol import PLEXEProtocolConverter as Pcc
from PCS.dependencies.pcs.protocol.messages.FesasBeacon import FesasBeacon


logging_class: str = "SensorLogic"
logger: LogManager.Logger = LogManager.get_logger(logging_class)


# SensorLogic does process the message so the next module can read the data
def call_logic(data):
    # check if data is in the right format
    if isinstance(data, str):
        beacon = process_message(data)
        if beacon is None:
            return 'no data'
        else:
            logger.debug(0, "forward beacon of type {}", [beacon.__class__.__name__])
            return MonitorLogic.call_logic(beacon)
    else:
        logger.error(0, "Received data not in correct format. Data: {}", [str(data)])
        return 'no data'


def process_message(message: str) -> Optional[FesasBeacon]:
    try:
        beacon: FesasBeacon = Pcc.convert_beacon_from_plexe_protocol(message)
    except FesasBeaconParseException:
        logger.warn(0, "unable to parse message from Plexe: {}", [traceback.format_exc()])
        return None
    if beacon:
        logger.debug(0, "received beacon of type {}", [beacon.__class__.__name__])
        return beacon
    else:
        return None

# testing
# print(call_logic("hi"))
