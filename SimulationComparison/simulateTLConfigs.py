import os, sys
import xml.etree.ElementTree as ET
import traci

# simulation configuration files
TRAFFIC_LIGHTS_FILE_1 = "traffic_lights_1.xml"
TRAFFIC_LIGHTS_FILE_2 = "traffic_lights_2.xml"

BASE_CONFIG_FILE = "base_config.sumocfg"
BASE_MAP_FILE = "base_map.net.xml"

# random vehicle generator
VEHICLE_RATE = 1/1.4 # 1.4 carro por segundo
GENERATE_NEW_CARS = True

# simulation parameters
STEP_LENGTH = "1"
AMBULANCE_ENTRY_TIME = 100 # instante em que ambulancia entra
MAX_SIMULATION_STEPS = 3700
AMBULANCE_NAME = "Amb"

# temp files
ERASE_TEMP_FILES = True
OUTPUT_MAP_FILE_1 = "temp_tl1.net.xml"
OUTPUT_MAP_FILE_2 = "temp_tl2.net.xml"
CONFIG_FILE_1 = "temp_config1.sumocfg"
CONFIG_FILE_2 = "temp_config2.sumocfg"
    
# Read traffic light configurations and write full map
def write_full_map(base_map_file, tl_file, output_map_file):
  mapTree = ET.parse(base_map_file)
  mapNet = mapTree.getroot()
  mapEdges = mapNet.findall("edge")
  tlLogicIndex = mapNet.getchildren().index(mapEdges[-1]) + 1

  tlTree = ET.parse(tl_file)
  tlData = tlTree.getroot()
  for tlLogic in tlData.iter("tlLogic"):
      mapNet.insert(tlLogicIndex, tlLogic)
      tlLogicIndex += 1

  mapTree.write(output_map_file)

# Write sumo config with specified net file
def write_full_config(base_config_file, net_file, output_config_file):
  config_tree = ET.parse(base_config_file)
  config = config_tree.getroot()
  net_elem = config.find("input").find("net-file")
  net_elem.set("value", net_file)
  config_tree.write(output_config_file)

# Execute simulation step for a given simulation label
def traciStep(sim_label, current_step):
    traci.switch(sim_label)
    traci.simulationStep()
    if current_step == AMBULANCE_ENTRY_TIME: # ambulancia entra no instante configurado
        traci.route.add("trip", ["416151865", "28596086#1"]) ##do hospital ate a NVIDIA
        traci.vehicle.add(AMBULANCE_NAME, "trip", typeID="reroutingType") ##faz rerotear essa trip
        traci.vehicle.setColor(AMBULANCE_NAME, (255,0,0,0)) ##Muda cor pra vermelha
        traci.gui.trackVehicle('View #0', AMBULANCE_NAME)
        traci.gui.setZoom('View #0', 1000.0)
    # simulation ends when ambulance arrives
    if current_step > AMBULANCE_ENTRY_TIME and AMBULANCE_NAME in traci.simulation.getArrivedIDList():
        return False
    return True
    
    
def main():
    # check sumo path
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:   
        sys.exit("Please declare environment variable 'SUMO_HOME'")
   
    # Generate random cars and routes
    if GENERATE_NEW_CARS:
        print('\n-> Randomizing vehicle trips...')
        os.system('randomTrips.py -n base_map.net.xml -e %s -p %s' % (str(MAX_SIMULATION_STEPS), str(VEHICLE_RATE)))
        os.system('randomTrips.py -n base_map.net.xml -r osm.passenger.rou.xml -e %s -p %s' % (str(MAX_SIMULATION_STEPS), str(VEHICLE_RATE)))

    # generate full nets from base map and traffic light configurations
    write_full_map(BASE_MAP_FILE, TRAFFIC_LIGHTS_FILE_1, OUTPUT_MAP_FILE_1)
    write_full_map(BASE_MAP_FILE, TRAFFIC_LIGHTS_FILE_2, OUTPUT_MAP_FILE_2)
    
    # generate configuration files
    write_full_config(BASE_CONFIG_FILE, OUTPUT_MAP_FILE_1, CONFIG_FILE_1)
    write_full_config(BASE_CONFIG_FILE, OUTPUT_MAP_FILE_2, CONFIG_FILE_2)

    # run simulations
    print('\n\n-> Simulating traffic...')
    sumoCmd1 = ["sumo-gui", "-c", CONFIG_FILE_1, "--step-length", STEP_LENGTH]
    traci.start(sumoCmd1, label="sim1")

    sumoCmd2 = ["sumo-gui", "-c", CONFIG_FILE_2, "--step-length", STEP_LENGTH]
    traci.start(sumoCmd2, label="sim2")

    sim1_running = True
    sim2_running = True
    step = 0
    while sim1_running or sim2_running:
        if sim1_running:
            sim1_running = traciStep("sim1", step)
        if sim2_running:
            sim2_running = traciStep("sim2", step)
        step += 1
    traci.close()
    
    if ERASE_TEMP_FILES:
        os.remove(OUTPUT_MAP_FILE_1)
        os.remove(OUTPUT_MAP_FILE_2)
        os.remove(CONFIG_FILE_1)
        os.remove(CONFIG_FILE_2)

if __name__ == "__main__":
    main()
