#!/usr/bin/env python

#
# This script is used to create checkpointed images of MARSSx86 Simulator.
# To use this script uses 'util.cfg' configuration file to read a simulation
# run configuration. Take a look at 'util.cfg.example' to get the idea on how
# to setup a run configuration.
#
# Author  : Avadh Patel
# Contact : apatel at cs.binghamton.edu
#

import tempfile
import os
import subprocess
import sys
import copy
import itertools
import types

from optparse import OptionParser
from threading import Thread, Lock
from sets import Set

import config

# Helper functions

def get_run_config(conf, name):
    # First check if given configuration exists or not

    conf_name = "run %s" % name
    if not conf.has_section(conf_name):
        print("Unable to find configuration %s from config file." % conf_name)
        exit(-1)

    return conf_name

def get_list_from_conf(value):
    # User can specify configuration values either in comma seperated, or new
    # line seperated or mix of both.
    ret = []
    for i in value.split('\n'):
        for j in i.split(','):
            if len(j) > 0:
                ret.append(j.strip())
    return ret

vnc_inc = 0

def get_run_configs(run_name, options, conf_parser):
    global vnc_inc

    run_cfgs = []

    # First find the run section from config file
    run_sec = get_run_config(conf_parser, run_name)

    # Check if this run-section points to other run-sections
    # or not
    if conf_parser.has_option(run_sec, "runs"):
        sub_runs = get_list_from_conf(conf_parser.get(run_sec, "runs"))
        for sub_run in sub_runs:
            run_cfgs.extend(get_run_configs(sub_run, options, conf_parser))
        return run_cfgs

    # Collect all the parameters and construct a 'dict' object with all
    # the information required for running a specific checkpoint

    # Get qemu binary -- added by gaoke
    qemu_bin = conf_parser.get(run_sec, 'qemu_bin', True)

    # Get disk images
    qemu_img = conf_parser.get(run_sec, 'images')
    qemu_img = get_list_from_conf(qemu_img)

    for img in qemu_img:
        if not os.path.exists(img):
            print("Qemu disk image (%s) doesn't exists." % img)
            exit(-1)

    # Get VM memory
    vm_memory = conf_parser.get(run_sec, 'memory')

    if not vm_memory:
        print("Please specify 'memory' in your config.")
        exit(-1)

    if conf_parser.has_option(run_sec, 'vnc_counter'):
        vnc_counter = conf_parser.getint(run_sec, 'vnc_counter')
    else:
        vnc_counter = None

    # Checkpoin List
    if not conf_parser.has_option(run_sec, 'suite'):
        print("Plese specify benchmark suite using 'suite' option.")
        exit(-1)

    suite = "suite %s" % conf_parser.get(run_sec, 'suite')

    if not conf_parser.has_section(suite):
        print("Unable to find section '%s' in your configuration." % suite)
        exit(-1)

    if not conf_parser.has_option(suite, 'checkpoints'):
        print("Please specify checkpoints in section '%s'." % suite)
        exit(-1)

    check_list = conf_parser.get(suite, 'checkpoints')
    check_list = get_list_from_conf(check_list)

    # Filter checkpoint list from user specified ones
    if options.chk_names != "":
        check_sel = options.chk_names.split(',')
        chk_st = Set(check_list)
        chk_sel_st = Set(check_sel)
        chk_st = chk_st & chk_sel_st
        check_list = list(chk_st)

    print("Checkpoints: %s" % str(check_list))

    # Get optional qemu arguments
    qemu_cmd = ''
    qemu_args = ''

    if conf_parser.has_option(run_sec, 'qemu_args'):
        qemu_args = conf_parser.get(run_sec, 'qemu_args')

