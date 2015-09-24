### Test utils - Blivet
### Part of: Blivet test collection
### Author: kvalek@redhat.com
### This program is under GPL licence.

install_name = "f23"
install_disk = "{}.iso".format(install_name)
mach_name = install_name
full_disk_path_1 = "/home/Libvirt_disks/{}1.img".format(mach_name)
full_disk_path_2 = "/home/Libvirt_disks/{}2.img".format(mach_name)
full_disk_path_3 = "/home/Libvirt_disks/{}3.img".format(mach_name)
full_loc_path = "/home/Libvirt_disks/{}".format(install_disk)

ks_file_path = 'http://10.34.39.2/ks/kv/autoInstaller.ks'
key_location = "/home/kvalek/.ssh/atlas"
ram_size = 2048

import subprocess
import glob
import time
import re


scp_source = "/home/kvalek/GitHub/blivet-tests/"

# check if machine exists
vys = subprocess.getoutput("virsh list --all | grep {}".format(mach_name))

if vys == "":
    # undefine domain if needed
    subprocess.call(["virsh destroy {}".format(mach_name)], shell=True)
    subprocess.call(["virsh undefine {}".format(mach_name)], shell=True)

    # begin creation and installation
    subprocess.call(["virt-install", "--name", "{}".format(mach_name),\
    "--disk", "{},size=8".format(full_disk_path_1),\
    "--disk", "{},size=2".format(full_disk_path_2),\
    "--disk", "{},size=2".format(full_disk_path_3),\
    "--location", "{}".format(full_loc_path),\
    "--graphics", "vnc,listen=0.0.0.0", "--noautoconsole",\
    "--ram", "{}".format(ram_size), "-x", "ks={}".format(ks_file_path), "--noreboot"])

while (subprocess.call(["virsh list | grep {}".format(mach_name)], shell=True) != 1):
    time.sleep(10)

subprocess.call(["virsh snapshot-create-as {} snap-start --atomic".format(mach_name)], shell=True)
subprocess.call(["virsh", "start", install_name])
while (subprocess.call(["virt-log -d {} | grep bound".format(mach_name)], shell=True) != 0):
    time.sleep(10)

ip_address = subprocess.getoutput("virt-log -d {} | grep bound | tail -n 1".format(mach_name))
vystup = re.search(r'.*to\ ([0-9]*.[0-9]*.[0-9*]*.[0-9]*).*', ip_address)
if vystup:
    print(vystup.group(1))
print(ip_address)
file_list = glob.glob("{}*".format(scp_source))

# scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no
# copy files to machine
for inc in file_list:
    subprocess.call(["scp", "-o", "UserKnownHostsFile=/dev/null", "-o", "StrictHostKeyChecking=no", "-i", "{}".format(key_location), inc, "{}:~".format(vystup.group(1))])

# run test
subprocess.call(["ssh", "-i", "{}".format(key_location), "-o", "StrictHostKeyChecking=no", "root@{}".format(vystup.group(1)), "'python3'","'test_arrays.py'"])
subprocess.call(["scp", "-i", "{}".format(key_location), "root@{}:/root/TEST_RESULT".format(vystup.group(1)), "./"])
vys = subprocess.call(["virsh snapshot-revert  {} snap-start".format(mach_name)], shell=True)
if vys != 0:
    print("*** ERROR: Snapshot failed to revert")
subprocess.call(["cat", "./TEST_RESULT"])
subprocess.call(["virsh shutdown {}".format(mach_name)], shell=True)
