
#!/usr/bin/env python
#
# Copyright (c) 2018 Michele Segata <segata@ccs-labs.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.
#

import os
import sys
import random
import plexe.position_helper as position_helper

from examples import custom_platooning_demo
from examples.utils import add_platooning_vehicle_extended, communicate_2, start_sumo, running, \
    get_distance, get_distance2

from typing import List

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
from plexe import Plexe, ACC, CACC, FAKED_CACC, RPM, GEAR, ACCELERATION, SPEED
import examples.PCSCommunication as PCSCommunication
import plexe.position_helper as position_helper

lock = 0

# vehicle length
LENGTH = 4
# inter-vehicle distance
DISTANCE = 5
# cruising speed
SPEED = 120 / 3.6
# number of vehicles
N_VEHICLES = 14

# vehicle to track in the simulation
VEHICLE_TO_TRACK = "v.0"

# new variables
JOIN_DISTANCE = DISTANCE * 2
JOIN_POSITION = 2

GOING_TO_POSITION = 0
OPENING_GAP = 1
COMPLETED = 2

JOINER = ""
FRONT_JOIN = ""
BEHIND_JOIN = ""

platoon_vehicles: List = []
platoon_vehicles_planner: List = []
joinList: List = []

platoon_lane = 0

myDict = {}
test = 0
con = 0
count = 0
test3 = 1
temp3 = 0
indexPos = 0

def add_vehicles(plexe, n, real_engine=False):
    """
    Adds n vehicles to the simulation
    :param plexe: API instance
    :param n: number of vehicles# vehicle length
LENGTH = 4
# inter-vehicle distance
DISTANCE = 5
# cruising speed
SPEED = 120 / 3.6
# number of vehicles
N_VEHICLES = 20
    :param real_engine: set to true to use the realistic engine model,
    false to use a first order lag model
    """
    # add n vehicles
    for i in range(n):
        vid = "v.%d" % i
        add_platooning_vehicle_extended(plexe, vid, (n - i + 1) * (DISTANCE + LENGTH) + 50, 0, SPEED, DISTANCE,
                                        real_engine)
        plexe.set_fixed_lane(vid, 0, safe=False)
        traci.vehicle.setSpeedMode(vid, 0)
        plexe.set_active_controller(vid, ACC)

def open_gap(plexe, vid, jid, n):
    """
    Makes the vehicle that will be behind the joiner open a gap to let the
    joiner in. This is done by creating a temporary platoon, i.e., setting
    the leader of all vehicles behind to the one that opens the gap and then
    setting the front vehicle of the latter to be the joiner. To properly
    open the gap, the vehicle leaving space switches to the "fake" CACC,
    to consider the GPS distance to the joiner
    :param plexe: API instance
    :param vid: vehicle that should open the gap
    :param jid: id of the joiner
    :param topology: the current platoon topology
    :param n: total number of vehicles currently in the platoon
    :return: the modified topology
    """
    index = int(vid.split(".")[1])
    # check out, which index vid have in a platoon
    vid_index = 0
    for i in range(0, len(platoon_vehicles_planner)):
        if platoon_vehicles_planner[i] - 1 == index: vid_index = i; break

    # temporarily change the leader
    print("platoonplanner check",platoon_vehicles_planner)
    for i in range(vid_index + 1, len(platoon_vehicles_planner)):
        #vidstr = "v.%d" % i
        vidstr = "v.%d"%(platoon_vehicles_planner[i]-1)
        print("vidstr",vidstr)
        print("check change the leader")
        for v_id, v_information in position_helper.all_vehicles.items():
            if (v_id == vidstr):
                print("v_id",v_id)
                v_information.platoon_leader_id = vid;
                break
    # the front vehicle if the vehicle opening the gap is the joiner
    # topology[vid]["front"] = "jid"
    for v_id, v_information in position_helper.all_vehicles.items():
        if (v_id == vid):
            v_information.front_vehicle_id = jid
            plexe.set_active_controller(v_id, FAKED_CACC)
            plexe.set_path_cacc_parameters(v_id, distance=JOIN_DISTANCE + 5);break


