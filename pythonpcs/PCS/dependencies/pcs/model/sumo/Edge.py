from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from PCS.dependencies.pcs.model.sumo.Lane import Lane


# represents a sumo edge within a map
class Edge:

    def __init__(self, edge_id: str):
        self.edge_id: str = edge_id
        self.lanes: List[Lane] = []

    # checks whether or not a certain link is part of this Edge
    def contains_lane(self, lane_id: str) -> bool:
        for lane in self.lanes:
            if lane.lane_id == lane_id:
                return True
        return False

    # get all edges that are connected with the current Edge via at least one Lane
    def get_connected_edges(self) -> List['Edge']:
        edges = []
        for lane in self.lanes:
            for connected_lane in lane.next_lanes:
                edges.append(connected_lane.edge)
        return edges
