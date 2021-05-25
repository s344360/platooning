import copy
from typing import Optional, List, Dict
from PCS.dependencies.pcs.model.VehiclePosition import VehiclePosition
from PCS.dependencies.pcs.model.VehicleMovement import VehicleMovement
from PCS.dependencies.pcs.model.VehicleParameter import VehicleParameter
from PCS.dependencies.pcs.strategy.DrivingStrategy import DrivingStrategy


class Vehicle:
    def __init__(self, vehicle_id: int, vehicle_type: str, desired_velocity: int):
        # unique vehicle id
        self.vehicle_id: int = vehicle_id
        # SUMO vehicle type
        self.vehicle_type: str = vehicle_type
        # current RSU of the vehicle
        self.rsu: int = 1
        # the position history of the vehicle
        self.position_history: List[VehiclePosition] = []
        # the movement history of the vehicle
        self.movement_history: List[VehicleMovement] = []
        # the current driving strategy of the vehicle
        self.driving_strategy: DrivingStrategy = None
        # a list of currently planned adaptions used to create update beacons for PLEXE
        self.planned_adaptions: Dict[VehicleParameter] = {}
        # the desired velocity of the vehicle, received during checkin
        self.desired_velocity: int = desired_velocity

    def __str__(self):
        return "vehicle id: " + str(self.vehicle_id)

    # a new entry to the position history
    def add_position(self, position: VehiclePosition):
        # remove old position data from this time step
        for pos in self.position_history:
            if pos.time == position.time:
                self.position_history.remove(pos)
        # add new position data
        self.position_history.append(position)

    # get the latest position entry of the vehicle
    # None if no data was received yet
    def get_latest_position(self) -> Optional[VehiclePosition]:
        if len(self.position_history) > 0:
            return self.position_history[len(self.position_history) - 1]
        else:
            return None

    # get the position of the vehicle at a specific simulation step
    # None if no data was received yet
    def get_position(self, time: int) -> Optional[VehiclePosition]:
        for pos in self.position_history:
            if pos.time == time:
                return pos
        return None

    def get_latest_position_approx(self, time: int) -> VehiclePosition:
        """
        Get the latest known position for a certain time. Try to calculate the approximate
        location if required (based on location and speed)
        :param time: time to search for
            note that this might result in locations that do not exist because the lane position is increased by
            this method. So the calculated length of the lane can be bigger than the actual length of the lane.
            It would be too complicated to check this and change to the following lane
        :return: a vehicle location
        """
        for pos in self.position_history:
            if pos.time == time:
                return pos
        # no exact location found, calculate approximate location
        pos = copy.deepcopy(self.get_latest_position())
        # calculate how far the vehicle gets per time step with the current speed
        distance = self.get_latest_movement().time * 1000 / 60 / 60
        distance = distance * (time - pos.time)
        pos.lane_position = pos.lane_position + distance
        return pos

    # a new entry to the movement history
    def add_movement(self, movement: VehicleMovement):
        # remove old movement data from this time step
        for mov in self.movement_history:
            if mov.time == movement.time:
                self.movement_history.remove(mov)
        # add new movement data
        self.movement_history.append(movement)

    # get the latest movement entry of the vehicle
    # None if no data was received yet
    def get_latest_movement(self) -> Optional[VehicleMovement]:
        if len(self.movement_history) > 0:
            print(self.movement_history[len(self.movement_history) - 1])
            return self.movement_history[len(self.movement_history) - 1]
        else:
            return None

    # get the movement of a vehicle at a specific simulation step
    # None if no data was received yet
    def get_movement(self, time: int) -> Optional[VehicleMovement]:
        for mov in self.movement_history:
            if mov.time == time:
                return mov
        return None
