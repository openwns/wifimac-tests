import random
random.seed(22)

import dll

import wns
import wns.WNS
import wns.Logger
from wns import dB, dBm, fromdB, fromdBm
from wns.Interval import Interval

import constanze.Constanze
import constanze.Node

import wifimac.support.NodeCreator
import wifimac.support.Config
import wifimac.PathSelection
import wifimac.CapabilityInformationBase
import wifimac.evaluation.default
import wifimac.evaluation.ip

import ofdmaphy.OFDMAPhy

import rise.Scenario

from ip.VirtualARP import VirtualARPServer
from ip.VirtualDHCP import VirtualDHCPServer
from ip.VirtualDNS import VirtualDNSServer

# create an instance of the WNS configuration
# The variable must be called WNS!!!!
WNS = wns.WNS.WNS()
WNS.outputStrategy = wns.WNS.OutputStrategy.DELETE
WNS.maxSimTime = simTime
settlingTime = 3.0
#WNS.masterLogger.backtrace.enabled = True
#WNS.masterLogger.enabled = True
WNS.statusWriteInterval = 120 # in seconds realTime
WNS.probesWriteInterval = 3600 # in seconds realTime

#################
# Create scenario
scenarioXSize = distanceBetweenMPs*(numMPs + 2)
scenarioYSize = verticalDistanceSTAandMP

riseConfig = WNS.modules.rise
riseConfig.debug.transmitter = (commonLoggerLevel > 1)
riseConfig.debug.receiver    = (commonLoggerLevel > 1)
riseConfig.debug.main = (commonLoggerLevel > 1)

ofdmaPhyConfig = WNS.modules.ofdmaPhy
managerPool = wifimac.support.NodeCreator.ManagerPool(xSize = scenarioXSize,
                                                      ySize = scenarioYSize,
                                                      numMeshChannels = 1,
                                                      ofdmaPhyConfig = ofdmaPhyConfig)
# End create scenario
#####################

######################################
# Radio channel propagation parameters
myPathloss = rise.scenario.Pathloss.PyFunction(validFrequencies = Interval(2000, 6000),
                                               validDistances = Interval(2, 5000), # [m]
                                               offset = dB(-27.552219),
                                               freqFactor = 20,
                                               distFactor = 35,
                                               distanceUnit = "m", # nur fuer die Formel, nicht fuer validDistances
                                               minPathloss = dB(42), # pathloss at 2m distance
                                               outOfMinRange = rise.scenario.Pathloss.Constant("42 dB"), #Pathloss.FreeSpace(),
                                               outOfMaxRange = rise.scenario.Pathloss.Deny(),
                                               scenarioWrap = False,
                                               sizeX = scenarioXSize,
                                               sizeY = scenarioYSize)
#myShadowing = rise.scenario.Shadowing.SpatialCorrelated(shadowSigma=5, correlationDistance=50)
myShadowing = rise.scenario.Shadowing.No()
myFastFading = rise.scenario.FastFading.No()
propagationConfig = rise.scenario.Propagation.Configuration(pathloss = myPathloss, shadowing = myShadowing, fastFading = myFastFading)
# End radio channel propagation parameters
##########################################

###################################
#Create nodes using the NodeCreator
nc = wifimac.support.NodeCreator.NodeCreator(propagationConfig)

# one RANG
rang = nc.createRANG()
rang.logger.level = commonLoggerLevel
if(ulIsActive):
    # The RANG only has one IPListenerBinding that is attached
    # to the listener. The listener is the only traffic sink
    # within the RANG
    ipListenerBinding = constanze.Node.IPListenerBinding(rang.nl.domainName, parentLogger=rang.logger)
    listener = constanze.Node.Listener(rang.nl.domainName + ".listener", probeWindow = 0.1, parentLogger=rang.logger)
    rang.load.addListener(ipListenerBinding, listener)
    rang.nl.windowedEndToEndProbe.config.windowSize = 2.0
    rang.nl.windowedEndToEndProbe.config.sampleInterval = 0.5
WNS.nodes.append(rang)

# create (magic) service nodes
# One virtual ARP Zone
varp = VirtualARPServer("VARP", "theOnlyZone")
varp.logger.level = commonLoggerLevel
WNS.nodes.append(varp)

# One virtual DNS server
vdns = VirtualDNSServer("VDNS", "ip.DEFAULT.GLOBAL")
vdns.logger.level = commonLoggerLevel
WNS.nodes.append(vdns)

# One virtual pathselection server
vps = wifimac.PathSelection.VirtualPSServer("VPS", numNodes = (numSTAs + (numMPs+2)*2 + 1))
vps.logger.level = commonLoggerLevel
WNS.nodes.append(vps)

# One virtual capability information base server
vcibs = wifimac.CapabilityInformationBase.VirtualCababilityInformationService("VCIB")
vcibs.logger.level = commonLoggerLevel
WNS.nodes.append(vcibs)

# Single instance of id-generator for all nodes with ids
idGen = wifimac.support.NodeCreator.idGenerator()

# save IDs for probes
apIDs = []
mpIDs = []
staIDs = []
apAdrs = []
mpAdrs = []

# selection of the BSS-frequency: iterating over the BSS-set
bssCount = 0

# One AP at the beginning
apConfig = wifimac.support.Config.Node(position = wns.Position(distanceBetweenMPs/2, 0, 0))
apConfig.transceivers.append(MyBSSTransceiver(beaconDelay = 0.001, frequency = bssFrequencies[bssCount % len(bssFrequencies)]))
apConfig.transceivers.append(MyMeshTransceiver(beaconDelay = 0.001, frequency = meshFrequency))
ap = nc.createAP(idGen = idGen,
                 managerPool = managerPool,
                 config = apConfig)
