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
                    print dev_name

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
            print t_outdir

            # os.dup2(serial_pty, sys.stdout.fileno())

            stdout_thread = StdOut(p.stdout)
            stdout_thread.start()
            serial_thread.start()

            # Wait for simulation to complete
            p.wait()

            serial_thread.join()
            stdout_thread.join()

# num threads
vm_smp = 4

# Spec2006 Parse
spec_dir = "/root/spec2006bin/gcc/"

def gen_commands(bench, coreid):
	for bench in spec_bench_specifiers:
		cmd = '''cd %s%s
taskset -c %d ./%s %s &\n''' % (spec_dir, bench[1], coreid, bench[2], bench[3])
		return cmd

chk_list = [
		['2lbm4c', 'lbm','lbm'],
		]

spec_bench_specifiers = [
		['lbm', '470.lbm','lbm_base.gcc','3000 reference.dat 0 0 100_100_130_ldc.of'],
		]

spec_list = []
for chk in chk_list:
	cmd_list='~/set_semaphore %d %s &\n' % (len(chk) - 1, chk[0])
	for i in range(len(chk)):
		if i == 0:
			name = chk[i]
		if i != 0:
			cmd_list += gen_commands(chk[i],i-1)

	chk_ = {'name': chk[0],
			'command':cmd_list
			}
#	print cmd_list
	spec_list.append(chk_)


# Now start RunSim threads with running commands
run_list = spec_list 


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