#    if 'snapshot' not in qemu_args:
#        qemu_args = '%s -snapshot' % qemu_args

    # Get the output directory path
    if not conf_parser.has_option(run_sec, 'out_dir'):
        print("Please specify out_dir in section '%s'." % run_sec)
        exit(-1)

    out_dir = conf_parser.get(run_sec, 'out_dir', True)

    # If not provide config path, use cmdline path 
    if out_dir =='':
        output_dir = options.output_dir + "/"
    else:
        output_dir = out_dir
    options.output_dir = output_dir

    output_dirs = [output_dir]

    if options.iterate > 1:
        output_dirs = []
        for i in range(options.iterate):
            i_dir = output_dir + "run_%d/" % (i + 1)
            output_dirs.append(i_dir)
            if not os.path.exists(i_dir):
                os.makedirs(i_dir)

    # For each checkpoint create a run_config dict and add to list
    img_idx = 0
    for o_dir, check_pt in itertools.product(output_dirs, check_list):
     #   print "o_dir:" + o_dir
        if vnc_counter != None:
            vnc_t = vnc_counter + vnc_inc
            vnc_inc += 1
        else:
            vnc_t = None
        run_cfg = { 'checkpoint' : check_pt,
                'qemu_args' : qemu_args,
                'qemu_img' : qemu_img[img_idx % len(qemu_img)],
                'qemu_bin' : qemu_bin,
                'vm_memory' : vm_memory,
                'vnc_counter' : vnc_t,
                'out_dir' : o_dir,
                }
        run_cfgs.append(run_cfg)
        img_idx += 1

    return run_cfgs

# First check if user has provided directory to save all results files
opt_parser = OptionParser("Usage: %prog [options] run_config")
opt_parser.add_option("-d", "--output-dir", dest="output_dir",
        type="string", help="Name of the output directory to save all results")
opt_parser.add_option("-c", "--config",
        help="Configuration File. By default use util.cfg in util directory")
opt_parser.add_option("-e", "--email", action="store_true",
        help="Send email using 'send_gmail.py' script after completion")
opt_parser.add_option("-i", "--iterate", action="store", default=1, type=int,
        help="Run simulation N times")
opt_parser.add_option("-n", "--num-insts", dest="num_insts", default=1,
        type=int, help="Run N instance of simulations in parallel")
opt_parser.add_option("--chk-names", dest="chk_names", type="string",
        help="Comma separated names of checkpoints to run, this overrides " +
        "default sets of checkpoints specified in config file.", default="")
opt_parser.add_option("-m","--machine", dest="machine_tag", type="string",
        help="Used to generate output dir", default="xeon-4-1")
opt_parser.add_option("-a","--address-map", dest="scheme", type="string",
        help="Which addressmapping scheme used, and genernate output dir", default="Nehalem")

(options, args) = opt_parser.parse_args()

# Check if there is any configration argument provided or not
if len(args) == 0 or args[0] == None:
    print("Please provide configuration name.")
    opt_parser.print_help()
    exit(-1)

# Read configuration file
conf_parser = config.read_config(options.config)

# If user give argument 'out' then print the output of simulation run
# to stdout else ignore it
out_to_stdout = False

checkpoint_lock = Lock()
run_idx = 0

# Config parameters for each checkpoint
run_configs = []
for arg in args:
    run_configs.extend(get_run_configs(arg, options, conf_parser))

num_threads = min(int(options.num_insts), len(run_configs))

#print("Run configurations: %s" % str(run_configs))
print("Total run configurations: %s" % (len(run_configs)))
print("%d parallel simulation instances will be run." % num_threads)

login_cmds = ["root\n", "root\n"]

def pty_to_stdout(fd, untill_chr):
    chr = '1'
    while chr != untill_chr:
        chr = os.read(fd, 1)
        sys.stdout.write(chr)
    sys.stdout.flush()

def pty_login(fd):
    os.write(fd, login_cmds[0])
    pty_to_stdout(fd, ':')
    os.write(fd, login_cmds[1])

# also used to substitue other *simconfig* 's variables according *args*
def gen_value(args, simconfig):
    gen_cfg = simconfig
    recursive_count = 0
    while '%' in gen_cfg or recursive_count > 10:
        gen_cfg = gen_cfg % args
        recursive_count += 1
    return gen_cfg

# Thread class that will store the output on the serial port of qemu to file
class SerialOut(Thread):

    def __init__(self, out_filename, out_devname):
        # global output_dir
        super(SerialOut, self).__init__()
        self.out_filename = out_filename
        self.out_devname = out_devname

    def run(self):
        # Open the serial port and a file
        out_file = open(self.out_filename, 'w')
        out_dev_file = os.open(self.out_devname, os.O_RDONLY)

        try:
            while True:
                line = os.read(out_dev_file, 1)
                out_file.write(line)
                if len(line) == 0:
                    break
        except OSError:
            pass

        print("Writing to output file completed")
        out_file.close()
        os.close(out_dev_file)

