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
import xml.etree.ElementTree as ET
DEVNULL = open(os.devnull, 'wb')

class NormController:   
    PORT = 8813
    # Use this if this file is in the same directory as the sumo files, enter the correct path to the sumo files otherwise.
    PATH = os.getcwd()
    #PATH = "E:/Scriptie/ritsscenario"
    CASENAME="hello"
    SWITCH_TIME = 0
    
    
    def handleNormal(self):
        vehicleList = traci.areal.getLastStepVehicleIdList("N42lane0")
        
        # 2 interesting cases:
        # 1. there are five or more cars waiting on the sensor -> switch priority
        # 2. there are four or less cars, but at least one waiting on the sensor -> sensor triggered
        if len(vehicleList) >= 5:
            self.returnToSwitchPriority()
        elif len(vehicleList) > 0:
            self.state = "sensorTriggered"
            self.vehicleWaitingTime = 0.0
            self.waitingVehicleID = vehicleList[0]
        print "handleNormal"
    
    def handleSensorTriggered(self):
        print "handleSensorTriggered"
        vehicleList = traci.areal.getLastStepVehicleIdList("N42lane0")
        if len(vehicleList) >= 5:
            self.returnToSwitchPriority()
        elif len(vehicleList) == 0:
            self.returnToNormal()
        elif self.waitingVehicleID == vehicleList[0]:
            self.vehicleWaitingTime += traci.simulation.getDeltaT()
            if self.vehicleWaitingTime >= 40000:
                self.returnToSwitchPriority()
            
    def handleSwitchPriority(self):
        print "handleSwitchPriority"
        self.switch_time += traci.simulation.getDeltaT()

        if self.switch_time >= 10000:
                self.returnToNormal()
        if self.stoppedVehicleID == None:
            stoppedVehicleList = traci.areal.getLastStepVehicleIdList("A28_350_lane0_0")
            if len(stoppedVehicleList) > 0:
                self.stoppedVehicleID = stoppedVehicleList[0]
                traci.vehicle.setSpeed(self.stoppedVehicleID,0)
                traci.vehicle.setColor(self.stoppedVehicleID,(0,255,0,0))
            
    
    def returnToSwitchPriority(self):
        self.state="switchPriority"
        self.switch_time = 0.0
    
    def returnToNormal(self):
        self.state = "normal"
        self.vehicleWaitingTime = 0.0
        self.switch_time = 0.0
        self.waitingVehicleID = None
        if self.stoppedVehicleID != None:                    
            maxLaneSpeed = traci.lane.getMaxSpeed(traci.vehicle.getLaneID(self.stoppedVehicleID))
            traci.vehicle.setSpeed(self.stoppedVehicleID,maxLaneSpeed)
            self.stoppedVehicleID = None
   
    switch = {"normal" : handleNormal,
                "sensorTriggered" : handleSensorTriggered,
                "switchPriority" : handleSwitchPriority,
    }
    
    state = "normal"

    def __init__(self, options):
             # this script has been called from the command line. It will start sumo as a
        # server, then connect and run
        if options.gui:
            sumoBinary = checkBinary('sumo-gui')
        else:
            sumoBinary = checkBinary('sumo')
             
        self.rounds = 1000
        self.sumoProcess = subprocess.Popen([sumoBinary, "-n", self.PATH+"/"+self.CASENAME+".net.xml",'-r',self.PATH+"/"+self.CASENAME+".rou.xml",'-a',self.PATH+"/sensors.xml", "--remote-port", str(self.PORT)], stdout=DEVNULL#stdout=sys.stdout,
        ,stderr=sys.stderr)
    
        print "Opening a port at", self.PORT
        traci.init(self.PORT)
        print "Connection made with sumo"
        self.laneAreaList = traci.areal.getIDList()
        self.stoppedVehicleID = None
    
    def run(self):
        print "starting simulation for",self.rounds,"rounds"
        step = 0
        while step < self.rounds:
            traci.simulationStep()
            self.switch[self.state](self)
            """
            Als de invoegstrook meer dan 5 auto's wachtend heeft: voorrang
            Als voorste auto op invoegstrook langer dan 1 minuut wacht: voorrang
            
            
          
            
            
            laneAreaList=traci.areal.getIDList()
            print
            print "+---------------------------------------+"
            print "Current Step:", step
            for laneAreaID in laneAreaList:
                print "Position of sensor:",self.getSensorPos(laneAreaID)
                print laneAreaID
                print "+ getJamLengthMeters\t", traci.areal.getJamLengthMeters(laneAreaID),"\t+"
                print "+ getJamLengthVehicle\t", traci.areal.getJamLengthVehicle(laneAreaID),"\t+"
                print "+ getLastStepMeanSpeed\t", traci.areal.getLastStepMeanSpeed(laneAreaID),"\t+"
                print "+ getLastStepOccupancy\t", traci.areal.getLastStepOccupancy(laneAreaID),"\t+"
                print "+ getLastStepVehicleIdList\t", traci.areal.getLastStepVehicleIdList(laneAreaID),"\t+"
                
                vehicleList = traci.areal.getLastStepVehicleIdList(laneAreaID)
                if laneAreaID == "N42lane0":
                    for vehicleID in vehicleList:                  
                        print "+ getDrivingDistance nextsensor(",vehicleID,") ", traci.vehicle.getDrivingDistance(vehicleID,"A28Tot700",getSensorPos("A28lane0.1"),0)
                elif laneAreaID == "A28lane1.0":
                    for vehicleID in vehicleList:                  
                        print "+ getDrivingDistance nextsensor(",vehicleID,") ", traci.vehicle.getDrivingDistance(vehicleID,"A28Tot700",20,0)
                
                print "---------------------------------------"
            print "+---------------------------------------+"\
              """
            step += 1
        traci.close()
    
    def getSensorPos(self,name):
        tree = ET.parse(self.PATH+"/sensors.xml")
        root = tree.getroot()
        for child in root:
            if child.get("id") == name: 
                return child.get("pos")

    def cleanup(self):
        self.sumoProcess.wait()
        
def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--gui", action="store_true",  default=False, help="run the gui version of sumo")
    options, args = optParser.parse_args()
    return options
        
# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()
    
    norm = NormController(options)
    norm.run()
    norm.cleanup()

