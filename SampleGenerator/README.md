# Description
This program generates training samples by simulating traffic with random initial conditions.
Traffic lights and vehicle routes are randomized and configured as simulation parameters of SUMO.
During simulation, the ambulance is inserted into traffic and its route is calculated. The simulation ends when the ambulance arrives at the target destination.

# Pre-requisites
1. Python 2.7 (https://www.python.org)
2. SUMO (http://sumo.dlr.de)

# Usage
## Configuration
Parameters such as vehicle generation rate and traffic light duration can be configured within the script itself
## Command
    python simulate.py
## Outputs
* res_*.xml (score and traffic light configuration)
* *_pins.pickle.gz (vehicle density map)
* *_speed.pickle.gz (vehicle speed map)