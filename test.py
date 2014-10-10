import os
import sys
import optparse
import subprocess
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
      
else:   
    sys.exit("please declare environment variable 'SUMO_HOME'")
  
from sumolib import checkBinary 
from subprocess import Popen, PIPE, STDOUT
import traci
import os
DEVNULL = open(os.devnull, 'wb')
PORT = 8813
PATH = "E:/Scriptie/ritsscenario"
CASENAME="hello"
def init(): 
    print "Opening a port at", PORT
    traci.init(PORT)
    print "Connection made with sumo"
    
def run():
    print "starting simulation"
    step = 0
    while step < 10000:
        traci.simulationStep()
        laneAreaList=traci.areal.getIDList()
        print
        print "+---------------------------------------+"
        print "Current Step:", step
        for laneAreaID in laneAreaList:
            print laneAreaID
            print "+ getJamLengthMeters\t", traci.areal.getJamLengthMeters(laneAreaID),"\t+"
            print "+ getJamLengthVehicle\t", traci.areal.getJamLengthVehicle(laneAreaID),"\t+"
            print "+ getLastStepMeanSpeed\t", traci.areal.getLastStepMeanSpeed(laneAreaID),"\t+"
            print "+ getLastStepOccupancy\t", traci.areal.getLastStepOccupancy(laneAreaID),"\t+"
            print "+ getLastStepVehicleIdList\t", traci.areal.getLastStepVehicleIdList(laneAreaID),"\t+"
            vehicleList = traci.areal.getLastStepVehicleIdList(laneAreaID)
            if laneAreaID == "N42lane0":
                for vehicleID in vehicleList:                  
                    print "+ getDrivingDistance nextsensor(",vehicleID,") ", traci.vehicle.getDrivingDistance(vehicleID,"A28Tot700",20,0)
            elif laneAreaID == "A28lane1.0":
                for vehicleID in vehicleList:                  
                    print "+ getDrivingDistance nextsensor(",vehicleID,") ", traci.vehicle.getDrivingDistance(vehicleID,"A28Tot700",20,1)
            
            print "---------------------------------------"
        print "+---------------------------------------+"
        step += 1
    traci.close()

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--gui", action="store_true", default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options

# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.gui:
        sumoBinary = checkBinary('sumo-gui')
    else:
        sumoBinary = checkBinary('sumo')
    sumoProcess = subprocess.Popen([sumoBinary, "-n", PATH+"/"+CASENAME+".net.xml",'-r',PATH+"/"+CASENAME+".rou.xml",'-a',PATH+"/sensors.xml", "--remote-port", str(PORT)], stdout=DEVNULL#stdout=sys.stdout,
    ,stderr=sys.stderr)
    init()
    run()
    sumoProcess.wait()