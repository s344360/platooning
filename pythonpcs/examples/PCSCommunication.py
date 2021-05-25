import zmq
import json
import random
from plexe.vehicle_data import VehicleData
import ast
import plexe.position_helper as position_helper
from plexe import ACC, CACC, FAKED_CACC, RPM, GEAR, ACCELERATION, SPEED, POS_X, POS_Y
import math

sequence_number = 0


# Socket to talk to server (Server = PCS)
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5556")


# send status data to PCS and wait for the answer
def send_status_to_pcs(plexe):
    global sequence_number
    vid: int
    vehicle_information: position_helper.VehicleInformation
    for vid, vehicle_information in position_helper.all_vehicles.items():
        sequence_number += 1

        # gather vehicle data
        vehicle_data: VehicleData = plexe.get_vehicle_data(vid)
        planned_velocity = vehicle_information.planned_velocity
        if planned_velocity != -1:
            planned_velocity *= 3.6

        ac = plexe.get_active_controller(vid)
        if ac is 1:
            active_controller = "ACC"
        elif ac is 2:
            active_controller = "CACC"
        else:
            active_controller = "-1"

        data = {
            "messageType": "STATUS",
            "vehicleID": int(vid[2:]) + 1,  # cut off the first part of the String so there is only
                                            # the number of the vehicle left, not v.<number> and convert to int
                                            # and add +1 because the PCS vehicle indices start with 1
            "seqNo": sequence_number,
            "platoonID": vehicle_information.platoon_id,
            "currentVelocity": vehicle_data.speed * 3.6,
            "position": {"x": vehicle_data.pos_x, "y": vehicle_data.pos_y},
            "lane": plexe.get_lane_index(vid),   # traci.vehicle.getLaneIndex(key),
            "rsu": -1,   # default value
            "info": {
                "cruiseControl": active_controller,
                "laneID": plexe.get_lane_id(vid),    # traci.vehicle.getID(key),
                "lanePosition": plexe.get_lane_position(vid),   # traci.vehicle.getLanePosition(key),
                "currentTime": vehicle_data.time,
                "plannedLane": vehicle_information.planned_lane,
                "plannedVelocity": planned_velocity
            }
        }

        # Convert Vehicle Data (dict) to valid json
        json_data = json.dumps(data)

        # send outgoing_message and save the response in incoming_message
        socket.send_json(json_data)
        incoming_message = socket.recv_json()

        # handle incoming message
        if incoming_message != 'no data':
            for elements in incoming_message:
                beacon = ast.literal_eval(elements)
                handle_message_to_plexe(plexe, beacon)


# send checkin data to PCS and wait for the answer
def send_checkin_to_pcs(plexe):
    global sequence_number
    vid: int
    vehicle_information: position_helper.VehicleInformation
    for vid, vehicle_information in position_helper.all_vehicles.items():
        sequence_number += 1

        # gather vehicle data
        vehicle_data: VehicleData = plexe.get_vehicle_data(vid)

        data = {
            "messageType": "CHECKIN_REQ",
            "vehicleID": int(vid[2:]) + 1,  # cut off the first part of the String so there is only
                                            # the number of the vehicle left, not v.<number> and convert to int
                                            # and add +1 because the PCS vehicle indices start with 1
            "seqNo": sequence_number,
            "platoonID": vehicle_information.platoon_id,
            "currentVelocity": vehicle_data.speed * 3.6,
            "position": {"x": vehicle_data.pos_x, "y": vehicle_data.pos_y},
            "lane": plexe.get_lane_index(vid),
            "info": {
                "vehicleType": plexe.get_type_id(vid),
                "desiredVelocity": plexe.get_max_speed(vid) * 3.6 * 0.8     # * random.uniform(0.9, 1.1)
            }
        }

        # Convert Vehicle Data (dict) to valid json
        json_data = json.dumps(data)

        # send outgoing_message and save the response in incoming_message
        socket.send_json(json_data)
        socket.recv_json()


def handle_message_to_plexe(plexe, beacon):
    if beacon["messageType"] == "CHECKIN_ACK":
        # do nothing for now - doesn't happen at the moment
        pass
    elif beacon["messageType"] == "CHECKOUT_ACK":
        # do nothing for now - doesn't happen at the moment
        pass
    elif beacon["messageType"] == "COMMAND":
        if beacon["commandType"] == "DRIVING_PARAMETERS":
            # set speed
            # vehicle id -1 because Plexe indices start with 0, PCS starts with 1
            vehicle_id = "v." + str(int(beacon["vehicleID"])-1)
            speed = beacon["commandProperties"]["speed"]/3.6
            plexe.set_cc_desired_speed(vehicle_id, speed)
            position_helper.all_vehicles[vehicle_id].planned_velocity = speed
            # set lane
            if beacon["commandProperties"]["lane"] == -1:
                # let driver decide lane
                position_helper.all_vehicles[vehicle_id].planned_lane = -1
                plexe.enable_auto_lane_changing(vehicle_id, True)
            else:
                position_helper.all_vehicles[vehicle_id].planned_lane = beacon["commandProperties"]["lane"]
                plexe.enable_auto_lane_changing(vehicle_id, False)
                plexe.set_fixed_lane(vehicle_id, beacon["commandProperties"]["lane"])

            # set controller
            if beacon["commandProperties"]["cacc"] == 0:
                plexe.set_active_controller(vehicle_id, ACC)
                # vehicle is not using CACC -> no leader/front data needed for this vehicle

                position_helper.all_vehicles[vehicle_id].platoon_leader_id = None
                position_helper.all_vehicles[vehicle_id].front_vehicle_id = None

            else:
                plexe.set_active_controller(vehicle_id, CACC)
                # vehicle is using CACC -> leader/front data needed for feeding the CACC algorithm

                # get data about the leader vehicle and save it to the position helper
                leader_id = "v." + str(int(beacon["commandProperties"]["leaderID"]) - 1)
                position_helper.all_vehicles[vehicle_id].platoon_leader_id = leader_id

                # get data about the front vehicle and save it to the position helper
                front_id = "v." + str(int(beacon["commandProperties"]["frontID"])-1)
                position_helper.all_vehicles[vehicle_id].front_vehicle_id = front_id

            # save platoon data to the position helper
            position_helper.all_vehicles[vehicle_id].platoon_id = beacon["commandProperties"]["platoonID"]


"""
# testing area:

list = ['{"messageType": "COMMAND", "vehicleID": 7, "seqNo": 15, "rsuIDs": [-1], "commandType": "DRIVING_PARAMETERS", 
"commandProperties": {"lane": 1, "leaderID": 0, "frontID": 0, "ownPosition": 0, "speed": 129, "platoonID": 0, 
"dp_type": 0, "cacc": 0}}']

for elements in list:
    print(type(list))
    print(type(elements))
    edict = ast.literal_eval(elements)
    print(type(edict))
    print(edict["messageType"])
"""
