import ast
import json

from typing import List


from PCS.dependencies.pcs.protocol.messages.FesasBeacon import FesasBeacon
from PCS.dependencies.pcs.protocol.messages.FesasBeaconCheckinReq import FesasBeaconCheckinReq
from PCS.dependencies.pcs.protocol.messages.FesasBeaconCheckoutReq import FesasBeaconCheckoutReq
from PCS.dependencies.pcs.protocol.messages.FesasBeaconDrivingParameters import FesasBeaconDrivingParameters
from PCS.dependencies.pcs.protocol.messages.FesasBeaconStatus import FesasBeaconStatus
from PCS.dependencies.pcs.protocol.exception.FesasBeaconParseException import FesasBeaconParseException
from PCS.dependencies.pcs.protocol.dataTypes.PlatooningMessageType import PlatooningMessageType
from PCS.dependencies.pcs.protocol.dataTypes.PlatooningCommandType import PlatooningCommandType


"""implements a communication protocol between PCS and Plexe"""


def convert_beacon_from_plexe_protocol(message: str) -> FesasBeacon:
    """
    convert a (json encoded) string received from Plexe into a FesasBeacon object
    :param message: the message to parse, json encoded
    :return: the parsed beacon
    """
    message_dict = ast.literal_eval(message)
    message_type_str = message_dict["messageType"]
    if message_type_str not in PlatooningMessageType.__members__:
        raise FesasBeaconParseException("unable to convert msg from Plexe, unknown message type: " + message_type_str)
    message_type = PlatooningMessageType[message_type_str]

    if message_type == PlatooningMessageType.CHECKIN_REQ:
        return parse_fesas_beacon_checkin_req(message_dict)
    elif message_type == PlatooningMessageType.CHECKOUT_REQ:
        return parse_fesas_beacon_checkout_req(message_dict)
    elif message_type == PlatooningMessageType.STATUS:
        return parse_status_beacon(message_dict)
    else:
        raise FesasBeaconParseException("message type not implemented yet: " + message_type)


def convert_beacon_to_plexe_protocol(beacon: FesasBeaconDrivingParameters) -> str:
    """
    Convert a FesasBeaconDrivingParameters object to a json encoded string
    :param beacon: the beacon to parse
    :return: json encoded string representing the beacon
    """
    message = {
        "messageType": "COMMAND",
        "vehicleID": beacon.vehicle_id,
        "seqNo": beacon.sequence_number,
        "rsuIDs": [beacon.rsu],
        "commandType": PlatooningCommandType.DRIVING_PARAMETERS.name,
        "commandProperties": {
            "lane": beacon.lane,
            "leaderID": beacon.leader_id,
            "frontID": beacon.front_id,
            "ownPosition": beacon.own_position,
            "speed": beacon.velocity,
            "platoonID": beacon.platoon_id,
            "dp_type": 0,
            "cacc": beacon.cacc,
            "vehicles": beacon.vehicles_in_platoon,
            "joiner": beacon.joiner,
            "myDict": beacon.myDict,
            "platoon_lane":beacon.platoon_lane,
            "platoon_vehicles":beacon.platoon_vehicles
        }
    }
    return json.dumps(message)


def parse_fesas_beacon_checkin_req(beacon: dict) -> FesasBeaconCheckinReq:
    """
    Parse a FesasBeaconCheckinReq object from a dict containing a parsed json string
    :param beacon: beacon: the beacon as a dict parsed from a json string
    :return: the beacon
    """
    o = FesasBeaconCheckinReq()
    o.vehicle_id = beacon["vehicleID"]
    o.sequence_number = beacon["seqNo"]
    o.current_velocity = beacon["currentVelocity"]
    o.desired_velocity = beacon["info"]["desiredVelocity"]
    o.lane = beacon["lane"]
    o.platoon_id = beacon["platoonID"]
    o.position_x = beacon["position"]["x"]
    o.position_y = beacon["position"]["y"]
    o.vehicle_type = beacon["info"]["vehicleType"]
    return o


def parse_fesas_beacon_checkout_req(beacon: dict) -> FesasBeaconCheckoutReq:
    """
    Parse a FesasBeaconCheckoutReq object from a dict containing a parsed json string
    :param beacon: beacon: the beacon as a dict parsed from a json string
    :return: the beacon
    """
    o = FesasBeaconCheckoutReq()
    o.vehicle_id = beacon["vehicleID"]
    o.sequence_number = beacon["seqNo"]
    return o


def parse_status_beacon(beacon: dict) -> FesasBeaconStatus:
    """
    Parse a FesasBeaconStatus object from a dict containing a parsed json string
    :param beacon: the beacon as a dict parsed from a json string
    :return: the beacon
    """
    o = FesasBeaconStatus()
    o.vehicle_id = beacon["vehicleID"]
    o.sequence_number = beacon["seqNo"]
    o.rsu = beacon["rsu"]
    o.current_velocity = beacon["currentVelocity"]
    o.current_time = beacon["info"]["currentTime"]
    o.lane = beacon["lane"]
    o.lane_id = beacon["info"]["laneID"]
    o.lane_position = beacon["info"]["lanePosition"]
    o.planned_lane = beacon["info"]["plannedLane"]
    o.cruise_control = beacon["info"]["cruiseControl"]
    o.planned_velocity = beacon["info"]["plannedVelocity"]
    o.platoon_id = beacon["platoonID"]
    o.position_x = beacon["position"]["x"]
    o.position_y = beacon["position"]["y"]
    return o

# testing

#   message1 = {
#        "messageType": "abb"
#   }


# import json

# message2 = {
#     "messageType": "STATUS"
# }
#   convert_beacon_from_plexe_protocol(message1)
# convert_beacon_from_plexe_protocol(json.dumps(message2))

'''
testing json parsing
print("dict: ")
print({"hi": [1, 2, 3], "hi2": {"hi3": 0}})
mes_json = json.dumps({"hi": [1, 2, 3], "hi2": {"hi3": 0}})
print("json: ")
print(mes_json)
mes_dict = ast.literal_eval(mes_json)
print("dict: some elements")
print(mes_dict["hi"][0])
print(mes_dict["hi2"]["hi3"])
'''
