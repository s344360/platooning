from typing import Dict, Optional, List
from pathlib import Path
import xml.etree.ElementTree as ET
import traceback


import PCS.dependencies.pcs.logging.LogManager as LogManager
from PCS.dependencies.pcs.configuration import PCSConfig
from PCS.dependencies.pcs.exception.MapException import MapException
from PCS.dependencies.pcs.model.Vehicle import Vehicle
from PCS.dependencies.pcs.model.sumo.Edge import Edge
from PCS.dependencies.pcs.model.sumo.Lane import Lane
from PCS.dependencies.pcs.navigation.PLEXE.NoPathFoundException import NoPathFoundException


logging_class: str = "PLEXE21RoutingModule"
logger: LogManager.Logger = LogManager.get_logger(logging_class)


# calculate the distance between two vehicles
# returns the distance in meters, NoPathFoundException if no path exists between the two vehicles
def calculate_distance(vehicle1: Vehicle, vehicle2: Vehicle) -> float:
    """
    Calculate the distance between vehicle1 and vehicle2
    :param vehicle1: vehicle 1
    :param vehicle2: vehicle 2
    :return: distance in meters, NoPathFoundException if no path exists between the two vehicles
    """
    # if vehicle2 is behind vehicle1, return distance * -1
    if not is_behind(vehicle1, vehicle2):
        if is_behind(vehicle2, vehicle1):
            return calculate_distance(vehicle2, vehicle1) * -1
        else:
            raise NoPathFoundException("unable to calculate distance between vehicles, no path exists between them")

    e1: Edge = get_cur_edge(vehicle1)
    e2: Edge = get_cur_edge(vehicle2)
    if not e1 or not e2:
        raise NoPathFoundException("unable to calculate path, at least one vehicle is not located in any known edge.")
    if e1.edge_id == e2.edge_id:
        # vehicles are using the same lane, just calculate their distance based on their position within lane
        logger.info(vehicle1.vehicle_id, "in same edge: v1 {} v2 {}", [
            str(vehicle1.get_latest_position().lane_position), str(vehicle2.get_latest_position().lane_position)])
        return vehicle2.get_latest_position().lane_position - vehicle1.get_latest_position().lane_position

    # vehicles are driving in different lanes
    distance: float = 0
    # (1) add the distance between vehicle1 and the end of its current lane
    vehicle1_lane: Lane = get_cur_lane(vehicle1)
    distance += vehicle1_lane.length - vehicle1.get_latest_position().lane_position
    # (2) add the length of all edges/lanes that are between the two vehicles
    for edge in get_edges_between(get_cur_edge(vehicle1), get_cur_edge(vehicle2)):
        # it should not make a big difference which lane is used
        # for the distance calculation, so we just use the very right one
        distance += edge.lanes[0].length
    # (3) add the distance between vehicle2 and the start of its current lane
    distance += vehicle2.get_latest_position().lane_position

    logger.info(vehicle1.vehicle_id, "not in same lane, v2 {}, v1 {}, between {}", [
        str(vehicle2.get_latest_position().lane_position),
        str(vehicle1_lane.length - vehicle1.get_latest_position().lane_position),
        str(distance - (vehicle1_lane.length - vehicle1.get_latest_position().lane_position) -
            vehicle2.get_latest_position().lane_position)])

    return distance


# get the current Edge a Vehicle is driving in
# None if the Vehicle is not part of any Edge
def get_cur_edge(vehicle: Vehicle) -> Optional[Edge]:
    if vehicle.get_latest_position() is None:
        # no position data stored about this vehicle
        return None
    for edge in edges.values():
        if edge.contains_lane(vehicle.get_latest_position().lane_id):
            return edge
    return None


# get the current Lane a Vehicle is driving at
# None if the Vehicle is not part of any Lane
def get_cur_lane(vehicle: Vehicle) -> Optional[Lane]:
    edge = get_cur_edge(vehicle)
    if edge is None:
        return None
    else:
        return edge.lanes[vehicle.get_latest_position().lane_index]


