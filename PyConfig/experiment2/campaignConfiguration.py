#! /usr/bin/python
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

import sys
import os

# begin example "wifimac.tutorial.experiment2.db.campaignConfiguration.Set"
from openwns.wrowser.simdb.Parameters import AutoSimulationParameters, Parameters, Bool, Int, Float, String
import openwns.wrowser.Configuration as config
import openwns.wrowser.simdb.Database as db
import subprocess

class Set(AutoSimulationParameters):
    # scenario parameters
    simTime = Float(parameterRange = [5.0])
    distance = Float(parameterRange = [25.0])
    ulRatio = Float(parameterRange = [0.0])
    packetSize = Int(parameterRange = [1480*8, 80*8])

    # input parameter
    offeredTraffic = Int(default = 100000)
# end example

# begin example "wifimac.tutorial.experiment2.db.campaignConfiguration.GetTotalThroughput"
def getTotalThroughput(paramsString, inputName, cursor):
    myQuery = " \
       SELECT idResults.scenario_id, idResults." + inputName + ", VAL.mean \
       FROM moments VAL, (SELECT scenario_id, " + inputName + " FROM parameter_sets \
                          WHERE " + paramsString + ") AS idResults \
       WHERE VAL.scenario_id = idResults.scenario_id AND \
       	     VAL.alt_name = 'ip.endToEnd.window.incoming.bitThroughput_Moments' \
       ORDER BY idResults." + inputName + ";"
    cursor.execute(myQuery)
    resultsIn = cursor.fetchall()

    myQuery = " \
       SELECT idResults.scenario_id, idResults." + inputName + ", VAL.mean \
       FROM moments VAL, (SELECT scenario_id, " + inputName + " FROM parameter_sets \
                          WHERE " + paramsString + ") AS idResults \
       WHERE VAL.scenario_id = idResults.scenario_id AND \
             VAL.alt_name = 'ip.endToEnd.window.aggregated.bitThroughput_Moments' \
       ORDER BY idResults." + inputName + ";"
    cursor.execute(myQuery)
    resultsAgg = cursor.fetchall()

    results = []
    for i in zip(resultsAgg, resultsIn):
        agg = i[0]
        inc = i[1]
        assert(agg[0] == inc[0])
        assert(agg[1] == inc[1])
        results.append([agg[0], agg[1], agg[2] + inc[2]])

    return results
# end example

# begin example "wifimac.tutorial.experiment2.db.campaignConfiguration.Cursor"
conf = config.Configuration()
conf.read("./.campaign.conf")
db.Database.connectConf(conf)
cursor = db.Database.getCursor()
# end example

# begin example "wifimac.tutorial.experiment2.db.campaignConfiguration.StartBinarySearch"
params = Set('offeredTraffic', cursor, conf.parser.getint("Campaign", "id"), getTotalThroughput)
[status, results] = params.binarySearch(maxError = 0.1,
                                        exactness = 0.05,
                                        createSimulations=True,
                                        debug=True)
# end example

# begin example "wifimac.tutorial.experiment2.db.campaignConfiguration.CreateNew"
print "%d new / %d waiting / %d finished simulations" %(status['new'],
                                                        status['waiting'],
                                                        status['finished'])
if(status['new'] > 0):
    subprocess.call(['./simcontrol.py --create-scenarios'],
                    shell = True)
    subprocess.call(['./simcontrol.py --execute-locally --restrict-state=NotQueued'],
                    shell = True)
# end example


