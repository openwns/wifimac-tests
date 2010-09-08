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

import random
random.seed(22)

import openwns
from openwns import dB, dBm, fromdB, fromdBm
from openwns.interval import Interval

import constanze.traffic
import constanze.node

import wifimac.support
import wifimac.evaluation.default
import wifimac.evaluation.ip
import wifimac.convergence.PhyMode
from wifimac.lowerMAC.RateAdaptation import ARF, Constant

import rise.Scenario

#######################
# Simulation parameters
#
simTime = 1.01
settlingTime = 1.1
simTime += settlingTime
commonLoggerLevel = 1
dllLoggerLevel = 2

numSTAs = 10
distance = 5.0

# load (IP Header size is set to 0)
packetSize = 1000*8
offered = 20e6/float(numSTAs)
startDelay = 1.00

# Frequencies
networkFrequency = 5500
# End simulation parameters
###########################

###########################
# Transceiver configuration

# configuration class for STAs
class MySTATransceiver(wifimac.support.Transceiver.Station):
    def __init__(self, position):
        super(MySTATransceiver, self).__init__(frequency = networkFrequency,
                                               position = position,
                                               scanFrequencies = [networkFrequency],
                                               scanDuration = 0.3)

        # Transmission power
        self.txPower = dBm(20)

        # rate adaptation strategy: None, constant BPSK 1/2
        self.layer2.ra.raStrategy = Constant(wifimac.convergence.PhyMode.makeBasicPhyMode("BPSK", "1/2", dB(6.0)))

        # For frames above this threshold (in bit) RTS/CTS will be used
        self.layer2.rtsctsThreshold = 1

        # we change the timeouts of the standard so that 100% synchronization of the STAs is assured
        self.layer2.ackTimeout = self.layer2.sifsDuration + self.layer2.maximumACKDuration + self.layer2.slotDuration
        self.layer2.ctsTimeout = self.layer2.sifsDuration + self.layer2.maximumCTSDuration + self.layer2.slotDuration

        # the retry counter (and thus the cw) is reseted for every compound
        self.layer2.arq.bianchiRetryCounter = True

        # we change the behavior of the frameSync so that EIFS will be done although the frame could not be indentified as one
        self.layer2.frameSynchronization.signalRxErrorAlthoughNotSynchronized = True

        self.layer2.arq.longRetryLimit = 7
        self.layer2.arq.shortRetryLimit = 7
        self.layer2.unicastDCF.cwMin = 15
        self.layer2.unicastDCF.cwMax = 1031

        # disable broadcast BO
        self.layer2.broadcastDCF.backoffDisabled = True
# End node configuration
########################


# create an instance of the WNS configuration
# The variable must be called WNS!!!!
WNS = openwns.Simulator(simulationModel = openwns.node.NodeSimulationModel())
WNS.outputStrategy = openwns.simulator.OutputStrategy.DELETE
WNS.maxSimTime = simTime
WNS.statusWriteInterval = 120 # in seconds realTime
WNS.probesWriteInterval = 3600 # in seconds realTime


#################
# Create scenario
scenario = rise.Scenario.Scenario()

riseConfig = WNS.modules.rise
riseConfig.debug.transmitter = (commonLoggerLevel > 1)
riseConfig.debug.receiver = (commonLoggerLevel > 1)
riseConfig.debug.main = (commonLoggerLevel > 1)

ofdmaPhyConfig = WNS.modules.ofdmaPhy
managerPool = wifimac.support.ChannelManagerPool(scenario = scenario,
                                                 numMeshChannels = 1,
                                                 ofdmaPhyConfig = ofdmaPhyConfig)
# End create scenario
#####################

######################################
# Radio channel propagation parameters
myPathloss = rise.scenario.Pathloss.PyFunction(
    validFrequencies = Interval(2000, 6000),
    validDistances = Interval(2, 5000), #[m]
    offset = dB(-27.552219),
    freqFactor = 20,
    distFactor = 35,
    distanceUnit = "m", # only for the formula, not for validDistances
    minPathloss = dB(42), # pathloss at 2m distance
    outOfMinRange = rise.scenario.Pathloss.Constant("42 dB"),
    outOfMaxRange = rise.scenario.Pathloss.Deny(),
    scenarioWrap = False,
    sizeX = distance,
    sizeY = 1)
myShadowing = rise.scenario.Shadowing.No()
myFastFading = rise.scenario.FastFading.No()
propagationConfig = rise.scenario.Propagation.Configuration(
    pathloss = myPathloss,
    shadowing = myShadowing,
    fastFading = myFastFading)
# End radio channel propagation parameters
##########################################

###################################
#Create nodes using the NodeCreator
nc = wifimac.support.NodeCreator(propagationConfig)

# one RANG
rang = nc.createRANG(listener = True, loggerLevel = commonLoggerLevel)
WNS.simulationModel.nodes.append(rang)

# create (magic) service nodes for ARP, DNS, Pathselection, Capability Information
WNS.simulationModel.nodes.append(nc.createVARP(commonLoggerLevel))
WNS.simulationModel.nodes.append(nc.createVDNS(commonLoggerLevel))
WNS.simulationModel.nodes.append(nc.createVPS(numSTAs+1, commonLoggerLevel))
WNS.simulationModel.nodes.append(nc.createVCIB(commonLoggerLevel))

