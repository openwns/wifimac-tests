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
simTime = 5.5
settlingTime = 2.0
commonLoggerLevel = 1
dllLoggerLevel = 2

# length of the string
numMPs = 0
numSTAs = 1
numAPs = 1
distanceBetweenMPs = 50
verticalDistanceSTAandMP = 10

# load
meanPacketSize = 1480 * 8
offeredDL = 6.0e6
offeredUL = 0.0e6
ulIsActive = False
dlIsActive = True
startDelayUL = 1.01
startDelayDL = 1.02

# Available frequencies for bss and backbone, in MHz
meshFrequency = 5500
bssFrequencies = [2400, 2440, 2480]
# End simulation parameters
###########################

####################
# Node configuration

# configuration class for AP and MP mesh transceivers
class MyMeshTransceiver(wifimac.support.Config.MeshTransceiver):
    def __init__(self, beaconDelay, frequency):
        super(MyMeshTransceiver, self).__init__(frequency, forwarding = True)
        # changes to the default config
        self.layer2.beacon.delay = beaconDelay

# configuration class for AP and MP BSS transceivers
class MyBSSTransceiver(wifimac.support.Config.MeshTransceiver):
    def __init__(self, beaconDelay, frequency):
        super(MyBSSTransceiver, self).__init__(frequency, forwarding = False)
        self.layer2.beacon.delay = beaconDelay
        self.layer2.mode = 'basic'
        self.layer2.ra.raStrategy = 'ConstantLow'
        self.layer2.rtsctsThreshold = 800#1e6*8

# configuration class for STAs
class MySTAConfig(wifimac.support.Config.Station):
    def __init__(self, initFrequency, position, scanFrequencies, scanDurationPerFrequency):
        super(MySTAConfig, self).__init__(frequency = initFrequency,
                                          position = position,
                                          scanFrequencies = scanFrequencies,
                                          scanDuration = scanDurationPerFrequency)
        self.layer2.mode = 'basic'
        self.layer2.ra.raStrategy = 'ConstantLow'
        self.layer2.rtsctsThreshold = 800#1e6*8
        self.layer2.mode = 'basic'

# End node configuration
########################

###########################################
# Scenario setup etc. is in configCommon.py
execfile('configCommon.py')