ap.logger.level = commonLoggerLevel
ap.dll.logger.level = dllLoggerLevel
WNS.nodes.append(ap)
apIDs.append(ap.id)
apAdrs.extend(ap.dll.addresses)
rang.dll.addAP(ap)
print "Created AP at (", distanceBetweenMPs/2, ", 0, 0) with id ", ap.id, " and addresses ", ap.dll.addresses

# Create MPs
for i in xrange(numMPs):
    bssCount+=1
    mpConfig = wifimac.support.Config.Node(position = wns.Position(distanceBetweenMPs/2+distanceBetweenMPs*(i+1), 0, 0))
    mpConfig.transceivers.append(MyBSSTransceiver(beaconDelay = 0.001*(i+2), frequency = bssFrequencies[bssCount % len(bssFrequencies)]))
    mpConfig.transceivers.append(MyMeshTransceiver(beaconDelay = 0.001*(i+2), frequency = meshFrequency))
    mp = nc.createMP(idGen = idGen,
                     managerPool = managerPool,
                     config = mpConfig)
    mp.logger.level = commonLoggerLevel
    mp.dll.logger.level = dllLoggerLevel
    WNS.nodes.append(mp)
    mpIDs.append(mp.id)
    mpAdrs.extend(mp.dll.addresses)
    print "Created MP at (", distanceBetweenMPs/2+distanceBetweenMPs*(i+1), ", 0, 0) with id ", mp.id, " and addresses ", mp.dll.addresses

# Create Last AP at the end
if(numAPs > 1):
    bssCount+=1
    apConfig = wifimac.support.Config.Node(position = wns.Position(distanceBetweenMPs/2+distanceBetweenMPs*(numMPs+1), 0, 0))
    apConfig.transceivers.append(MyBSSTransceiver(beaconDelay = 0.001*(numMPs+3), frequency = bssFrequencies[bssCount % len(bssFrequencies)]))
    apConfig.transceivers.append(MyMeshTransceiver(beaconDelay = 0.001*(numMPs+3), frequency = meshFrequency))
    ap = nc.createAP(idGen = idGen,
                     managerPool = managerPool,
                     config = apConfig)
    ap.logger.level = commonLoggerLevel
    ap.dll.logger.level = dllLoggerLevel
    WNS.nodes.append(ap)
    apIDs.append(ap.id)
    apAdrs.extend(ap.dll.addresses)
    rang.dll.addAP(ap)
    print "Created AP at (", distanceBetweenMPs/2+distanceBetweenMPs*(numMPs+1), ", 0, 0) with id ", ap.id, " and addresses ", ap.dll.addresses

# Create STAs in equidistance spread out over scenario
if(numSTAs > 1):
    staDist = scenarioXSize/(numSTAs-1)
else:
    staDist = 1

for j in xrange(numSTAs):
    staConfig = MySTAConfig(initFrequency = bssFrequencies[0],
                            position = wns.Position(staDist*j,verticalDistanceSTAandMP,0),
                            scanFrequencies = bssFrequencies,
                            scanDurationPerFrequency = 0.3)

    sta = nc.createSTA(idGen, managerPool, config = staConfig)
    sta.logger.level = commonLoggerLevel
    sta.dll.logger.level = dllLoggerLevel
    print "Created STA at (", staDist*j, ", ", verticalDistanceSTAandMP, ", 0) with id ", sta.id

    if(dlIsActive):
        # DL load RANG->STA
        cbrDL = constanze.Constanze.CBR(startDelayDL+random.random()*0.001, offeredDL, meanPacketSize, parentLogger=rang.logger)
        ipBinding = constanze.Node.IPBinding(rang.nl.domainName, sta.nl.domainName, parentLogger=rang.logger)
        rang.load.addTraffic(ipBinding, cbrDL)

        # Listener at STA for DL
        ipListenerBinding = constanze.Node.IPListenerBinding(sta.nl.domainName, parentLogger=sta.logger)
        listener = constanze.Node.Listener(sta.nl.domainName + ".listener", probeWindow = 0.1, parentLogger=sta.logger)
        sta.load.addListener(ipListenerBinding, listener)

    if(ulIsActive):
        # UL load STA->RANG
        cbrUL = constanze.Constanze.CBR(startDelayUL+random.random()*0.001, offeredUL, meanPacketSize, parentLogger=sta.logger)
        ipBinding = constanze.Node.IPBinding(sta.nl.domainName, rang.nl.domainName, parentLogger=sta.logger)
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

    # Add STA
    WNS.nodes.append(sta)
    staIDs.append(sta.id)
# End create nodes
##################


#########
# Probing

# wifimac probes
# Deactivated probes: system-test seems not to recognize probes by probe-bus?
wifimac.evaluation.default.installEvaluation(WNS, settlingTime, apIDs, mpIDs, staIDs, apAdrs, mpAdrs, staIDs, maxHopCount = numMPs+1, performanceProbes = True, networkProbes = False)

wifimac.evaluation.ip.installEvaluation(sim = WNS,
                                        nodeIds = [rang.nodeID],
                                        settlingTime = settlingTime,
                                        maxPacketDelay = 0.1,     # s
                                        maxBitThroughput = (numSTAs+1)*(offeredDL+offeredUL))  # Bit/s
