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
from wifimac.lowerMAC.RateAdaptation import Opportunistic, SINR

#######################
# Simulation parameters
#
# Simulation of the string topology: all nodes are placed equidistantly
# on a string, on each end of the string, an AP is positioned
# Traffic is either DL only or bidirectional
#
simTime = 3.5
settlingTime = 3.0
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
# wether MPs send/receive traffic
activeMPs = False

# Available frequencies for bss and backbone, in MHz
meshFrequency = 5500
bssFrequencies = [2400, 2440] #,2480]
# End simulation parameters
###########################

rtscts = True

####################
# Node configuration

# configuration class for AP and MP mesh transceivers, with RTS/CTS
class MyMeshTransceiver(wifimac.support.Transceiver.Mesh):
    def __init__(self, beaconDelay, frequency):
        super(MyMeshTransceiver, self).__init__(frequency)
        # changes to the default config
        self.layer2.beacon.delay = beaconDelay
        self.layer2.bufferSize = 50
        self.layer2.ra.raStrategy = SINR()

        if(rtscts):
            self.layer2.rtsctsThreshold = meanPacketSize/2
        else:
            self.layer2.rtsctsThreshold = meanPacketSize*2

# configuration class for AP and MP BSS transceivers, without RTS/CTS
class MyBSSTransceiver(wifimac.support.Transceiver.Mesh):
    def __init__(self, beaconDelay, frequency):
        super(MyBSSTransceiver, self).__init__(frequency)
        self.layer2.beacon.delay = beaconDelay
        self.layer2.ra.raStrategy = Opportunistic()
        self.layer2.bufferSize = 50


        if(rtscts):
            self.layer2.rtsctsThreshold = meanPacketSize/2
        else:
            self.layer2.rtsctsThreshold = meanPacketSize*2

# configuration class for STAs
class MySTAConfig(wifimac.support.Transceiver.Station):
    def __init__(self, initFrequency, position, scanFrequencies, scanDurationPerFrequency):
        super(MySTAConfig, self).__init__(frequency = initFrequency,
                                          position = position,
                                          scanFrequencies = scanFrequencies,
                                          scanDuration = scanDurationPerFrequency)
        self.layer2.ra.raStrategy = Opportunistic()

        if(rtscts):
            self.layer2.rtsctsThreshold = meanPacketSize/2
        else:
            self.layer2.rtsctsThreshold = meanPacketSize*2
# End node configuration
########################

###########################################
# Scenario setup etc. is in configCommon.py
execfile('configCommon.py')