def get_in_position(plexe, jid, fid):
    """
    Makes the joining vehicle get close to the join position. This is done by
    changing the topology and setting the leader and the front vehicle for
    the joiner. In addition, we increase the cruising speed and we switch to
    the "fake" CACC, which uses a given GPS distance instead of the radar
    distance to compute the control action
    :param plexe: API instance
    :param jid: id of the joiner
    :param fid: id of the vehicle that will become the predecessor of the joiner
    :param topology: the current platoon topology
    :return: the modified topology
    """
    for v_id, v_information in position_helper.all_vehicles.items():
        if (v_id == jid):
            v_information.platoon_leader_id = "v.%d" % (
                        platoon_vehicles_planner[0] - 1)
            v_information.front_vehicle_id = fid
            v_information.platoon_id = platoon_lane
            plexe.set_cc_desired_speed(v_id, SPEED + 15)
            plexe.set_active_controller(v_id, FAKED_CACC);break


def reset_leader(vid):
    """
    After the maneuver is completed, the vehicles behind the one that opened
    the gap, reset the leader to the initial one
    :param vid: id of the vehicle that let the joiner in
    :param topology: the current platoon topology
    :param n: total number of vehicles in the platoon (before the joiner)
    :return: the modified topology
    """
    index = int(vid.split(".")[1])
    vid_index = 0
    for i in range(0, len(platoon_vehicles_planner)):
        if platoon_vehicles_planner[i] - 1 == index: vid_index = i; break

    for i in range(vid_index + 1, len(platoon_vehicles_planner)):
        #vidstr = "v.%d" % i
        vidstr = "v.%d" % (platoon_vehicles_planner[i]-1)
        for v_id, v_information in position_helper.all_vehicles.items():
            if (v_id == vidstr):
                v_information.platoon_leader_id = "v.%d" % (
                            platoon_vehicles_planner[0] - 1); break


# find index to add joiner in the right position in platoon later
def find_joiner_position(tempA: List[int]):
    for i in range(0, len(platoon_vehicles_planner)):
        if (platoon_vehicles_planner[i] - 1 == platoon_vehicles_planner[
            tempA[1]] - 1):
            custom_platooning_demo.indexPos = i + 1
            break


def define_front_behind_vehicle(plexe):
    test3 = 1
    for key in myDict:
        for i in platoon_vehicles:
            if (i == int(key)):
                test3 = 0
                break

        # the next in myDict candidate joiner
        temp5 = plexe.get_lane_index(("v.%d" % (int(key) - 1)))
        if (test3 == 1 and (temp5 < 1 or temp5 > 1)):
            tempA = myDict[key]
            custom_platooning_demo.JOINER = "v.%d" % (int(key) - 1)
            custom_platooning_demo.FRONT_JOIN = "v.%d" % (
                        platoon_vehicles_planner[tempA[1]] - 1)  # 8.04platoon_vehicles[tempA[1]]-1
            custom_platooning_demo.BEHIND_JOIN = "v.%d" % (
                        platoon_vehicles_planner[tempA[0]] - 1)  # 8.04platoon_vehicles[tempA[0]]-1
            find_joiner_position(tempA)
            custom_platooning_demo.con = 1
            break

        if(test3 == 1 and temp5 == 1):
            test4 = 1
            if (len(joinList)== 0):
                joinList.append(key)
            for i in joinList:
                if i==key:test4=0;break
            if(test4 == 1 and len(joinList)!=0):joinList.append(key)

        test3 = 1

    custom_platooning_demo.lock = 1


