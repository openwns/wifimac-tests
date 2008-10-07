#! /usr/bin/env python2.4

# this is needed, so that the script can be called from everywhere
import os
import sys
base, tail = os.path.split(sys.argv[0])
os.chdir(base)

# Append the python sub-dir of WNS--main--x.y ...
sys.path.append(os.path.join('..', '..', '..', 'sandbox', 'default', 'lib', 'python2.4', 'site-packages'))

# ... because the module WNS unit test framework is located there.
import pywns.WNSUnit

testSuite = pywns.WNSUnit.TestSuite()

# create a system test
testSuite.addTest(pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                                executeable = "wns-core",
                                                configFile = 'config.py',
                                                runSimulations = True,
                                                shortDescription = '1AP, 1 STA, overload DL w RTS/CTS',
                                                requireReferenceOutput = True,
                                                disabled = False,
                                                disabledReason = ""))

testSuite.addTest(pywns.WNSUnit.ProbesTestSuite(sandboxPath = os.path.join('..', '..', '..', 'sandbox'),
                                                executeable = "wns-core",
                                                configFile = 'configSmallMesh.py',
                                                runSimulations = True,
                                                shortDescription = '2APs/1MPs network with 3 STAs',
                                                requireReferenceOutput = True,
                                                disabled = False,
                                                disabledReason = ""))
if __name__ == '__main__':
    # This is only evaluated if the script is called by hand

    # if you need to change the verbosity do it here
    verbosity = 2

    pywns.WNSUnit.verbosity = verbosity

    # Create test runner
    testRunner = pywns.WNSUnit.TextTestRunner(verbosity=verbosity)

    # Finally, run the tests.
    testRunner.run(testSuite)
