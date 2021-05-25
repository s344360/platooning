from PCS.dependencies.pcs.model.Vehicle import Vehicle
from PCS.dependencies.pcs.model.VehiclePosition import VehiclePosition
import functools


# comparator implementation used to compare two vehicles based on their position within their current lane.
# Note that using this comparator might only be a good idea if the two vehicles are on the same lane.
def old_lane_position_comparator(vehicle1: Vehicle, vehicle2: Vehicle) -> int:
    # sort based on position within the lane
    pos_v1 = vehicle1.get_latest_position().lane_position
    pos_v2 = vehicle2.get_latest_position().lane_position
    # return -1 if (v1 -> v2), 1 if (v2 -> v1) (driving direction ---->)
    return -1 if pos_v1 < pos_v2 else 1


# need to convert the old_lane_position_comparator to a valid key function in order to use sorted
lane_position_comparator = functools.cmp_to_key(old_lane_position_comparator)


# testing the comparator comparator -> is this driving order?

'''
v1 = Vehicle(1, "hi", 100)
v2 = Vehicle(2, "hi", 100)
v3 = Vehicle(3, "hi", 100)

p1 = VehiclePosition()
p1.lane_position = 1.34

p2 = VehiclePosition()
p2.lane_position = 1.39

p3 = VehiclePosition()
p3.lane_position = 1.36

v1.add_position(p1)
v2.add_position(p2)
v3.add_position(p3)

test_list = [v1, v2, v3]


test_list.sort(key=lane_position_comparator)
print(str(test_list[0].vehicle_id) + str(test_list[1].vehicle_id) + str(test_list[2].vehicle_id))
'''