def main(demo_mode, real_engine, setter=None):
    # used to randomly color the vehicles
    random.seed(1)
    start_sumo("examples/cfg/freeway.sumo.cfg", False)
    plexe = Plexe()
    traci.addStepListener(plexe)
    step = 0
    state = GOING_TO_POSITION
    while running(demo_mode, step, 600000):
        # when reaching the time limit, reset the simulation when in demo_mode
        # - demo mode always set to false when using the PCS in the simulation
        if demo_mode and step == 600000:
            start_sumo("examples/cfg/freeway.sumo.cfg", True)
            step = 0
            state = GOING_TO_POSITION
            random.seed(1)
        traci.simulationStep()

        # for tests

        if count < 1000:
            plexe.set_fixed_lane("v.2", 0, safe=False)
        if count > 2000 and count < 2100: #2000 2100
            plexe.set_fixed_lane("v.3", 0, safe=False)
        if count > 3000 and count < 3100:
            plexe.set_fixed_lane("v.5", 2, safe=False)
        if count > 4000 and count < 4100:
            plexe.set_fixed_lane("v.6", 2, safe=False)
        if count > 6000 and count < 6050:#6500 and count4 < 6700
            plexe.set_fixed_lane("v.7", 2, safe=False)#v.7
            define_front_behind_vehicle(plexe)
        if count > 6200 and count < 6250:  # 6500 and count4 < 6700
            plexe.set_fixed_lane("v.9", 2, safe=False)  # v.7


        custom_platooning_demo.count = count + 1

        if(len(joinList)>0):
            if (int(joinList[0]) - 1)!= (int(JOINER.split(".")[1])):
                define_front_behind_vehicle(plexe)
                joinList.pop(0)

        print("platoon_vehicles_planner", platoon_vehicles_planner)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
        if con == 1:
            state = 0
            custom_platooning_demo.con = 0
        if step == 0:
            add_vehicles(plexe, N_VEHICLES, real_engine)
            traci.gui.trackVehicle("View #0", VEHICLE_TO_TRACK)
            traci.gui.setZoom("View #0", 20000)
            # send information to the PCS that vehicles joined
            PCSCommunication.send_checkin_to_pcs(plexe)

        if step % 100 == 1:  # 1 times per second
            # send regular status beacons to the PCS
            PCSCommunication.send_status_to_pcs(plexe)

        if step % 10 == 1:
            # simulate vehicle communication every 100 ms
            communicate_2(plexe)

        #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<


        if lock == 1:

            get_in_position(plexe, JOINER, FRONT_JOIN)

            if state == GOING_TO_POSITION and step > 0:
                print("state == GOING_TO_POSITION")
                # when the distance of the joiner is small enough, let the others
                # open a gap to let the joiner enter the platoon

                if get_distance(plexe, JOINER, FRONT_JOIN) < JOIN_DISTANCE + 1:
                    print("near distance")
                    state = OPENING_GAP
                    open_gap(plexe, BEHIND_JOIN, JOINER,
                             N_VEHICLES)
                    print("get_distance")
            if state == OPENING_GAP:
                print("OPENING_GAP")

                # when the gap is large enough, complete the maneuver
                if get_distance(plexe, BEHIND_JOIN, FRONT_JOIN) > \
                        JOIN_DISTANCE + 2:
                    print("when distance large enough ")
                    state = COMPLETED
                    plexe.set_fixed_lane(JOINER, platoon_lane, safe=False)
                    print("change the lane")
                    # topology1[0]=0
                    plexe.set_active_controller(JOINER, CACC)
                    plexe.set_path_cacc_parameters(JOINER, distance=DISTANCE)
                    plexe.set_active_controller(BEHIND_JOIN, CACC)
                    plexe.set_path_cacc_parameters(BEHIND_JOIN, distance=DISTANCE)
                    reset_leader(BEHIND_JOIN)

                    intJoiner = int(JOINER.split(".")[1])
                    if custom_platooning_demo.temp3 != intJoiner:
                        custom_platooning_demo.temp3 = intJoiner
                        custom_platooning_demo.lock = 0

                        print("finished")
                        print("++++++++++dict is empty", myDict)

                        if (test3 == 1):
                            myDict.pop('%d' % (intJoiner + 1))
                        print("intJoiner", intJoiner)
                        print("indexPos", indexPos)
                        platoon_vehicles.insert(indexPos, intJoiner + 1)
                        platoon_vehicles_planner.insert(indexPos, intJoiner + 1)
                        #####################################
                        print("++++++++++dict is empty number 2", myDict)
                        custom_platooning_demo.con = 1
                        if (myDict != 0):
                            define_front_behind_vehicle(plexe)

        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

        if real_engine and setter is not None:
            # if we are running with the dashboard, update its values
            tracked_id = traci.gui.getTrackedVehicle("View #0")
            if tracked_id != "":
                ed = plexe.get_engine_data(tracked_id)
                vd = plexe.get_vehicle_data(tracked_id)
                setter(ed[RPM], ed[GEAR], vd.speed, vd.acceleration)

        step += 1
    traci.close()


if __name__ == "__main__":
    main(False, False)
