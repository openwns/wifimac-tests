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

# this is needed, so that the script can be called from everywhere
import os
import sys
base, tail = os.path.split(sys.argv[0])
os.chdir(base)

# Append the python sub-dir of WNS--main--x.y ...
sys.path.append(os.path.join('..', '..', '..', 'sandbox', 'default', 'lib', 'python2.4', 'site-packages'))

# ... because the module WNS unit test framework is located there.
import pywns.WNSUnit

disabled = []
for arg in sys.argv[1:]:
    disabled.append(int(arg))

testSuite = pywns.WNSUnit.TestSuite()

# create a system test
testSuite.addTest(pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                                configFile = 'config.py',
                                                runSimulations = True,
                                                shortDescription = '1AP, 1 STA, overload DL w RTS/CTS',
                                                requireReferenceOutput = True,
                                                disabled = (1 in disabled),
                                                disabledReason = "Disabled by command-line switch"))

testSuite.addTest(pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                                configFile = 'configSmallMesh.py',
                                                runSimulations = True,
                                                shortDescription = '2APs/1MPs network with 3 STAs',
                                                requireReferenceOutput = True,
                                                disabled = (2 in disabled),
                                                disabledReason = "Disabled by command-line switch"))

testSuite.addTest(pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                                configFile = 'configActiveMP.py',
                                                runSimulations = True,
                                                shortDescription = '1AP/1MP/1STA, MP and STA send/receive traffic',
                                                requireReferenceOutput = True,
                                                disabled = (3 in disabled),
                                                disabledReason = "Disabled by command-line switch"))

testSuite.addTest(pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                                configFile = 'config.py',
                                                runSimulations = True,
                                                shortDescription = 'WiFiMAC-Tutorial: Experiment 1',
                                                requireReferenceOutput = True,
                                                disabled = (4 in disabled),
                                                disabledReason = "Disabled by command-line switch",
                                                workingDir = "PyConfig/experiment1"))

testSuite.addTest(pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                                configFile = 'config.py',
                                                runSimulations = True,
                                                shortDescription = 'WiFiMAC-Tutorial: Experiment 3',
                                                requireReferenceOutput = True,
                                                disabled = (5 in disabled),
                                                disabledReason = "Disabled by command-line switch",
                                                workingDir = "PyConfig/experiment3"))

testSuite.addTest(pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                                configFile = 'config.py',
                                                runSimulations = True,
                                                shortDescription = 'WiFiMAC-Tutorial: Experiment 4',
                                                requireReferenceOutput = True,
                                                disabled = (6 in disabled),
                                                disabledReason = "Disabled by command-line switch",
                                                workingDir = "PyConfig/experiment4"))

testSuite.addTest(pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                                configFile = 'config.py',
                                                runSimulations = True,
                                                shortDescription = 'WiFiMAC-Tutorial: Experiment 5',
                                                requireReferenceOutput = True,
                                                disabled = (7 in disabled),
                                                disabledReason = "Disabled by command-line switch",
                                                workingDir = "PyConfig/experiment5"))

testSuite.addTest(pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                                configFile = 'config.py',
                                                runSimulations = True,
                                                shortDescription = 'WiFiMAC-Tutorial: Experiment 6',
                                                requireReferenceOutput = True,
                                                disabled = (8 in disabled),
                                                disabledReason = "Disabled by command-line switch",
                                                workingDir = "PyConfig/experiment6"))

testSuite.addTest(pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                                configFile = 'config.py',
                                                runSimulations = True,
                                                shortDescription = 'WiFiMAC-Tutorial: Experiment 7',
                                                requireReferenceOutput = True,
                                                disabled = (9 in disabled),
                                                disabledReason = "Disabled by command-line switch",
                                                workingDir = "PyConfig/experiment7"))
if __name__ == '__main__':
    # This is only evaluated if the script is called by hand

    # if you need to change the verbosity do it here
    verbosity = 2

    pywns.WNSUnit.verbosity = verbosity

    # Create test runner
    testRunner = pywns.WNSUnit.TextTestRunner(verbosity=verbosity)

    if (len(disabled) > 0):
        print "Disabled tests ", disabled

    # Finally, run the tests.
    testRunner.run(testSuite)
