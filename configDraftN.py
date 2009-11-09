###############################################################################
# This file is part of openWNS (open Wireless Network Simulator)
# _____________________________________________________________________________
#
# Copyright (C) 2004-2008
# Chair of Communication Networks (ComNets)
# Kopernikusstr. 16, D-52074 Aachen, Germany
# phone: ++49-241-80-27910,
# fax: ++49-241-80-22242
# email: info@openwns.org
# www: http://www.openwns.org
# _____________________________________________________________________________
#
# openWNS is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License version 2 as published by the
# Free Software Foundation;
#
# openWNS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import openwns

import wifimac.support.Transceiver
from wifimac.lowerMAC.RateAdaptation import OpportunisticwithMIMO, SINRwithMIMO

#######################
# Simulation parameters
#
# Simulation of the string topology: all nodes are placed equidistantly
# on a string, on each end of the string, an AP is positioned
# Traffic is either DL only or bidirectional
#
simTime = 2.1
settlingTime = 2.0
commonLoggerLevel = 1
dllLoggerLevel = 2

# length of the string
numMPs = 0
numSTAs = 1
numAPs = 1
distanceBetweenMPs = 50
verticalDistanceSTAandMP = 50

# load
meanPacketSize = 1480 * 8
offeredDL = 50.0e6
offeredUL = 1.0e6
ulIsActive = False
dlIsActive = True
startDelayUL = 1.01
startDelayDL = 1.02
# wether MPs send/receive traffic
activeMPs = False

# Available frequencies for bss and backbone, in MHz
meshFrequency = 5500
bssFrequencies = [2400, 2440] #,2480]

# DraftN Configuration
numAntennas = 3
maxAggregation = 10
mimoCorrelation = 0.0
# End simulation parameters
###########################

rtscts = True

####################
# Node configuration

# configuration class for AP and MP mesh transceivers, with RTS/CTS
class MyMeshTransceiver(wifimac.support.Transceiver.DraftNMesh):
    def __init__(self,  beaconDelay, frequency):
        super(MyMeshTransceiver, self).__init__(frequency, numAntennas, maxAggregation, mimoCorrelation)
        self.layer2.beacon.delay = beaconDelay

        if(rtscts):
            self.layer2.rtsctsThreshold = meanPacketSize/2
        else:
            self.layer2.rtsctsThreshold = meanPacketSize*self.layer2.aggregation.maxEntries*2

# configuration class for AP and MP BSS transceivers, without RTS/CTS
class MyBSSTransceiver(wifimac.support.Transceiver.DraftN):
    def __init__(self, beaconDelay, frequency):
        super(MyBSSTransceiver, self).__init__(frequency, numAntennas, maxAggregation, mimoCorrelation)
        self.layer2.beacon.enabled = True
        self.layer2.beacon.delay = beaconDelay

        #self.layer2.txop.txopLimit = 0.0
        #self.layer2.rtscts.rtsctsOnTxopData = True

        if(rtscts):
            self.layer2.rtsctsThreshold = meanPacketSize/2
        else:
            self.layer2.rtsctsThreshold = meanPacketSize*self.layer2.aggregation.maxEntries*2

# configuration class for STAs
class MySTAConfig(wifimac.support.Transceiver.DraftNStation):
    def __init__(self, initFrequency, position, scanFrequencies, scanDurationPerFrequency):
        super(MySTAConfig, self).__init__(frequency = initFrequency,
                                          position = position,
                                          scanFrequencies = scanFrequencies,
                                          scanDuration = scanDurationPerFrequency,
                                          numAntennas = numAntennas,
                                          maxAggregation = maxAggregation,
                                          mimoCorrelation = mimoCorrelation)

        if(rtscts):
            self.layer2.rtsctsThreshold = meanPacketSize/2
        else:
            self.layer2.rtsctsThreshold = meanPacketSize*self.layer2.aggregation.maxEntries*2
# End node configuration
########################

###########################################
# Scenario setup etc. is in configCommon.py
execfile('configCommon.py')
