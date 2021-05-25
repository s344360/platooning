from typing import List


from PCS.dependencies.pcs.model.sumo.Edge import Edge


class Lane:
    def __init__(self, edge: Edge, lane_id: str, lane_index: int, speed: float, length: float,
                 lane_start_x: float = -1, lane_start_y: float = -1, lane_end_x: float = -1, lane_end_y: float = -1):
        # the edge that is parent of this link
        self.edge: Edge = edge
        # the unique id of this lane
        self.lane_id: str = lane_id
        # the index of this lane starting from 0 for the very right Lane
        self.lane_index: int = lane_index
        # the allowed max speed on this Lane
        self.speed: float = speed
        # the length of this lane in meters
        self.length: float = length
        # the start x coordinate of this Lane
        self.lane_start_x: float = lane_start_x
        # the start y coordinate of this Lane
        self.lane_start_y: float = lane_start_y
        # the end x coordinate of this Lane
        self.lane_end_x: float = lane_end_x
        # the end y coordinate of this Lane
        self.lane_end_y: float = lane_end_y

        self.next_lanes: List[Lane] = []
