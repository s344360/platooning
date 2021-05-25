from typing import List


class Platoon:

    def __init__(self, platoon_id: int):
        # unique id of the platoon
        self.platoon_id: int = platoon_id
        # target/maximum speed of the platoon
        self.velocity: int = None
        # lane index of the platoon
        self.lane: int = None
        # current members of the platoon (list of ids)
        self.vehicles: List[int] = []
        # maximum number of vehicles within the platoon - default is five
        self.max_vehicles: int = 30

    def __str__(self):
        return "platoon id: " + str(self.platoon_id) + ", lane: " + str(self.lane) + \
               ", number of vehicles: " + str(len(self.vehicles))

    # get the id of the vehicle that is driving in front of another vehicle
    # or the id of the vehicle itself if it has no leading vehicle
    def get_front_id(self, vehicle_id: int) -> int:
        for i in range(1, len(self.vehicles)):
            if self.vehicles[i] == vehicle_id:
                # print(str(self.vehicles[i-1]) + " is in front of " + str(self.vehicles[i]))
                return self.vehicles[i-1]
        return vehicle_id

    # get the id of the last vehicle in the platoon
    def get_last_id(self) -> int:
        if self.is_empty():
            return 0
        else:
            return self.vehicles[len(self.vehicles)-1]

    # get the id of the first vehicle in the platoon
    # or return 0 if the platoon is empty
    def get_leader_id(self) -> int:
        if len(self.vehicles) > 0:
            return self.vehicles[0]
        else:
            return 0

    # get the position of a specific vehicle in the platoon
    # or return 0 if it is not part tof the platoon
    def get_position(self, vehicle_id: int) -> int:
        for i in range(0, len(self.vehicles)):
            if self.vehicles[i] == vehicle_id:
                return i
        return 0

    def is_empty(self) -> bool:
        return self.vehicles == []

    def is_full(self) -> bool:
        return len(self.vehicles) >= self.max_vehicles
