Plexe APIs for Python
=====================

This repository includes the APIs for the platooning functions provided
by Plexe in SUMO.

Installation
------------

Clone the repository and then install the APIs using `pip`:
```
cd plexe-pyapi
sudo pip install .
```
To uninstall them:
```
sudo pip uninstall PlexeAPI
```

Usage
-----

The APIs are provided by a single class (`plexe.Plexe`) which should be
added as a `StepListener` to `traci`. Look at the following snippet for
an example:
```python
from plexe import Plexe, ACC
import traci

sumo_cmd = ["sumo-gui", "-c", "sumo.cfg"]
traci.start(sumo_cmd)
plexe = Plexe()
traci.addStepListener(plexe)

traci.simulationStep()
plexe.set_active_controller("vehicle.0", ACC)
plexe.set_cc_desired_speed("vehicle.0", 30)
plexe.set_fixed_lane("vehicle.0", 0)
```

Examples
--------

The `examples` folder includes some demo applications showing Plexe
features within SUMO using the TraCI interface via Python. The demos
include:

* A join maneuver demo, where a vehicle approaches a platoon of 8 cars
  and joins it in a certain position.
* An engine demo, which shows the features of the realistic engine
  model by running a sort of drag race between three different vehicle
  models: an Alfa Romeo 147, an Audi R8, and a Bugatti Veyron.

The code of the first example is implemented inside the `joindemo.py`
file, while the second inside `enginedemo.py`. You can simply run them
using

```
python joindemo.py
```
and
```
python enginedemo.py
```

After running for a certain amount of time, both demo resets and
automatically start from scratch (demo mode).

Alternatively, you can run them together with a dashboard, which shows
the RPM, the speed, the gear, and the acceleration of the vehicle being
tracked in the GUI. By tracking a different vehicle, the dashboard shows
the data of the chosen one.

To run the demos together with the dashboard type

```
python dashboard-demo.py joindemo.py
```
and
```
python dashboard-demo.py enginedemo.py
```

Running the dashboard requires you to install `PyQt5`. These demos currently
work with versions of Plexe SUMO starting from Plexe 2.1, which can be
downloaded [here](https://github.com/michele-segata/plexe-sumo). Checkout and
compile the `plexe-2.1` or the `master` branch.

For more information on Plexe, visit
[http://plexe.car2x.org](http://plexe.car2x.org).

Installing PyQt5
===

On Python 3 PyQt5 is available as a binary package on `pip`. After installing
Qt5 on your machine, PyQt5 can simply be installed by typing
```
sudo pip install PyQt5
```
or
```
pip install --user PyQt5
```
for a non system-wide installation.

For Python 2.7, the user is required to download and compile the source packages
for `sip` and for `PyQt5`. Download the lastest version of `sip` from
[here](https://www.riverbankcomputing.com/software/sip/download). Unpack the
sources and `cd` into the directory. Then type the following commands to
configure, build, and install `sip`:
```
python configure.py --sip-module PyQt5.sip
make
sudo make install
```
Then download the `PyQt5` sources from
[here](https://www.riverbankcomputing.com/software/pyqt/download5). Unpack the
sources and `cd` into the directory. Then type the following commands to
configure, build, and install `PyQt5`:
```
python configure.py
make
sudo make install
```