# Thread class that will store the output on the serial port of qemu to file
class StdOut(Thread):

    def __init__(self, out_obj_):
        super(StdOut, self).__init__()
        self.out_obj = out_obj_

    def run(self):
        # Open the serial port and a file
        global out_to_stdout
        try:
            while True:
                line = self.out_obj.read(1)
                if len(line) == 0:
                    break
                if out_to_stdout:
                    sys.stdout.write(line)
        except OSError:
            pass

        print("Writing to stdout completed")


class RunSim(Thread):

    def __init__(self):
        super(RunSim, self).__init__()

    def add_to_cmd(self, opt):
        self.qemu_cmd = "%s %s" % (self.qemu_cmd, opt)

    def run(self):
        global checkpoint_lock
        global run_configs
        global run_idx
        global run_list
        # Start simulation from checkpoints
        pty_prefix = 'char device redirected to '
        while True:
            run_cfg = None
            self.qemu_cmd = ''

            try:
                checkpoint_lock.acquire()
                run_cfg = run_configs[run_idx]
                run_idx += 1
            except:
                run_cfg = None
            finally:
                checkpoint_lock.release()

            if not run_cfg:
                break

            print("Checkpoint %s" % str(run_cfg['checkpoint']))

            output_dir = run_cfg['out_dir']
            checkpoint = run_cfg['checkpoint']

            config_args = copy.copy(conf_parser.defaults())
            config_args['out_dir'] = os.path.realpath(run_cfg['out_dir'])
            config_args['bench'] = checkpoint
            config_args['machine_tag'] = options.machine_tag
            config_args['scheme'] = options.scheme

            t_outdir = gen_value(config_args, run_cfg['out_dir'])

            run_cfg['qemu_bin'] = gen_value(config_args, run_cfg['qemu_bin'])
            if not os.path.exists(run_cfg['qemu_bin']):
                print("Qemu binary file (%s) doesn't exists." % run_cfg['qemu_bin'])
                exit(-1)

            #  change here to create output_dir
            if not os.path.exists(t_outdir):
                os.makedirs(t_outdir)

            # Generate a common command string
            self.add_to_cmd(run_cfg['qemu_bin'])
            self.add_to_cmd('-m %s' % str(run_cfg['vm_memory']))
            self.add_to_cmd('-serial pty')
            if run_cfg['vnc_counter']:
                self.add_to_cmd('-vnc :%d' % run_cfg['vnc_counter'])
            else:
                self.add_to_cmd('-nographic')

            # Add Image at the end
            self.add_to_cmd('-hda %s' % run_cfg['qemu_img'])
            #self.add_to_cmd('-drive cache=unsafe,file=%s' % run_cfg['qemu_img'])
            self.add_to_cmd(run_cfg['qemu_args'])

            print("Starting Checkpoint: %s" % checkpoint)
            print("Files will be saved in: %s" % t_outdir)
            print("Command: %s" % self.qemu_cmd)

            p = subprocess.Popen(self.qemu_cmd.split(), stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, stdin=subprocess.PIPE, bufsize=0)

            serial_pty = None
            pty_term = None
            while p.poll() is None:
                line = p.stdout.readline()
                sys.stdout.write(line)
                if line.startswith(pty_prefix):
                    dev_name = line[len(pty_prefix):].strip()

                    # Open the device terminal and send simulation command
                    pty_term = os.open(dev_name, os.O_RDWR)
                    serial_pty = dev_name 

                    break

            if pty_term == None:
                print("ERROR:While connecting with pty terminal")

            pty_to_stdout(pty_term,':')

            # Now send the login commands to the terminal and wait
            # untill some response text
            pty_login(pty_term)

            pty_to_stdout(pty_term,'#')

            # At this point we assume that we have successfully logged in
            # Now give the command to run each checkpoint
            tmp_idx = 0
            while tmp_idx < len(run_list):
                if run_list[tmp_idx]['name'] == checkpoint:
                    os.write(pty_term, run_list[tmp_idx]['command'])
                    break
                else:
                    tmp_idx = tmp_idx + 1
            os.close(pty_term)

            serial_thread = SerialOut('%s/%s_%s.out' % (t_outdir, options.machine_tag, checkpoint), serial_pty)

            # os.dup2(serial_pty, sys.stdout.fileno())

            stdout_thread = StdOut(p.stdout)
            stdout_thread.start()
            serial_thread.start()

            # Wait for simulation to complete
            p.wait()

            serial_thread.join()
            stdout_thread.join()

