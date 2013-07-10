#!/usr/bin/python

import os

cores = ['4']

for i in range(0,len(cores)):
    compile_cmd = 'scons c='+ cores[i] + ' dramsim=/home/gaoke/DRAMSim2 config=config/xeon.conf'
    os.system(compile_cmd)
    rename_cmd = 'mv qemu/qemu-system-x86_64 qemu/qemu-system-x86_64-' + 'xeon-' + cores[i] + '-1'
    os.system(rename_cmd)
