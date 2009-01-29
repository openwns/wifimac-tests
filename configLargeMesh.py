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
import math

import wns.WNS
import wns.Logger
from wns import dB, dBm, fromdB, fromdBm

import constanze.Constanze
import constanze.Node

import wifimac.support
import wifimac.support.ScenarioFile
import wifimac.support.MRMCResult
import wifimac.support.Transceiver
import wifimac.pathselection
import wifimac.management.InformationBases
import wifimac.evaluation.default
import wifimac.evaluation.ip

import ofdmaphy.OFDMAPhy

import rise.Scenario

import ip.VirtualARP
#import ip.VirtualDHCP
import ip.VirtualDNS

#######################
# Simulation parameters
#from SimConfig import params

simTime = 25.5
settlingTime = 5.0#min(simTime/3.0+1.0, simTime-2.0)
commonLoggerLevel = 1
dllLoggerLevel = 2

# ratio of MPs/APs (upper bound, the actual ratio will be the highest possible value below)
MPsPerAP = 10.0#params.mpsPerAP

scenarioNumber = 1#params.scenarioNumber
reducedSize = 1000#params.scenarioSize

# load
meanPacketSize = 1480*8#params.packetSize
numSTAs = 64#params.numberOfSTAs
offered = 250000#params.offeredTraffic
ratioUL = 0.1#params.ratioUL
startDelay = 1.0

# Frequency planning
numMeshTransceivers = 1#params.numMeshTransceivers
numMeshFrequencies = 1#params.numMeshFrequencies
meshFrequencies = range(5500, 5500+20*numMeshFrequencies, 20)
bssFrequencies = [2400, 2440, 2480]
# End simulation parameters
###########################

rtscts = True

####################
# Node configuration

# configuration class for AP and MP mesh transceivers
class MyMeshTransceiver(wifimac.support.Transceiver.Mesh):
    def __init__(self, beaconDelay, frequency):
        super(MyMeshTransceiver, self).__init__(frequency)
        # changes to the default config
        self.layer2.beacon.delay = beaconDelay
        self.layer2.ra.raStrategy = 'SINR'
        if(rtscts):
            self.layer2.rtsctsThreshold = 8*800
        else:
            self.layer2.rtsctsThreshold = 800000000
        self.layer2.txop.txopLimit = 0.0#params.txopLimit
        self.layer2.rtscts.rtsctsOnTxopData = True
        self.layer2.bufferSize = 50
        self.layer2.bufferSizeUnit = 'PDU'
        self.layer2.manager.numAntennas = 1#params.numAntenn

# configuration class for AP and MP BSS transceivers
class MyBSSTransceiver(wifimac.support.Transceiver.Mesh):
    def __init__(self, beaconDelay, frequency):
        super(MyBSSTransceiver, self).__init__(frequency)
        self.layer2.beacon.delay = beaconDelay
        self.layer2.ra.raStrategy = 'SINR'
        if(rtscts):
            self.layer2.rtsctsThreshold = 8*800
        else:
            self.layer2.rtsctsThreshold = 800000000
        self.layer2.txop.txopLimit = 0.0#params.txopLimit
        self.layer2.rtscts.rtsctsOnTxopData = True
        self.layer2.bufferSize = 25
        self.layer2.bufferSizeUnit = 'PDU'
        self.layer2.manager.numAntennas = 1#params.numAntennas
        self.txPower = dBm(30)

# configuration class for STAs
class MySTAConfig(wifimac.support.Transceiver.Station):
    def __init__(self, initFrequency, position, scanFrequencies, scanDurationPerFrequency):
        super(MySTAConfig, self).__init__(frequency = initFrequency,
                                          position = position,
                                          scanFrequencies = scanFrequencies,
                                          scanDuration = scanDurationPerFrequency)
        self.layer2.ra.raStrategy = 'SINR'
        if(rtscts):
            self.layer2.rtsctsThreshold = 8*800
        else:
            self.layer2.rtsctsThreshold = 800000000
