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

# begin example "wifimac.tutorial.experiment1.campaignConfiguration.import"
from wrowser.simdb.Parameters import Parameters, Bool, Int, Float, String
# end example

# begin example "wifimac.tutorial.experiment1.campaignConfiguration.Set"
class Set(Parameters):
    simTime = Float()
    distance = Float()
    ulRatio = Float()
    offeredTraffic = Int()
# end example

# begin example "wifimac.tutorial.experiment1.campaignConfiguration.params"
params = Set()
# end example

# begin example "wifimac.tutorial.experiment1.campaignConfiguration.population"
params.simTime = 5.0
params.distance = 25.0
params.ulRatio = 0.0

for i in xrange(1, 11):
    params.offeredTraffic = i * 1000000
    params.write()
# end example
