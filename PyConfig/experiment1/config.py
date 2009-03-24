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

# begin example "wifimac.tutorial.experiment1.config.imports"
import random
random.seed(22)

import openwns
from openwns import dB, dBm, fromdB, fromdBm
from openwns.interval import Interval

import constanze.traffic
import constanze.node

import ip.VirtualARP
import ip.VirtualDNS

import wifimac.support
import wifimac.support.Transceiver
import wifimac.pathselection
import wifimac.management.InformationBases
import wifimac.evaluation.default
import wifimac.evaluation.ip
from wifimac.lowerMAC.RateAdaptation import Opportunistic

import rise.Scenario
# end example

# begin example "wifimac.tutorial.experiment1.config.simulationParameter"
#######################
# Simulation parameters
#
from SimConfig import params
simTime = params.simTime
settlingTime = 2.0
commonLoggerLevel = 2
dllLoggerLevel = 2

distance = params.distance

# load
packetSize = 1480 * 8
offeredDL = (1.0-params.ulRatio) * params.offeredTraffic
offeredUL = params.ulRatio * params.offeredTraffic
ulIsActive = (params.ulRatio > 0.0)
dlIsActive = (params.ulRatio < 1.0)
startDelayUL = 1.01
startDelayDL = 1.02

# Frequencies
networkFrequency = 5500
# End simulation parameters
###########################
# end example

# begin example "wifimac.tutorial.experiment1.config.WNS"
# create an instance of the WNS configuration
# The variable must be called WNS!!!!
WNS = openwns.Simulator(simulationModel = openwns.node.NodeSimulationModel())
WNS.outputStrategy = openwns.simulator.OutputStrategy.DELETE
WNS.maxSimTime = simTime
WNS.statusWriteInterval = 120 # in seconds realTime
WNS.probesWriteInterval = 3600 # in seconds realTime
# end example

# begin example "wifimac.tutorial.experiment1.config.scenario"
#################
# Create scenario
sizeX = distance
sizeY = 10
scenario = rise.Scenario.Scenario(sizeX, sizeY)

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
# end example

# begin example "wifimac.tutorial.experiment1.config.radioChannel"
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
    sizeX = sizeX,
    sizeY = sizeY)
myShadowing = rise.scenario.Shadowing.No()
myFastFading = rise.scenario.FastFading.No()
propagationConfig = rise.scenario.Propagation.Configuration(
    pathloss = myPathloss,
    shadowing = myShadowing,
    fastFading = myFastFading)
# End radio channel propagation parameters
##########################################
#end example

# begin example "wifimac.tutorial.experiment1.config.NodeCreation.Virtual"
###################################
#Create nodes using the NodeCreator
nc = wifimac.support.NodeCreator(propagationConfig)

# one RANG
rang = nc.createRANG()
rang.logger.level = commonLoggerLevel
if(ulIsActive):
    # The RANG only has one IPListenerBinding that is attached
    # to the listener. The listener is the only traffic sink
    # within the RANG
    ipListenerBinding = constanze.node.IPListenerBinding(
        rang.nl.domainName, parentLogger=rang.logger)
    listener = constanze.node.Listener(
        rang.nl.domainName + ".listener", probeWindow = 0.1, parentLogger=rang.logger)
    rang.load.addListener(ipListenerBinding, listener)
    rang.nl.windowedEndToEndProbe.config.windowSize = 1.0
    rang.nl.windowedEndToEndProbe.config.sampleInterval = 0.5
WNS.simulationModel.nodes.append(rang)

# create (magic) service nodes
# One virtual ARP Zone
varp = ip.VirtualARP.VirtualARPServer("VARP", "theOnlyZone")
varp.logger.level = commonLoggerLevel
WNS.simulationModel.nodes.append(varp)

# One virtual DNS server
vdns = ip.VirtualDNS.VirtualDNSServer("VDNS", "ip.DEFAULT.GLOBAL")
vdns.logger.level = commonLoggerLevel
WNS.simulationModel.nodes.append(vdns)

# One virtual pathselection server
vps = wifimac.pathselection.VirtualPSServer("VPS", numNodes = 2)
vps.logger.level = commonLoggerLevel
WNS.simulationModel.nodes.append(vps)

# One virtual capability information base server
vcibs = wifimac.management.InformationBases.VirtualCababilityInformationService("VCIB")
vcibs.logger.level = commonLoggerLevel
WNS.simulationModel.nodes.append(vcibs)

# end example