#        self.layer2.rtsctsThreshold = 800*8#params.rstctsThreshold
        self.txPower = dBm(30)

# End node configuration
########################


# create an instance of the WNS configuration
# The variable must be called WNS!!!!
WNS = wns.WNS.WNS()
WNS.outputStrategy = wns.WNS.OutputStrategy.DELETE
WNS.maxSimTime = simTime
#WNS.masterLogger.backtrace.enabled = True
#WNS.masterLogger.enabled = True
WNS.statusWriteInterval = 30+int(random.random()*30) # in seconds realTime
WNS.probesWriteInterval = 3600 # in seconds realTime

#################
# Create scenario
scen = wifimac.support.ScenarioFile.PredefScenario('./scenarioData.pkl', scenarioNumber, debug=True)

riseConfig = WNS.modules.rise
riseConfig.debug.transmitter = (commonLoggerLevel > 1)
riseConfig.debug.receiver    = (commonLoggerLevel > 1)
riseConfig.debug.main = (commonLoggerLevel > 1)

ofdmaPhyConfig = WNS.modules.ofdmaPhy
managerPool = wifimac.support.ChannelManagerPool(scenario = rise.Scenario.Scenario(scen.desc.sizeX, scen.desc.sizeY),
                                                 numMeshChannels = len(meshFrequencies),
                                                 ofdmaPhyConfig = ofdmaPhyConfig)
# End create scenario
#####################

######################################
# Radio channel propagation parameters
myPathloss = scen.desc.pathlossFunction
myShadowing = scen.desc.shadowingFunction
myFastFading = scen.desc.fastFadingFunction
propagationConfig = rise.scenario.Propagation.Configuration(pathloss = myPathloss, shadowing = myShadowing, fastFading = myFastFading)
# End radio channel propagation parameters
##########################################

###################################
#Create nodes using the NodeCreator
nc = wifimac.support.NodeCreator(propagationConfig)

posList = scen.desc.apPos
apPrefList = scen.desc.apPrefList
maxPathLength = scen.desc.maxPathLength
avgPathLength = scen.desc.avgPathLength

# Multi-Radio Multi-Channel Configuration
print "mrmc with %f mpsPerAP, %d transceivers, scenario %d" %(MPsPerAP, numMeshTransceivers, scenarioNumber)
if(MPsPerAP > 0) and (numMeshTransceivers > 1):
    mrmc = wifimac.support.MRMCResult.MRMCLoader('/net/beast1/SMX/smx/SimPlayground/MRMC/mrmcResults.pkl', mpsPerAP = MPsPerAP, numTransceivers = numMeshTransceivers, scenarioId = scenarioNumber)
    valid = False
    while not valid:
        try:
            mrmc.setFrequencies(meshFrequencies)
        except wifimac.support.MRMCResult.MRMCNoMatchingChannelNumber:
            meshFrequencies = meshFrequencies[1:]
            print "Reducing mesh frequencies to", meshFrequencies
        else:
            valid = True

    mrmc.printOverview()
    assert(mrmc.getNumChannels() == len(meshFrequencies))

# one RANG
rang = nc.createRANG()
rang.logger.level = dllLoggerLevel
if(ratioUL > 0):
    # The RANG only has one IPListenerBinding that is attached
    # to the listener. The listener is the only traffic sink
    # within the RANG
    ipListenerBinding = constanze.Node.IPListenerBinding(
        rang.nl.domainName, parentLogger=rang.logger)
    listener = constanze.Node.Listener(
        rang.nl.domainName + ".listener", probeWindow = 0.1, parentLogger=rang.logger)
    rang.load.addListener(ipListenerBinding, listener)
    rang.nl.windowedEndToEndProbe.config.windowSize = 1.0
    rang.nl.windowedEndToEndProbe.config.sampleInterval = 0.5
WNS.nodes.append(rang)

# create (magic) service nodes
# One virtual ARP Zone
varp = ip.VirtualARP.VirtualARPServer("VARP", "theOnlyZone")
varp.logger.level = commonLoggerLevel
WNS.nodes.append(varp)

