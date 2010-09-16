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
from wifimac.lowerMAC.RateAdaptation import PER, Constant, SINR
import wifimac.convergence.PhyMode

#######################
# Simulation parameters
#
# Simulation of the string topology: all nodes are placed equidistantly
# on a string, on each end of the string, an AP is positioned
# Traffic is either DL only or bidirectional
#
##from SimConfig import params
class Params:
    offered = 50e6
    raStrategy = "Constant"
    rtscts = True
    wallAttenuation = 100
    wall13 = True
    wall14 = False
    wall23 = True
    wall24 = False

params = Params()

simTime =  0.1
settlingTime = 2.0
commonLoggerLevel = 1
dllLoggerLevel = 2

# load
meanPacketSize = 1480 * 8
offered = params.offered
startDelay = 1.0
# End simulation parameters
###########################

####################
# Node configuration

# configuration class for AP and MP mesh transceivers
class MyMeshTransceiver(wifimac.support.Transceiver.Mesh):
    def __init__(self, beaconDelay):
        super(MyMeshTransceiver, self).__init__(5500)
        # changes to the default config
        self.layer2.beacon.delay = beaconDelay

        if(params.rtscts):
            self.layer2.rtsctsThreshold = 800
        else:
            self.layer2.rtsctsThreshold = 1e6*8
        self.layer2.txop.txopLimit = 0.00

        if(params.raStrategy == 'Constant'):
            self.layer2.ra.raStrategy = Constant(wifimac.convergence.PhyMode.makeBasicPhyMode("QAM64", "3/4", dB(24.8)))
        elif(params.raStrategy == 'PER'):
            self.layer2.ra.raStrategy = PER()
        elif(params.raStrategy == 'SINR'):
            self.layer2.ra.raStrategy = SINR()

# End node configuration
########################

import random
random.seed(22)

import dll

import openwns
import openwns.logger
from openwns.geometry import Position
from openwns import dB, dBm, fromdB, fromdBm
from openwns.interval import Interval

import constanze.traffic
import constanze.node

import wifimac.support
import wifimac.evaluation.default
import wifimac.evaluation.ip

import ofdmaphy.OFDMAPhy

import rise.Scenario

# create an instance of the WNS configuration
# The variable must be called WNS!!!!
WNS = openwns.Simulator(simulationModel = openwns.node.NodeSimulationModel())
WNS.outputStrategy = openwns.simulator.OutputStrategy.DELETE
WNS.maxSimTime = simTime
WNS.statusWriteInterval = 120 # in seconds realTime
WNS.probesWriteInterval = 3600 # in seconds realTime

#################
# Create scenario
sizeX = 15
sizeY = 15
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
objs = []
wallAttenuation = dB(params.wallAttenuation)
if(params.wall13):
    objs.append(rise.scenario.Shadowing.LineSegment(Position(0.0, 6.0, 0.0),
                                                    Position(2.0, 6.0, 0.0),
                                                    attenuation = wallAttenuation))
if(params.wall24):
    objs.append(rise.scenario.Shadowing.LineSegment(Position(10.0, 6.0, 0.0),
                                                    Position(12.0, 6.0, 0.0),
                                                    attenuation = wallAttenuation))
if(params.wall23):
    objs.append(rise.scenario.Shadowing.LineSegment(Position(8.0, 2.0, 0.0),
                                                    Position(10.0, 4.0, 0.0),
                                                    attenuation = wallAttenuation))
if(params.wall14):
    objs.append(rise.scenario.Shadowing.LineSegment(Position(4.0, 2.0, 0.0),
                                                    Position(2.0, 4.0, 0.0),
                                                    attenuation = wallAttenuation))
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
myShadowing = rise.scenario.Shadowing.Objects(obstructionList = objs)
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
rang = nc.createRANG(listener = False, loggerLevel = commonLoggerLevel)
WNS.simulationModel.nodes.append(rang)

# create (magic) service nodes for ARP, DNS, Pathselection, Capability Information
WNS.simulationModel.nodes.append(nc.createVARP(commonLoggerLevel))
WNS.simulationModel.nodes.append(nc.createVDNS(commonLoggerLevel))
vps = nc.createVPS(5, 2)#commonLoggerLevel)
vps.vps.preKnowledge.alpha = 0.999
vps.vps.preKnowledge.add(1, 4, 1000)
vps.vps.preKnowledge.add(4, 1, 1000)
vps.vps.preKnowledge.add(3, 2, 1000)
vps.vps.preKnowledge.add(2, 3, 1000)
vps.vps.preKnowledge.add(4, 2, 1000)
vps.vps.preKnowledge.add(2, 4, 1000)
WNS.simulationModel.nodes.append(vps)
WNS.simulationModel.nodes.append(nc.createVCIB(commonLoggerLevel))

# Single instance of id-generator for all nodes with ids
idGen = wifimac.support.idGenerator()

# save IDs for probes
apIDs = []
mpIDs = []
staIDs = []
apAdrs = []
mpAdrs = []

# selection of the BSS-frequency: iterating over the BSS-set
bssCount = 0

# One AP at (1,1)
apConfig = wifimac.support.Node(position = Position(1, 1, 0))
apConfig.transceivers.append(MyMeshTransceiver(beaconDelay = 0.001))
ap = nc.createAP(idGen = idGen, managerPool = managerPool, config = apConfig)
ap.logger.level = commonLoggerLevel
ap.dll.logger.level = dllLoggerLevel
WNS.simulationModel.nodes.append(ap)
apIDs.append(ap.id)
apAdrs.extend(ap.dll.addresses)
rang.dll.addAP(ap)