# Spec2006 Parse
spec_dir = "/root/spec2006bin/gcc/"

def gen_commands(bench, coreid):
	for bench_ in spec_bench_specifiers:
		if (bench_[0] == bench):
			cmd = '''cd %s%s
taskset -c %d ./%s %s &\n''' % (spec_dir, bench_[1], coreid, bench_[2], bench_[3])
			return cmd

spec_chk_list = [

		['1perl1c', 'perl'],
		['1bzip1c', 'bzip'],
		['1gcc1c', 'gcc'],
		['1bwaves1c', 'bwaves'],
		['1gamess1c', 'gamess'],
		['1mcf1c', 'mcf'],
		['1zeusmp1c', 'zeusmp'],
		['1gromacs1c', 'gromacs'],
		['1cactusADM1c', 'cactusADM'],
		['1leslie3d1c', 'leslie3d'],
		['1namd1c', 'namd'],
		['1gobmk1c', 'gobmk'],
		['1deal1c', 'deal'],
		['1soplex1c', 'soplex'],
		['1povray1c', 'povray'],
		['1calculix1c', 'calculix'],
		['1hmmer1c', 'hmmer'],
		['1sjeng1c', 'sjeng'],
		['1gems1c', 'GemsFDTD'],
		['1quantum1c', 'quantum'],
		['1h2641c', 'h264'],
		['1tonto1c', 'tonto'],
		['1lbm1c', 'lbm'],
		['1omnetpp1c', 'omnetpp'],
		['1astar1c', 'astar'],
		['1wrf1c', 'wrf'],
		['1sphinx1c', 'sphinx'],
		['1xalanc1c', 'xalanc'],

		['1perl4c', 'perl'],
		['1bzip4c', 'bzip'],
		['1gcc4c', 'gcc'],
		['1mcf4c', 'mcf'],
		['1cactusADM4c', 'cactusADM'],
		['1leslie3d4c', 'leslie3d'],
		['1namd4c', 'namd'],
		['1deal4c', 'deal'],
		['1soplex4c', 'soplex'],
		['1povray4c', 'povray'],
		['1calculix4c', 'calculix'],
		['1hmmer4c', 'hmmer'],
		['1sjeng4c', 'sjeng'],
		['1quantum4c', 'quantum'],
		['1lbm4c', 'lbm'],
		['1omnetpp4c', 'omnetpp'],
		]

