#!/usr/bin/python

import os
"""
neha = os.popen("util/run_bench.py --chk-names=1blackscholes4c,1bodytrack4c,1canneal4c,1ferret4c,1fluidanimate4c,1freqmine4c,1streamcluster4c,1vips4c,1x2644c -a Nehalem -s \"-run\" parsec-2.1")
sch1 = os.popen("util/run_bench.py --chk-names=1blackscholes4c,1bodytrack4c,1canneal4c,1ferret4c,1fluidanimate4c,1freqmine4c,1streamcluster4c,1vips4c,1x2644c -a Scheme1 -s \"-run\" parsec-2.1")
sch2 = os.popen("util/run_bench.py --chk-names=1blackscholes4c,1bodytrack4c,1canneal4c,1ferret4c,1fluidanimate4c,1freqmine4c,1streamcluster4c,1vips4c,1x2644c -a Scheme2 -s \"-run\" parsec-2.1")
sch3 = os.popen("util/run_bench.py --chk-names=1blackscholes4c,1bodytrack4c,1canneal4c,1ferret4c,1fluidanimate4c,1freqmine4c,1streamcluster4c,1vips4c,1x2644c -a Scheme3 -s \"-run\" parsec-2.1")
sch4 = os.popen("util/run_bench.py --chk-names=1blackscholes4c,1bodytrack4c,1canneal4c,1ferret4c,1fluidanimate4c,1freqmine4c,1streamcluster4c,1vips4c,1x2644c -a Scheme4 -s \"-run\" parsec-2.1")
sch5 = os.popen("util/run_bench.py --chk-names=1blackscholes4c,1bodytrack4c,1canneal4c,1ferret4c,1fluidanimate4c,1freqmine4c,1streamcluster4c,1vips4c,1x2644c -a Scheme5 -s \"-run\" parsec-2.1")
sch6 = os.popen("util/run_bench.py --chk-names=1blackscholes4c,1bodytrack4c,1canneal4c,1ferret4c,1fluidanimate4c,1freqmine4c,1streamcluster4c,1vips4c,1x2644c -a Scheme6 -s \"-run\" parsec-2.1")
sch7 = os.popen("util/run_bench.py --chk-names=1blackscholes4c,1bodytrack4c,1canneal4c,1ferret4c,1fluidanimate4c,1freqmine4c,1streamcluster4c,1vips4c,1x2644c -a Scheme7 -s \"-run\" parsec-2.1")
"""
"""
neha = os.popen("util/run_bench.py --chk-names=4blackscholes4c,4bodytrack4c,4canneal4c,4ferret4c,4fluidanimate4c,4freqmine4c,4streamcluster4c,4vips4c,4x2644c -a Nehalem -s \"-run\" parsec-2.1")
sch1 = os.popen("util/run_bench.py --chk-names=4blackscholes4c,4bodytrack4c,4canneal4c,4ferret4c,4fluidanimate4c,4freqmine4c,4streamcluster4c,4vips4c,4x2644c -a Scheme1 -s \"-run\" parsec-2.1")
sch2 = os.popen("util/run_bench.py --chk-names=4blackscholes4c,4bodytrack4c,4canneal4c,4ferret4c,4fluidanimate4c,4freqmine4c,4streamcluster4c,4vips4c,4x2644c -a Scheme2 -s \"-run\" parsec-2.1")
sch3 = os.popen("util/run_bench.py --chk-names=4blackscholes4c,4bodytrack4c,4canneal4c,4ferret4c,4fluidanimate4c,4freqmine4c,4streamcluster4c,4vips4c,4x2644c -a Scheme3 -s \"-run\" parsec-2.1")
sch4 = os.popen("util/run_bench.py --chk-names=4blackscholes4c,4bodytrack4c,4canneal4c,4ferret4c,4fluidanimate4c,4freqmine4c,4streamcluster4c,4vips4c,4x2644c -a Scheme4 -s \"-run\" parsec-2.1")
sch5 = os.popen("util/run_bench.py --chk-names=4blackscholes4c,4bodytrack4c,4canneal4c,4ferret4c,4fluidanimate4c,4freqmine4c,4streamcluster4c,4vips4c,4x2644c -a Scheme5 -s \"-run\" parsec-2.1")
sch6 = os.popen("util/run_bench.py --chk-names=4blackscholes4c,4bodytrack4c,4canneal4c,4ferret4c,4fluidanimate4c,4freqmine4c,4streamcluster4c,4vips4c,4x2644c -a Scheme6 -s \"-run\" parsec-2.1")
sch7 = os.popen("util/run_bench.py --chk-names=4blackscholes4c,4bodytrack4c,4canneal4c,4ferret4c,4fluidanimate4c,4freqmine4c,4streamcluster4c,4vips4c,4x2644c -a Scheme7 -s \"-run\" parsec-2.1")
"""
neha = os.popen("util/run_bench.py --chk-names=16blackscholes16c,16bodytrack16c,16canneal16c -m xeon-16-1 -a Nehalem -s \"-run\" parsec-2.1")
sch1 = os.popen("util/run_bench.py --chk-names=16blackscholes16c,16bodytrack16c,16canneal16c -m xeon-16-1 -a Scheme1 -s \"-run\" parsec-2.1")
sch2 = os.popen("util/run_bench.py --chk-names=16blackscholes16c,16bodytrack16c,16canneal16c -m xeon-16-1 -a Scheme2 -s \"-run\" parsec-2.1")
sch3 = os.popen("util/run_bench.py --chk-names=16blackscholes16c,16bodytrack16c,16canneal16c -m xeon-16-1 -a Scheme3 -s \"-run\" parsec-2.1")
sch4 = os.popen("util/run_bench.py --chk-names=16blackscholes16c,16bodytrack16c,16canneal16c -m xeon-16-1 -a Scheme4 -s \"-run\" parsec-2.1")
sch5 = os.popen("util/run_bench.py --chk-names=16blackscholes16c,16bodytrack16c,16canneal16c -m xeon-16-1 -a Scheme5 -s \"-run\" parsec-2.1")
sch6 = os.popen("util/run_bench.py --chk-names=16blackscholes16c,16bodytrack16c,16canneal16c -m xeon-16-1 -a Scheme6 -s \"-run\" parsec-2.1")
sch7 = os.popen("util/run_bench.py --chk-names=16blackscholes16c,16bodytrack16c,16canneal16c -m xeon-16-1 -a Scheme7 -s \"-run\" parsec-2.1")
