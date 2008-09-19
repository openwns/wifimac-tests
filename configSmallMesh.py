import wns

import wifimac.support.NodeCreator
import wifimac.support.Config

#######################
# Simulation parameters
#
# Simulation of the string topology: all nodes are placed equidistantly
# on a string, on each end of the string, an AP is positioned
# Traffic is either DL only or bidirectional
#
simTime = 3.5
settlingTime = 2.0
commonLoggerLevel = 1
dllLoggerLevel = 2

# length of the string
numMPs = 1
numSTAs = 3
numAPs = 2
distanceBetweenMPs = 50
verticalDistanceSTAandMP = 50

# load
meanPacketSize = 1480 * 8
offeredDL = 1.0e6
offeredUL = 1.0e6
ulIsActive = True
dlIsActive = True
startDelayUL = 1.01
startDelayDL = 1.02

# Available frequencies for bss and backbone, in MHz
meshFrequency = 5500
bssFrequencies = [2400, 2440] #,2480]
# End simulation parameters
###########################

rtscts = True

####################
# Node configuration

# configuration class for AP and MP mesh transceivers, with RTS/CTS
class MyMeshTransceiver(wifimac.support.Config.MeshTransceiver):
    def __init__(self, beaconDelay, frequency):
        super(MyMeshTransceiver, self).__init__(frequency, forwarding = True)
        # changes to the default config
        self.layer2.beacon.delay = beaconDelay
        self.layer2.mode = 'DraftN'
        self.layer2.ra.raStrategy = 'SINRwithMIMO'
        self.layer2.txop.txopLimit = 0.0
        self.layer2.rtscts.rtsctsOnTxopData = True
        self.layer2.aggregation.maxEntries = 10
        self.layer2.blockACK.maxOnAir = 10
        self.layer2.bufferSize = 50
        self.layer2.bufferSizeUnit = 'PDU'
        self.layer2.manager.numAntennas = 3

        if(rtscts):
            self.layer2.rtsctsThreshold = meanPacketSize/2
        else:
            self.layer2.rtsctsThreshold = meanPacketSize*self.layer2.aggregation.maxEntries*2

# configuration class for AP and MP BSS transceivers, without RTS/CTS
class MyBSSTransceiver(wifimac.support.Config.MeshTransceiver):
    def __init__(self, beaconDelay, frequency):
        super(MyBSSTransceiver, self).__init__(frequency, forwarding = False)
        self.layer2.beacon.delay = beaconDelay
        self.layer2.mode = 'DraftN'
        self.layer2.ra.raStrategy = 'SINR'
        self.layer2.txop.txopLimit = 0.0
        self.layer2.rtscts.rtsctsOnTxopData = True
        self.layer2.aggregation.maxEntries = 10
        self.layer2.blockACK.maxOnAir = 10
        self.layer2.bufferSize = 50
        self.layer2.bufferSizeUnit = 'PDU'
        self.layer2.manager.numAntennas = 1

        if(rtscts):
            self.layer2.rtsctsThreshold = meanPacketSize/2
        else:
            self.layer2.rtsctsThreshold = meanPacketSize*self.layer2.aggregation.maxEntries*2

# configuration class for STAs
class MySTAConfig(wifimac.support.Config.Station):
    def __init__(self, initFrequency, position, scanFrequencies, scanDurationPerFrequency):
        super(MySTAConfig, self).__init__(frequency = initFrequency,
                                          position = position,
                                          scanFrequencies = scanFrequencies,
                                          scanDuration = scanDurationPerFrequency)
        self.layer2.mode = 'DraftN'
        self.layer2.ra.raStrategy = 'SINR'

        if(rtscts):
            self.layer2.rtsctsThreshold = meanPacketSize/2
        else:
            self.layer2.rtsctsThreshold = meanPacketSize*self.layer2.aggregation.maxEntries*2
# End node configuration
########################

###########################################
# Scenario setup etc. is in configCommon.py
execfile('configCommon.py')
