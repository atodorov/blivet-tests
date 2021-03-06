### Test - stage 1
### Part of: Blivet test collection
### Author: kvalek@redhat.com
### This program is under GPL licence.
import sys
sys.path.append("..")
sys.path.append("./Test_Deps")

import classes
import test_utils

test_system = classes.SystemDisk_Scan('vdb')
test_blivet = classes.BlivetInitialization('vdb').disk
ia = test_utils.test(test_system, test_blivet)
test_utils.write_issues(ia, "Basic disk", 1)
