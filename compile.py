#!/usr/bin/python

import os

#cores = ['1','4','8','16','24','32','48','64']
#cores = ['2','4','8','16']
#cores = ['1','4','16','32']
cores = ['1']

for i in range(0,len(cores)):
    compile_cmd = 'scons c='+ cores[i] + ' dramsim=/home/gaoke/dramsim4marss/DRAMSim2 config=config/xeon.conf'
    os.system(compile_cmd)
    rename_cmd = 'mv qemu/qemu-system-x86_64 qemu/qemu-system-x86_64-' + 'xeon-' + cores[i] + '-1'
    os.system(rename_cmd)