# One virtual DNS server
vdns = ip.VirtualDNS.VirtualDNSServer("VDNS", "ip.DEFAULT.GLOBAL")
vdns.logger.level = commonLoggerLevel
WNS.nodes.append(vdns)

# One virtual pathselection server
vps = wifimac.pathselection.VirtualPSServer("VPS", numNodes = numSTAs + (len(posList)*(len(meshFrequencies)+1))+1)
vps.logger.level = dllLoggerLevel
WNS.nodes.append(vps)

# One virtual capability information base server
vcibs = wifimac.management.InformationBases.VirtualCababilityInformationService("VCIB")
vcibs.logger.level = commonLoggerLevel
WNS.nodes.append(vcibs)

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

# Create AP(s)
# At least one, at most such that the ratio MPs/(MPs+APs) is above the given parameter
while(len(posList)*1.0/(MPsPerAP+1) > len(apIDs)):
    # create AP configuration
    apConfig = wifimac.support.Node(position = wns.Position(posList[apPrefList[len(apIDs)]][0], posList[apPrefList[len(apIDs)]][1], 0))
    # add BSS transceiver
    apConfig.transceivers.append(MyBSSTransceiver(beaconDelay = 0.001*(len(apIDs)+1+random.random()),
                                                  frequency = bssFrequencies[bssCount % len(bssFrequencies)]))
    # add mesh transceivers, one for each frequency
    if(MPsPerAP > 0):
        if(numMeshTransceivers > 1):
            # No mesh, no mesh transceivers
            for f in mrmc.getFrequenciesForNode(bssCount):
                apConfig.transceivers.append(MyMeshTransceiver(beaconDelay = 0.001*(len(apIDs)+1+random.random()),
                                                               frequency = f))
        else:
            assert(numMeshFrequencies == 1)
            apConfig.transceivers.append(MyMeshTransceiver(beaconDelay = 0.001*(len(apIDs)+1+random.random()),
                                                           frequency = meshFrequencies[0]))

    # create AP instance with config
    ap = nc.createAP(idGen, managerPool, apConfig)
    ap.logger.level = commonLoggerLevel
    ap.dll.logger.level = dllLoggerLevel
    WNS.nodes.append(ap)
    apIDs.append(ap.id)
    apAdrs.extend(ap.dll.addresses)
    rang.dll.addAP(ap)

    bssCount += 1

print "Created", len(apIDs), "APs"

# Create MPs
for i in xrange(len(apIDs), len(posList)):
    if(numMeshTransceivers > 1) and (len(mrmc.getFrequenciesForNode(bssCount)) == 0):
        continue
    mpConfig = wifimac.support.Node(position = wns.Position(posList[apPrefList[i]][0], posList[apPrefList[i]][1], 0))
    mpConfig.transceivers.append(MyBSSTransceiver(beaconDelay = 0.001*(i+1+random.random()),
                                                  frequency = bssFrequencies[bssCount % len(bssFrequencies)]))
    if(numMeshTransceivers > 1):
        for f in mrmc.getFrequenciesForNode(bssCount):
            mpConfig.transceivers.append(MyMeshTransceiver(beaconDelay = 0.001*(i+1+random.random()),
                                                           frequency = f))
    else:
        mpConfig.transceivers.append(MyMeshTransceiver(beaconDelay = 0.001*(i+1+random.random()),
                                                       frequency = meshFrequencies[0]))

    mp = nc.createMP(idGen, managerPool, mpConfig)
    mp.logger.level = commonLoggerLevel
    mp.dll.logger.level = dllLoggerLevel
    WNS.nodes.append(mp)
    mpIDs.append(mp.id)
    mpAdrs.extend(mp.dll.addresses)

    bssCount+=1
print "Created %d MPs, ratio is %f" % (len(mpIDs),  len(mpIDs)*1.0/len(apIDs))