spec_bench_specifiers = [

        ['perl', '400.perl', 'perlbench_base.gcc', '-I./lib checkspam.pl 2500 5 25 11 150 1 1 1 1'],
        ['bzip', '401.bzip2','bzip2_base.gcc','input.program 280'],
        ['gcc', '403.gcc', 'gcc_base.gcc', 's04.i -o s04.s'],
        ['bwaves', '410.bwaves', 'bwaves_base.gcc', ''],
        ['gamess', '416.gamess', 'gamess_base.gcc', '< h2ocu2+.gradient.config'],
        ['mcf', '429.mcf', 'mcf_base.gcc', 'inp.in'],
        ['milc', '433.milc', 'milc_base.gcc', '< su3imp.in'],
        ['zeusmp', '434.zeusmp', 'zeusmp_base.gcc', ''],
        ['gromacs', '435.gromacs', 'gromacs_base.gcc', '--silent -deffnm gromacs -nice 0'],
        ['cactusADM', '436.cactusADM', 'cactusADM_base.gcc', 'benchADM.par'],
        ['leslie3d', '437.leslie3d', 'leslie3d_base.gcc', '< leslie3d.in'],
        ['namd', '444.namd', 'namd_base.gcc', '--input namd.input --iterations 38 --output namd.out'],
        ['gobmk', '445.gobmk', 'gobmk_base.gcc', '--quite --mode gtp < nngs.tst'],
        ['deal', '447.dealII', 'dealII_base.gcc', '23'],
        ['soplex', '450.soplex', 'soplex_base.gcc', '-m3500 ref.mps'],
        ['povray', '453.povray', 'povray_base.gcc', 'SPEC-benchmark-ref.ini'],
        ['calculix', '454.calculix', 'calculix_base.gcc', '-i hyperviscoplastic'],
        ['hmmer', '456.hmmer', 'hmmer_base.gcc', 'nph3.hmm swiss41'],
        ['sjeng', '458.sjeng', 'sjeng_base.gcc', 'ref.txt'],
        ['GemsFDTD', '459.GemsFDTD', 'GemsFDTD_base.gcc', ''],
        ['quantum', '462.libquantum', 'libquantum_base.gcc', '1397 8'],
        ['h264', '464.h264ref', 'h264ref_base.gcc', '-d sss_encoder_main.cfg'],
        ['tonto', '465.tonto', 'tonto_base.gcc', ''],
        ['lbm', '470.lbm', 'lbm_base.gcc', '3000 reference.dat 0 0 100_100_130_ldc.of'],
        ['omnetpp', '471.omnetpp', 'omnetpp_base.gcc', 'omnetpp.ini'],
        ['astar', '473.astar', 'astar_base.gcc', 'BigLakes2048.cfg'],
        ['wrf', '481.wrf', 'wrf_base.gcc', ''],
        ['sphinx', '482.sphinx3', 'sphinx_base.gcc', 'ctlfile . args.an4'],
        ['xalanc', '483.xalancbmk', 'xalancbmk_base.gcc', '-v t5.xml xalanc.xsl'],
		]

spec_list = []
for chk in spec_chk_list:
	cmd_list='~/checkpoint_after 10000M %s\n' % chk[0]
	for i in range(len(chk)):
		if i == 0:
			name = chk[i]
		if i != 0:
			cmd_list += gen_commands(chk[i],i-1)
	chk_ = {'name': chk[0],
			'command':cmd_list
			}
	spec_list.append(chk_)

