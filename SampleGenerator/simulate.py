import os, sys
import xml.etree.ElementTree as ET
from random import randint
import numpy as np
import time
import pickle
import math
import traci
import gzip

KEEP_OUTPUTS = True # if False, simulation output files are erased after being processed

# Random generator parameters
VEHICLE_RATE = 1/1.4 # 1.4 cars per second
MINTLTIME = 4  # seconds, lowest traffic light interval
MAXTLTIME = 60 # seconds, highest traffic light interval
GENERATE_NEW_CARS = True
GENERATE_NEW_TRAFFIC_LIGHTS = True

# Simulation parameters
STEP_LENGTH = "1"
AMBULANCE_ENTRY_TIME = 100
MAX_SIMULATION_STEPS = 3700
SHOW_INTERFACE = False
SHOW_WARNINGS = False
AMBULANCE_NAME = "Amb"
PROPERTIES = "%.1fcps_%sstep_%s" % (1/VEHICLE_RATE, STEP_LENGTH, str(int(time.time() * 1000)))
OUTPUT_DIRECTORY = "."
OUTPUT_FILENAME = "out_%s.xml" % (PROPERTIES)
OUTPUT_FILE = "%s/%s" % (OUTPUT_DIRECTORY, OUTPUT_FILENAME) # arquivo de saida

# Result generation parameters
XINIT = 0
XEND = 2800
YINIT = 0
YEND = 2900
AREASTEP = 10
PICKLE_DIRECTORY = "."
RESULT_DIRECTORY = "."
    
# Check for SUMO in environment PATH 
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:   
    sys.exit("Please declare environment variable 'SUMO_HOME'")

start_time = time.time()
partial_time = start_time

print('----------------------------------------------------');
print('-> Starting simulation %s' % PROPERTIES);

# Generate random vehicle trips
if GENERATE_NEW_CARS:
    print('\n-> Randomizing vehicle trips...')
    os.system('randomTrips.py -n osm.net.xml -e %s -p %s' % (str(MAX_SIMULATION_STEPS), str(VEHICLE_RATE)))
    os.system('randomTrips.py -n osm.net.xml -r osm.passenger.rou.xml -e %s -p %s' % (str(MAX_SIMULATION_STEPS), str(VEHICLE_RATE)))
    partial_time = time.time()

# Generate random traffic light timings
if GENERATE_NEW_TRAFFIC_LIGHTS:
    print('\n\n-> Randomizing traffic light configurations...')
    netTree = ET.parse('osm.net.xml') # le arquivo atual
    netRoot = netTree.getroot()
    for phase in netRoot.iter('phase'):
        if 'y' not in phase.get('state'):
            phase.set('duration', str(randint(MINTLTIME, MAXTLTIME))) # gera duracao aleatoria para estados que nao tem amarelo
    netTree.write('osm.net.xml') # reescreve arquivo da rede
    partial_time = time.time()

## Execute SUMO simlation and generate output
print('\n\n-> Simulating traffic...')
sumoCmd = ["sumo" + ("-gui" if SHOW_INTERFACE else ""), "-c", "osm.sumocfg", "--fcd-output", OUTPUT_FILE, "--step-length", STEP_LENGTH]
if SHOW_WARNINGS == False:
    sumoCmd.extend(["-W", "true"])
traci.start(sumoCmd)

for step in xrange(MAX_SIMULATION_STEPS):
    traci.simulationStep()
    if step == AMBULANCE_ENTRY_TIME:
        traci.route.add("trip", ["416151865", "28596086#1"])
        traci.vehicle.add(AMBULANCE_NAME, "trip", typeID="reroutingType")
        if SHOW_INTERFACE:
            traci.vehicle.setColor(AMBULANCE_NAME, (255,0,0,0))
            traci.gui.trackVehicle('View #0', AMBULANCE_NAME)
            traci.gui.setZoom('View #0', 1000.0)
    if step > AMBULANCE_ENTRY_TIME and AMBULANCE_NAME in traci.simulation.getArrivedIDList():
        print("\n--- Ambulance has arrived ---\n")
        break

traci.close()

