#!/bin/bash

util/run_bench.py --chk-names=1perl4c,1bzip4c,1gcc4c,1gobmk4c,1hmmer4c,1sjeng4c,1quantum4c,1h2644c,1omnetpp4c,1astar4c,1xalanc4c,1milc4c,1bwaves4c,1gamess4c,1zeusmp4c,1gromacs4c,1cactusADM4c,1leslie3d4c,1namd4c,1deal4c,1soplex4c,1povray4c,1calculix4c,1gems4c,1tonto4c,1lbm4c,1wrf4c,1sphinx4c,1mcf4c -m xeon-4-1 -s "-run -stopinsns 200m" -n 4 spec2006 
