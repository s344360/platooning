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
from examples.utils import add_platooning_vehicle_extended, communicate_2, start_sumo, running

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
from plexe import Plexe, ACC, CACC, FAKED_CACC, RPM, GEAR, ACCELERATION, SPEED
import examples.PCSCommunication as PCSCommunication

# vehicle length
LENGTH = 4
# inter-vehicle distance
DISTANCE = 5
# cruising speed
SPEED = 120 / 3.6
# number of vehicles
N_VEHICLES = 16
# vehicle to track in the simulation
VEHICLE_TO_TRACK = "v.0"


def add_vehicles(plexe, n, real_engine=False):
    """
    Adds n vehicles to the simulation
    :param plexe: API instance
    :param n: number of vehicles
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


def main(demo_mode, real_engine, setter=None):
    # used to randomly color the vehicles
    random.seed(1)
    start_sumo("examples/cfg/freeway.sumo.cfg", False)
    plexe = Plexe()
    traci.addStepListener(plexe)
    step = 0
    while running(demo_mode, step, 600000):

        # when reaching the time limit, reset the simulation when in demo_mode
        # - demo mode always set to false when using the PCS in the simulation
        if demo_mode and step == 600000:
            start_sumo("examples/cfg/freeway.sumo.cfg", True)
            step = 0
            random.seed(1)

        traci.simulationStep()

        if step == 0:
            # create vehicles and track the joiner
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