print('\n>> Simulation duration: %.2f s' % (time.time() - partial_time))
partial_time = time.time()

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

###### Output processing
print('\n-> Processing simulation output...')
# Prepare mesh
x_list = []
y_list = []

current_x = XINIT
current_y = YINIT
while current_x < XEND:
  while current_y < YEND:
    y_list.append(0)
    current_y = current_y + AREASTEP

  current_y = YINIT
  x_list.append(y_list)
  y_list = []
  current_x = current_x + AREASTEP

picture_array = np.asarray(x_list)
pins_array = np.asarray(x_list)

# Prepare result xml
resultRoot = ET.Element("data")
## Create score
score = ET.SubElement(resultRoot, "score", ambTime="0.0", ambAvgSpeed="0.0", routeLength="0.0", allAvgSpeed="0.0", value="0.0")

totalTime = 0
vehicleTimeAmbCount = 0
xAmb = 0
yAmb = 0
xAmbPrev = xAmb
yAmbPrev = yAmb

now = 0.0
allAvgSpeed = 0.0
ambAvgSpeed = 0.0
for event, elem in ET.iterparse(OUTPUT_FILE):
    if elem.tag == "timestep":
        now = float(elem.get('time'))
        for vehicle in elem.iter('vehicle'):
            # update pins
            current_x = float(vehicle.get('x'))
            mesh_x = current_x//AREASTEP
            mesh_x = int(mesh_x)

            current_y = float(vehicle.get('y'))
            mesh_y = current_y//AREASTEP
            mesh_y = int(mesh_y)

            current_speed = float(vehicle.get('speed'))

            picture_array[mesh_x][mesh_y] = picture_array[mesh_x][mesh_y] + current_speed
            pins_array[mesh_x][mesh_y] = pins_array[mesh_x][mesh_y] + 1
            
            # update ambulance speed and distance
            if now > AMBULANCE_ENTRY_TIME: 
                vehicleTimeAmbCount += 1
                allAvgSpeed += current_speed
                if vehicle.get('id') == AMBULANCE_NAME:
                    ambAvgSpeed += current_speed
                    xAmb = float(vehicle.get('x'))
                    yAmb = float(vehicle.get('y'))
                    if xAmbPrev > 0 : score.set('routeLength', str(math.sqrt(math.pow(xAmb-xAmbPrev,2)+math.pow(yAmb-yAmbPrev,2))+float(score.get('routeLength')))) 
                    xAmbPrev = xAmb
                    yAmbPrev = yAmb
        elem.clear()
score.set('ambTime', str(now - AMBULANCE_ENTRY_TIME))
score.set('ambAvgSpeed', str(ambAvgSpeed/(now - AMBULANCE_ENTRY_TIME)))
score.set('allAvgSpeed', str(allAvgSpeed / vehicleTimeAmbCount))
score.set('value', str(float(score.get('ambAvgSpeed'))*0.6/30 + float(score.get('allAvgSpeed'))*0.4/30))

netTree = ET.parse('osm.net.xml')
netRoot = netTree.getroot()
for tlLogic in netRoot.iter('tlLogic'):
  resultRoot.append(tlLogic)
    
resultTree = ET.ElementTree(resultRoot)
indent(resultRoot)
resultTree.write("%s/res_%s.xml" % (RESULT_DIRECTORY, PROPERTIES))

average_speed_array = picture_array / now
average_pins_array = pins_array / now

with gzip.open("%s/%s_pins.pickle.gz" % (PICKLE_DIRECTORY, OUTPUT_FILENAME), 'wb') as f:
    pickle.dump(average_pins_array, f)

with gzip.open("%s/%s_speed.pickle.gz" % (PICKLE_DIRECTORY, OUTPUT_FILENAME), 'wb') as f:
    pickle.dump(average_speed_array, f)

print('>> Output processing time: %.2f s' % (time.time() - partial_time))
print('\n>> Total time: %.2f s\n\n' % (time.time() - start_time))


with open("time.txt", "a") as myfile:
    myfile.write("\n--- %s seconds ---" % (time.time() - start_time))


if KEEP_OUTPUTS == False:
    print("Apagando output")
    os.remove(OUTPUT_FILE)