# get a list of all edges between two other edges
# returns all edges between start and end, NoPathFoundException if no path exists from the start to the target edge
def get_edges_between(start: Edge, end: Edge) -> List[Edge]:
    path: List[Edge] = []
    if start is None or end is None or start.edge_id == end.edge_id: return path
    if len(start.get_connected_edges()) == 0:
        # dead end found
        raise NoPathFoundException('now path found from edge ' + start.edge_id + ' to ' + end.edge_id)
    for curEdge in start.get_connected_edges():
        try:
            path = path + get_edges_between(curEdge, end)
            path.append(curEdge)
        except NoPathFoundException as e:
            raise e
    path.remove(start)
    path.remove(end)
    return path


# get a lane by its unique id
def get_lane(lane_id: str) -> Lane:
    for edge in edges.values():
        for lane in edge.lanes:
            if lane_id == lane.lane_id:
                return lane
    raise MapException("no such lane: " + lane_id)


def is_behind(vehicle1: Vehicle, vehicle2: Vehicle) -> bool:
    """
    Check whether vehicle 1 is behind vehicle 2
    :param vehicle1: vehicle 1
    :param vehicle2: vehicle 2
    :return: false if vehicle 1 is not behind vehicle 2
    """
    try:
        path: List[Edge] = get_edges_between(get_cur_edge(vehicle1), get_cur_edge(vehicle2))
        if not path:
            e1: Edge = get_cur_edge(vehicle1)
            e2: Edge = get_cur_edge(vehicle2)
            if not e1 or not e2:
                raise NoPathFoundException("unable to calculate path, at least one vehicle is not located "
                                           "in any known edge.")
            if e1.edge_id == e2.edge_id:
                # they are in the same edge -> compare position to get approximated result
                # assuming that all lanes have the same length
                return vehicle1.get_latest_position().lane_position < \
                       vehicle2.get_latest_position_approx(vehicle1.get_latest_position().time).lane_position
            else:
                # they are not in the same edge but the path is empty
                # -> vehicle2 must be in the edge in front of vehicle 1
                return True
    except NoPathFoundException:
        # no path between the vehicles
        return False
    # there is a path between from vehicle 1 to vehicle 2
    return True


def load_map(absolute_path_to_network_file: str):
    try:
        # go back until we are out of parent directory of the project
        cwd = Path.cwd()
        while str(cwd.name) != 'pythonpcs':
            cwd = cwd.parent
        cwd = cwd.parent
        # combine with absolute path: cut the first character ("/") of the path, concatenation doesnt work otherwise
        path_to_network_file = cwd / absolute_path_to_network_file[1:] / 'freeway.net.xml'
        # parse the xml document
        root = ET.parse(path_to_network_file).getroot()

        # read all edges
        for child in root.iter('edge'):
            # create the edge
            edge: Edge = Edge(child.get('id'))
            edges[edge.edge_id] = edge
            # parse all lanes of the current edge
            for child2 in child.iter('lane'):
                lane_id: str = child2.get('id')
                lane_index: int = int(child2.get('index'))
                lane_speed: float = float(child2.get('speed'))
                lane_length: float = float(child2.get('length'))
                lane: Lane = Lane(edge, lane_id, lane_index, lane_speed, lane_length)
                edge.lanes.append(lane)

        # read all connections
        for child in root.iter('connection'):
            from_edge_id: str = child.get('from')
            to_edge_id: str = child.get('to')
            from_lane: int = int(child.get('fromLane'))
            to_lane: int = int(child.get('toLane'))
            from_edge: Edge = edges[from_edge_id]
            to_edge: Edge = edges[to_edge_id]
            start_lane: Lane = from_edge.lanes[from_lane]
            start_lane.next_lanes.append(to_edge.lanes[to_lane])

        logger.info(0, "parsed sumo map with {} edges", [str(len(edges))])
    except Exception:
        logger.error(0, "unable to read edges for current sumo map: {}", [traceback.format_exc()])


edges: Dict[str, Edge] = {}
load_map(PCSConfig.path_to_sumo_network_file)

# testing
# print(edges['192064428'].get_connected_edges())