# One MP at (11, 1), traffic from (1,1)
mpConfig = wifimac.support.Node(position = Position(11, 1, 0))
mpConfig.transceivers.append(MyMeshTransceiver(beaconDelay = 0.002))
mp = nc.createMP(idGen = idGen, managerPool = managerPool, config = mpConfig)
mp.logger.level = commonLoggerLevel
mp.dll.logger.level = dllLoggerLevel
dl = constanze.traffic.Poisson(startDelay+random.random()*0.001, offered, meanPacketSize, parentLogger=rang.logger)
ipBinding = constanze.node.IPBinding(rang.nl.domainName, mp.nl.domainName, parentLogger=rang.logger)
rang.load.addTraffic(ipBinding, dl)
ipListenerBinding = constanze.node.IPListenerBinding(mp.nl.domainName, parentLogger=mp.logger)
listener = constanze.node.Listener(mp.nl.domainName + ".listener", probeWindow = 0.1, parentLogger=mp.logger)
mp.load.addListener(ipListenerBinding, listener)
# IP Route Table
mp.nl.addRoute("192.168.1.0", "255.255.255.0", "0.0.0.0", "wifi")
mp.nl.addRoute(rang.nl.dataLinkLayers[0].addressResolver.address,
               "255.255.255.255",
               rang.nl.dataLinkLayers[0].addressResolver.address,
               "wifi")
rang.nl.addRoute(mp.nl.dataLinkLayers[0].addressResolver.address,
                 "255.255.255.255",
                 mp.nl.dataLinkLayers[0].addressResolver.address,
                 "wifi")
staIDs.append(mp.id)
WNS.simulationModel.nodes.append(mp)
mpIDs.append(mp.id)
mpAdrs.extend(mp.dll.addresses)

# One AP at (1,11)
apConfig = wifimac.support.Node(position = Position(1, 11, 0))
apConfig.transceivers.append(MyMeshTransceiver(beaconDelay = 0.003))
ap = nc.createAP(idGen = idGen, managerPool = managerPool, config = apConfig)
ap.logger.level = commonLoggerLevel
ap.dll.logger.level = dllLoggerLevel
WNS.simulationModel.nodes.append(ap)
apIDs.append(ap.id)
apAdrs.extend(ap.dll.addresses)
rang.dll.addAP(ap)

# One MP at (11, 11), traffic from (1,11)
mpConfig = wifimac.support.Node(position = Position(11, 11, 0))
mpConfig.transceivers.append(MyMeshTransceiver(beaconDelay = 0.004))
mp = nc.createMP(idGen = idGen, managerPool = managerPool, config = mpConfig)
mp.logger.level = commonLoggerLevel
mp.dll.logger.level = dllLoggerLevel
dl = constanze.traffic.Poisson(startDelay+random.random()*0.001, offered, meanPacketSize, parentLogger=rang.logger)
ipBinding = constanze.node.IPBinding(rang.nl.domainName, mp.nl.domainName, parentLogger=rang.logger)
rang.load.addTraffic(ipBinding, dl)
ipListenerBinding = constanze.node.IPListenerBinding(mp.nl.domainName, parentLogger=mp.logger)
listener = constanze.node.Listener(mp.nl.domainName + ".listener", probeWindow = 0.1, parentLogger=mp.logger)
mp.load.addListener(ipListenerBinding, listener)
# IP Route Table
mp.nl.addRoute("192.168.1.0", "255.255.255.0", "0.0.0.0", "wifi")
mp.nl.addRoute(rang.nl.dataLinkLayers[0].addressResolver.address,
               "255.255.255.255",
               rang.nl.dataLinkLayers[0].addressResolver.address,
               "wifi")
rang.nl.addRoute(mp.nl.dataLinkLayers[0].addressResolver.address,
                 "255.255.255.255",
                 mp.nl.dataLinkLayers[0].addressResolver.address,
                 "wifi")
staIDs.append(mp.id)
WNS.simulationModel.nodes.append(mp)
mpIDs.append(mp.id)
mpAdrs.extend(mp.dll.addresses)



# End create nodes
##################

#########
# Probing

# wifimac probes
from openwns.evaluation import *
node = openwns.evaluation.createSourceNode(WNS, 'ip.endToEnd.window.incoming.bitThroughput')
node.appendChildren(SettlingTimeGuard(settlingTime))
node.getLeafs().appendChildren(Separate(by = 'MAC.Id', forAll = mpIDs, format = 'Node%d'))
node.getLeafs().appendChildren(Moments(name = 'ip.endToEnd.window.incoming.bitThroughput',
                                       description = "Throughput (incoming) [bit/s]"))

node = openwns.evaluation.createSourceNode(WNS, 'ip.endToEnd.window.aggregated.bitThroughput')
node.appendChildren(SettlingTimeGuard(settlingTime))
node.getLeafs().appendChildren(Accept(by = 'wns.node.Node.id', ifIn = [rang.nodeID]))
node.getLeafs().appendChildren(Moments(name = 'ip.endToEnd.window.aggregated.bitThroughput',
                                       description = "Throughput (aggregated) [bit/s]"))


wifimac.evaluation.default.installEvaluation(WNS,
                                             settlingTime,
                                             apIDs, mpIDs, staIDs,
                                             apAdrs, mpAdrs, staIDs,
                                             maxHopCount = 1,
                                             performanceProbes = True,
                                             networkProbes = True,
                                             draftNProbes = False)

openwns.setSimulator(WNS)

