#!/usr/bin/python

import os

run1 = os.popen("util/run_bench.py --chk-names=1namd4c,1soplex4c,1cactusADM4c,1omnetpp4c,1povray4c,1sjeng4c,1gcc4c,1leslie3d4c,1bzip4c,1lbm4c,1calculix4c,1mcf4c,1quantum4c,1hmmer4c -s \"-run\" -a Nehalem spec2006")
run2 = os.popen("util/run_bench.py --chk-names=1namd4c,1soplex4c,1cactusADM4c,1omnetpp4c,1povray4c,1sjeng4c,1gcc4c,1leslie3d4c,1bzip4c,1lbm4c,1calculix4c,1mcf4c,1quantum4c,1hmmer4c -s \"-run\" -a Scheme1 spec2006")
run3 = os.popen("util/run_bench.py --chk-names=1namd4c,1soplex4c,1cactusADM4c,1omnetpp4c,1povray4c,1sjeng4c,1gcc4c,1leslie3d4c,1bzip4c,1lbm4c,1calculix4c,1mcf4c,1quantum4c,1hmmer4c -s \"-run\" -a Scheme2 spec2006")
run4 = os.popen("util/run_bench.py --chk-names=1namd4c,1soplex4c,1cactusADM4c,1omnetpp4c,1povray4c,1sjeng4c,1gcc4c,1leslie3d4c,1bzip4c,1lbm4c,1calculix4c,1mcf4c,1quantum4c,1hmmer4c -s \"-run\" -a Scheme3 spec2006")
run5 = os.popen("util/run_bench.py --chk-names=1namd4c,1soplex4c,1cactusADM4c,1omnetpp4c,1povray4c,1sjeng4c,1gcc4c,1leslie3d4c,1bzip4c,1lbm4c,1calculix4c,1mcf4c,1quantum4c,1hmmer4c -s \"-run\" -a Scheme4 spec2006")
run6 = os.popen("util/run_bench.py --chk-names=1namd4c,1soplex4c,1cactusADM4c,1omnetpp4c,1povray4c,1sjeng4c,1gcc4c,1leslie3d4c,1bzip4c,1lbm4c,1calculix4c,1mcf4c,1quantum4c,1hmmer4c -s \"-run\" -a Scheme5 spec2006")
run7 = os.popen("util/run_bench.py --chk-names=1namd4c,1soplex4c,1cactusADM4c,1omnetpp4c,1povray4c,1sjeng4c,1gcc4c,1leslie3d4c,1bzip4c,1lbm4c,1calculix4c,1mcf4c,1quantum4c,1hmmer4c -s \"-run\" -a Scheme6 spec2006")
run8 = os.popen("util/run_bench.py --chk-names=1namd4c,1soplex4c,1cactusADM4c,1omnetpp4c,1povray4c,1sjeng4c,1gcc4c,1leslie3d4c,1bzip4c,1lbm4c,1calculix4c,1mcf4c,1quantum4c,1hmmer4c -s \"-run\" -a Scheme7 spec2006")