# Parse with parsecmgmt
parsec_chk_list = [
# 4 cores
		['1blackscholes4c', 1 ,'blackscholes'],
		['1bodytrack4c', 1 ,'bodytrack'],
		['1canneal4c', 1 ,'canneal'],
		['1ferret4c', 1 ,'ferret'],
		['1fluidanimate4c', 1 ,'fluidanimate'],
		['1freqmine4c', 1 ,'freqmine'],
		['1streamcluster4c', 1 ,'streamcluster'],
		['1vips4c', 1 ,'vips'],
		['1x2644c', 1 ,'x264'],

		['4blackscholes4c', 4 ,'blackscholes'],
		['4bodytrack4c', 4 ,'bodytrack'],
		['4canneal4c', 4 ,'canneal'],
		['4ferret4c', 4 ,'ferret'],
		['4fluidanimate4c', 4 ,'fluidanimate'],
		['4freqmine4c', 4 ,'freqmine'],
		['4streamcluster4c', 4 ,'streamcluster'],
		['4vips4c', 4 ,'vips'],
		['4x2644c', 4 ,'x264'],

# 8 cores
		['1blackscholes8c', 1 ,'blackscholes'],
		['1bodytrack8c', 1 ,'bodytrack'],
		['1canneal8c', 1 ,'canneal'],
		['1ferret8c', 1 ,'ferret'],
		['1fluidanimate8c', 1 ,'fluidanimate'],
		['1freqmine8c', 1 ,'freqmine'],
		['1streamcluster8c', 1 ,'streamcluster'],
		['1vips8c', 1 ,'vips'],
		['1x2648c', 1 ,'x264'],

		['4blackscholes8c', 4 ,'blackscholes'],
		['4bodytrack8c', 4 ,'bodytrack'],
		['4canneal8c', 4 ,'canneal'],
		['4ferret8c', 4 ,'ferret'],
		['4fluidanimate8c', 4 ,'fluidanimate'],
		['4freqmine8c', 4 ,'freqmine'],
		['4streamcluster8c', 4 ,'streamcluster'],
		['4vips8c', 4 ,'vips'],
		['4x2648c', 4 ,'x264'],

		['8blackscholes8c', 8 ,'blackscholes'],
		['8bodytrack8c', 8 ,'bodytrack'],
		['8canneal8c', 8 ,'canneal'],
		['8ferret8c', 8 ,'ferret'],
		['8fluidanimate8c', 8 ,'fluidanimate'],
		['8freqmine8c', 8 ,'freqmine'],
		['8streamcluster8c', 8 ,'streamcluster'],
		['8vips8c', 8 ,'vips'],
		['8x2648c', 8 ,'x264'],
# 16 cores
		['1blackscholes16c', 1 ,'blackscholes'],
		['1bodytrack16c', 1 ,'bodytrack'],
		['1canneal16c', 1 ,'canneal'],
		['1ferret16c', 1 ,'ferret'],
		['1fluidanimate16c', 1 ,'fluidanimate'],
		['1freqmine16c', 1 ,'freqmine'],
		['1streamcluster16c', 1 ,'streamcluster'],
		['1vips16c', 1 ,'vips'],
		['1x26416c', 1 ,'x264'],

		['4blackscholes16c', 4 ,'blackscholes'],
		['4bodytrack16c', 4 ,'bodytrack'],
		['4canneal16c', 4 ,'canneal'],
		['4ferret16c', 4 ,'ferret'],
		['4fluidanimate16c', 4 ,'fluidanimate'],
		['4freqmine16c', 4 ,'freqmine'],
		['4streamcluster16c', 4 ,'streamcluster'],
		['4vips16c', 4 ,'vips'],
		['4x26416c', 4 ,'x264'],

		['8blackscholes16c', 8 ,'blackscholes'],
		['8bodytrack16c', 8 ,'bodytrack'],
		['16canneal16c', 8 ,'canneal'],
		['8ferret16c', 8 ,'ferret'],
		['8fluidanimate16c', 8 ,'fluidanimate'],
		['8freqmine16c', 8 ,'freqmine'],
		['8streamcluster16c', 8 ,'streamcluster'],
		['8vips16c', 8 ,'vips'],
		['8x26416c', 8 ,'x264'],

		['16blackscholes16c', 16 ,'blackscholes'],
		['16bodytrack16c', 16 ,'bodytrack'],
		['16canneal16c', 16 ,'canneal'],
		['16ferret16c', 16 ,'ferret'],
		['16fluidanimate16c', 16 ,'fluidanimate'],
		['16freqmine16c', 16 ,'freqmine'],
		['16streamcluster16c', 16 ,'streamcluster'],
		['16vips16c', 16 ,'vips'],
		['16x26416c', 16 ,'x264'],
		]

parsec_bench_list = ['blackscholes', 'bodytrack', 'ferret', 'freqmine',
        'swaptions', 'fluidanimate', 'vips', 'x264', 'canneal', 'dedup',
        'streamcluster', 'facesim', 'raytrace']

pre_setup_str = '''cd parsec-2.1; . env.sh
        export PARSEC_CPU_NUM=`grep processor /proc/cpuinfo | wc -l`; echo $PARSEC_CPU_NUM
        '''
parsec_roi_list = []
for chk in parsec_chk_list:
    vm_smp = chk[1]
    bench = chk[2]
    pre_command = "%s\nexport CHECKPOINT_NAME=\"%s\"\n" % (pre_setup_str, chk[0])
    parsec_cmd = "parsecmgmt -a run -c gcc-hooks -x roi -n %d -i simlarge -p %s" % (vm_smp, bench)
    bench_dict = {'name' : chk[0], 'command' : '%s\n%s\n' % (pre_command, parsec_cmd) }
    parsec_roi_list.append(bench_dict)

# Now start RunSim threads with running commands
#run_list = spec_list 
run_list = parsec_roi_list 

# Now start RunSim threads
threads = []

for i in range(num_threads):
    th = RunSim()
    threads.append(th)
    th.start()

print("All Threads are started")

for th in threads:
    th.join()

# Send email to notify run completion
if options.email:
    email_script = "%s/send_gmail.py" % os.path.dirname(os.path.realpath(__file__))
    subprocess.call([email_script, "-m", "Completed simulation runs in %s" %
        str(options.output_dir)])

print("Completed all simulation runs.")
