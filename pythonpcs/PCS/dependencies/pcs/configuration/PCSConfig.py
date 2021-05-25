"""
This class is a singleton which reads all configurable parameters from the
configuration file. It then provides methods for other components to access
these parameters
"""


from typing import List
from PCS.dependencies.pcs.model.VehiclePosition import VehiclePosition
import json
from pathlib import Path


# go back until pythonpcs in file directory
cwd = Path.cwd()
while str(cwd.name) != 'pythonpcs':
    cwd = cwd.parent
# load config.json into a dictionary
path_to_config = cwd / 'Config' / 'config.json'  # no slashes in path string -> correct os path separator
config = json.loads(open(path_to_config).read())


# assign values


# The ID of the PCS
pcs_id: str = config['id']

# The name of the corresponding highway
highway: str = config['highway']

# The IP address of the PCS
pcs_ip: str = config['ip']

# The port of the knowledge which awaits requests from the VRS
communication_knowledge_port: int = config['communicationKnowledgePort']

# An array of all sensor ports
sensor_ports: List[int] = config['sensorPorts']

# A position specifying the start of this PCS' segment
start: VehiclePosition = VehiclePosition()
start.pos_x = config['start']['x']
start.pos_y = config['start']['y']

# A position specifying the end of this PCS' segment
end: VehiclePosition = VehiclePosition()
end.pos_x = config['start']['x']
end.pos_y = config['start']['y']

# exits are not used

# The number of lanes
number_of_lanes: int = config['numberOfLanes']

# If vehicles are closer to another vehicle than this value, the PCS orchestrates overtaking
overtaking_distance_threshold: float = config['overtakingDistanceThreshold']

# The space in front of a vehicle on the lane to the right which needs to
# be free in order to change to the first lane
end_overtaking_distance_threshold_front: float = config['endOvertakingDistanceThresholdFront']

# The space behind a a vehicle on the lane to the right which needs to be
# free in order to change to the first lane
end_overtaking_distance_threshold_rear: float = config['endOvertakingDistanceThresholdRear']

# The speed range which is acceptable for platooning (e.g. the system only
# considers vehicles as platooning partners if their speed is in this range)
join_speed_range: float = config['joinSpeedRange']

# The distance range which is acceptable for platooning. The system only considers vehicles as
# potential platooning partners if their distance falls below this threshold value
join_distance_range: float = config['joinDistanceRange']

# The velocity used for overtaking (1.2 means that the overtaking vehicle
# will increase its speed by 20 percent)
overtake_velocity: float = config['overtakeVelocity']

# The velocity used to approach a platooning partner and to join its platoon
# (1.2 means that the overtaking vehicle will increase its speed by 20 percent)
join_speed: float = config['joinSpeed']

# The maximum allowed size of a platoon
max_platoon_size: int = config['maxPlatoonSize']

# The position where the PCS subsystem requests communication information
# of the subsequent subsystem for a vehicle
position_connect_to_next_pcs: VehiclePosition = VehiclePosition()
position_connect_to_next_pcs.pos_x = config['positionConnectToNextPcs']['x']
position_connect_to_next_pcs.pos_y = config['positionConnectToNextPcs']['y']

# The port used to communicate with the preceding PCS subsystem
port_connection_previous_pcs: int = config['portConnectionPreviousPcs']

# IP address of the next PCS subsystem
next_pcs_ip: str = config['nextPcsIp']

# Port of the next PCS subsystem
next_pcs_port: int = config['nextPcsPort']

# Specifies the managed resources used for this system. Use "PLEXE" for the
# platooning simulator PLEXE. Use "Lego" for Lego Mindstorms robots.
mr_type: str = config['mrType']

# Contains the absolute path to the SUMO road network xml file.
# This file contains information about the SUMO edges, lanes, junctions, and connections.
# The PCS requires this file for the PLEXE routing module.
# If the PCS is used without PLEXE, the user does not need to specify the path to the XML file.
path_to_sumo_network_file: str = config['pathToSumoNetworkFile']    # used - RoutingModule