# Create STAs
sizeX = min(reducedSize, scen.desc.sizeX)
sizeY = min(reducedSize, scen.desc.sizeY)
assert(sizeX == sizeY)

stasPerLine = math.ceil(math.sqrt(numSTAs))
gridDist = sizeX/stasPerLine
# start in lower left corner
gridX = gridDist/2+(scen.desc.sizeX-min(reducedSize,scen.desc.sizeX))/2
gridY = gridDist/2+(scen.desc.sizeY-min(reducedSize,scen.desc.sizeY))/2
lineCount = 0

for i in xrange(numSTAs):
    staConfig = MySTAConfig(initFrequency = bssFrequencies[0],
                            position = wns.Position(gridX, gridY, 0),
                            scanFrequencies = bssFrequencies,
                            scanDurationPerFrequency = 0.3)
    sta = nc.createSTA(idGen, managerPool, config = staConfig)
    sta.logger.level = commonLoggerLevel
    sta.dll.logger.level = dllLoggerLevel

    lineCount+=1
    if(lineCount == stasPerLine):
        # full line, advance gridX
        gridY = gridDist/2+(scen.desc.sizeY-min(reducedSize, scen.desc.sizeY))/2
        gridX += gridDist
        #assert(gridX < scen.desc.sizeX)
        lineCount = 0
    else:
        gridY += gridDist
        assert(gridY < scen.desc.sizeX)


    sta.logger.level = commonLoggerLevel
    sta.dll.logger.level = dllLoggerLevel

    if ((settlingTime-startDelay-1.0) > 0):
        delayTraffic = startDelay + (settlingTime-startDelay-1.0)*random.random()
    else:
        delayTraffic = startDelay + 0.1*random.random()

    # DL RANG->STA
    if (ratioUL < 1.0):
        DL = constanze.Constanze.Poisson(delayTraffic, offered*(1.0-ratioUL), meanPacketSize, parentLogger=rang.logger)
        ipBinding = constanze.Node.IPBinding(rang.nl.domainName, sta.nl.domainName, parentLogger=rang.logger)
        rang.load.addTraffic(ipBinding, DL)

        # Listener at STA
        ipListenerBinding = constanze.Node.IPListenerBinding(sta.nl.domainName, parentLogger=sta.logger)
        listener = constanze.Node.Listener(sta.nl.domainName + ".listener", probeWindow = 0.1, parentLogger=sta.logger)
        sta.load.addListener(ipListenerBinding, listener)

    # UL load STA->RANG
    if(ratioUL > 0.0):
        # UL load STA->RANG
        UL = constanze.Constanze.Poisson(delayTraffic+0.01, offered*ratioUL, meanPacketSize, parentLogger=sta.logger)
        ipBinding = constanze.Node.IPBinding(sta.nl.domainName, rang.nl.domainName, parentLogger=sta.logger)
        sta.load.addTraffic(ipBinding, UL)

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

    # Add STA
    WNS.nodes.append(sta)
    staIDs.append(sta.id)

print "Created %d STAs, last one at pos %d/%d" % (len(staIDs), gridX, gridY)

# End create nodes
##################


#########
# Probing

# wifimac probes
# Deactivated probes: system-test seems not to recognize probes by probe-bus?
wifimac.evaluation.default.installEvaluation(WNS, settlingTime,
                                             apIDs, mpIDs, staIDs,
                                             apAdrs, mpAdrs, staIDs,
                                             maxHopCount = int(maxPathLength[1:][len(apIDs)-1])+1,
                                             performanceProbes = True,
                                             networkProbes = False)

wifimac.evaluation.ip.installEvaluation(sim = WNS,
                                        staIds = staIDs,
                                        rangId = rang.nodeID,
                                        settlingTime = settlingTime,
                                        maxPacketDelay = 0.1,     # s
                                        maxBitThroughput = (numSTAs+1)*(offered))  # Bit/s

print "maxHopCount here: ", int(maxPathLength[1:][len(apIDs)-1])+1

