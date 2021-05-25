import PCS.dependencies.pcs.logging.LogManager as LogManager
import PCS.dependencies.pcs.protocol.PLEXEProtocolConverter as Pcc
from PCS.dependencies.pcs.protocol.messages.FesasBeacon import FesasBeacon


logging_class: str = "EffectorLogic"
logger: LogManager.Logger = LogManager.get_logger(logging_class)


 


# It just needs to return the result of the previous layer converted with the Protocol Converter
# resulting in the SimpleSocket sending it back to the Plexe±
def call_logic(data):
    if isinstance(data, FesasBeacon):
        msg = Pcc.convert_beacon_to_plexe_protocol(data)
       
        logger.debug(data.vehicle_id, msg)
        
        return msg
    else:

        logger.error(0, "Received data in wrong format.")
        return 'no data'