# begin example "wifimac.tutorial.experiment1.config.NodeCreation.AP"
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
apTransceiver.txPower = dBm(20)
# set the inital start delay of the beacon so that beacons
# from multiple APs do not collide
apTransceiver.layer2.beacon.delay = 0.001
# rate adaptation strategy: PER based
apTransceiver.layer2.ra.raStrategy = Opportunistic()
# For frames above this threshold (in bit) RTS/CTS will be used
apTransceiver.layer2.rtsctsThreshold = 8e6

## Create AP node
apConfig = wifimac.support.Node(position = openwns.Position(0,0,0))
apConfig.transceivers.append(apTransceiver)
ap = nc.createAP(idGen, managerPool, apConfig)
ap.logger.level = commonLoggerLevel
ap.dll.logger.level = dllLoggerLevel
WNS.simulationModel.nodes.append(ap)
apIDs.append(ap.id)
apAdrs.extend(ap.dll.addresses)
rang.dll.addAP(ap)
print "Created AP at (0,0,0) with id ", ap.id, " and addresses ", ap.dll.addresses

#end example

# begin example "wifimac.tutorial.experiment1.config.NodeCreation.STA.node"
# Create Station Transceiver
staConfig = wifimac.support.Transceiver.Station(frequency = networkFrequency,
                                                position = openwns.Position(distance, 0, 0),
                                                scanFrequencies = [networkFrequency],
                                                scanDuration = 0.3)
# Transmission power
staConfig.txPower = dBm(20)
# rate adaptation strategy: PER based
staConfig.layer2.ra.raStrategy = Opportunistic()
# For frames above this threshold (in bit) RTS/CTS will be used
staConfig.layer2.rtsctsThreshold = 8e6

# Create station node
sta = nc.createSTA(idGen, managerPool, config = staConfig)
sta.logger.level = commonLoggerLevel
sta.dll.logger.level = dllLoggerLevel
# end example

# begin example "wifimac.tutorial.experiment1.config.NodeCreation.STA.Traffic"
if(dlIsActive):
    # DL load RANG->STA
    cbrDL = constanze.traffic.Poisson(startDelayDL+random.random()*0.001,
                                        offeredDL,
                                        packetSize,
                                        parentLogger=rang.logger)
    ipBinding = constanze.node.IPBinding(rang.nl.domainName,
                                         sta.nl.domainName,
                                         parentLogger=rang.logger)
    rang.load.addTraffic(ipBinding, cbrDL)

    # Listener at STA for DL
    ipListenerBinding = constanze.node.IPListenerBinding(sta.nl.domainName,
                                                         parentLogger=sta.logger)
    listener = constanze.node.Listener(sta.nl.domainName + ".listener",
                                       probeWindow = 1.0,
                                       parentLogger=sta.logger)
    sta.load.addListener(ipListenerBinding, listener)

if(ulIsActive):
    # UL load STA->RANG
    cbrUL = constanze.traffic.Poisson(startDelayUL+random.random()*0.001,
                                        offeredUL,
                                        packetSize,
                                        parentLogger=sta.logger)
    ipBinding = constanze.node.IPBinding(sta.nl.domainName,
                                         rang.nl.domainName,
                                         parentLogger=sta.logger)
    sta.load.addTraffic(ipBinding, cbrUL)

# IP Route Table
sta.nl.addRoute("192.168.1.0", "255.255.255.0", "0.0.0.0", "wifi")
sta.nl.addRoute(rang.nl.dataLinkLayers[0].addressResolver.address,
                "255.255.255.255",
                rang.nl.dataLinkLayers[0].addressResolver.address,
                "wifi")
rang.nl.addRoute(sta.nl.dataLinkLayers[0].addressResolver.address,
                 "255.255.255.255",
                 sta.nl.dataLinkLayers[0].addressResolver.address,
                 "wifi")
# end example

# begin example "wifimac.tutorial.experiment1.config.NodeCreation.STA.Add"
# Add STA
WNS.simulationModel.nodes.append(sta)
staIDs.append(sta.id)
print "Created STA at (", distance , ", 0, 0) with id ", sta.id
# End create nodes
##################
# end example

# begin example "wifimac.tutorial.experiment1.config.Probing"
#########
# Probing

# wifimac probes
wifimac.evaluation.default.installEvaluation(WNS,
                                             settlingTime,
                                             apIDs, mpIDs, staIDs,
                                             apAdrs, mpAdrs, staIDs,
                                             maxHopCount = 1,
                                             performanceProbes = True, networkProbes = False)

wifimac.evaluation.ip.installEvaluation(sim = WNS,
                                        staIds = staIDs,
                                        rangId = rang.nodeID,
                                        settlingTime = settlingTime,
                                        maxPacketDelay = 0.1,     # s
                                        maxBitThroughput = 1.1*(offeredDL+offeredUL))  # Bit/s

# end example

openwns.setSimulator(WNS)