# Single instance of id-generator for all nodes with ids
idGen = wifimac.support.idGenerator()

# save IDs for probes
apIDs = []
mpIDs = []
staIDs = []
apAdrs = []
mpAdrs = []

## Create AP Transceiver
apTransceiver = wifimac.support.Transceiver.Mesh(frequency = networkFrequency)
# Transmission power
apTransceiver.txPower = dBm(25) #jen: 20
# set the inital start delay of the beacon so that beacons
# from multiple APs do not collide
apTransceiver.layer2.beacon.delay = 0.001
# No beacons shall be transmitted after the first one
apTransceiver.layer2.beacon.period = simTime * 2
# rate adaptation strategy: Constant with default BPSK 1/2
apTransceiver.layer2.ra.raStrategy =  Constant(wifimac.convergence.PhyMode.makeBasicPhyMode("BPSK", "1/2", dB(6.0)))
# For frames above this threshold (in bit) RTS/CTS will be used
apTransceiver.layer2.rtsctsThreshold = 1;

## Create AP node
apConfig = wifimac.support.Node(position = openwns.geometry.position.Position(0, 0, 0))
apConfig.transceivers.append(apTransceiver)
ap = nc.createAP(idGen, managerPool, apConfig)
ap.logger.level = commonLoggerLevel
ap.dll.logger.level = dllLoggerLevel
WNS.simulationModel.nodes.append(ap)
apIDs.append(ap.id)
apAdrs.extend(ap.dll.addresses)
rang.dll.addAP(ap)
print "Created AP at (0,0,0) with id ", ap.id, " and addresses ", ap.dll.addresses

# All STAs have to have the same position to avoid successful reception on collisions
for s in xrange(numSTAs):
    staConfig = MySTATransceiver(position = openwns.geometry.position.Position(distance, 0, 0))
    sta = nc.createSTA(idGen, managerPool, rang, config = staConfig,
                       loggerLevel = commonLoggerLevel,
                       dllLoggerLevel = dllLoggerLevel)

    # Set ip header size to zero
    sta.nl.ipHeader.config.headerSize = 0

    ul    = constanze.traffic.Poisson(startDelay+random.random()*0.1,
                                      offered,
                                      packetSize,
                                      parentLogger=sta.logger)
    ipBinding = constanze.node.IPBinding(sta.nl.domainName,
                                         rang.nl.domainName,
                                         parentLogger=sta.logger)
    sta.load.addTraffic(ipBinding, ul)

    # Add STA
    WNS.simulationModel.nodes.append(sta)
    staIDs.append(sta.id)
    print "Created STA at (", distance, ", 0, 0) with id ", sta.id
# End create nodes
##################

#########
# Probing
from openwns.evaluation import *

# Head of line packet service time (w/o final SIFS and ACK)
node = openwns.evaluation.createSourceNode(WNS, 'wifimac.hol.packet.incoming.delay')
n = node.appendChildren(SettlingTimeGuard(settlingTime))
n.appendChildren(PDF(minXValue = 0.0, maxXValue = 0.001, resolution=1000,
                     name = "wifimac.hol.packet.delay.detail",
                     description = "Packet service time [s]"))

# System throughput
node = openwns.evaluation.createSourceNode(WNS, 'ip.endToEnd.window.incoming.bitThroughput')
node = node.appendChildren(SettlingTimeGuard(settlingTime))
node = node.appendChildren(Accept(by = 'wns.node.Node.id', ifIn = [rang.nodeID]))
node = node.appendChildren(Moments(name = 'ip.endToEnd.window.incoming.bitThroughput',
                                   description = "UL Throughput [bit/s]"))
node = node.appendChildren(TimeSeries(name = 'ip.endToEnd.window.incoming.bitThroughput',
                                      description = "UL Throughput [bit/s]"))


# debugging probes, activate if required
node = openwns.evaluation.createSourceNode(WNS, 'wifimac.linkQuality.msduSuccessRate')
node = node.appendChildren(Accept(by = 'MAC.CompoundIsForMe', ifIn = [1]))
node = node.appendChildren(Accept(by = 'MAC.CompoundIsUnicast', ifIn = [1]))
node = node.appendChildren(SettlingTimeGuard(settlingTime))
node = node.appendChildren(Moments(name = 'wifimac.linkQuality.msduSuccessRate',
                                   description = "MSDU Success Rate"))

node = openwns.evaluation.createSourceNode(WNS, 'wifimac.linkQuality.rtsSuccess')
node = node.appendChildren(SettlingTimeGuard(settlingTime))
node = node.appendChildren(Moments(name = 'wifimac.linkQuality.rtsSuccess',
                                   description = "RTS Success Rate"))

node = openwns.evaluation.createSourceNode(WNS, 'wifimac.linkQuality.numTxAttempts')
node = node.appendChildren(SettlingTimeGuard(settlingTime))
node.appendChildren(PDF(minXValue = 0.0, maxXValue = 100, resolution=1000,
                        name = "wifimac.linkQuality.numTxAttempts",
                        description = "Number of Tx Attempts"))

openwns.setSimulator(WNS)
