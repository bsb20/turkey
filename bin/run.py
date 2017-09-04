#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import subprocess
import pathos.multiprocessing as mp
from random import randint

from turkey import Job, Task, Policy, apps, pthread, tbb

# TODO: https://argcomplete.readthedocs.io/en/latest/

parser = argparse.ArgumentParser(description='Turkey job runner')
parser.add_argument('-q', '--turkey-home', help='Turkey home directory')
subparsers = parser.add_subparsers(help='sub-command help', dest='cmd')

###############################################################################
# Server commands
###############################################################################

server = subparsers.add_parser('server', help='Handle server stuff')

###############################################################################
# Client (the dummy one) commands
###############################################################################

client = subparsers.add_parser('client', help='Do dummy client stuff')

###############################################################################
# Build subcommand
###############################################################################

build = subparsers.add_parser('build', help='Build specified app')
build.add_argument('app', help='App to build', default='all')
build.add_argument('-f', '--force', help='Force rebuild', action='store_true')
build.add_argument(
    '-e', '--cmake-executable', help='Path to cmake', default='cmake')
build.add_argument('-j', '--parallel', help='Parallelize', action='store_true')

###############################################################################
# Data subcommand
###############################################################################

data = subparsers.add_parser('data', help='Download and unpack data')
data.add_argument('app', help='App to data for', default='all')

###############################################################################
# Generate subcommand
###############################################################################

gen = subparsers.add_parser('gen', help='Generate job files for run command')
gen.add_argument(
    '-a',
    '--apps',
    help='List of applications to generate from',
    default='pthread')
gen.add_argument('-p', '--prefix', help='Job name prefix', default='job')
gen.add_argument(
    '-j',
    '--num-jobs',
    help='Number of jobs to generate',
    type=int,
    default=100)
gen.add_argument(
    '-t',
    '--num-tasks',
    help='Number of tasks per job to generate',
    type=int,
    default=100)
gen.add_argument(
    '-n',
    '--num-threads',
    help='Number of threads to launch each task with',
    type=int,
    default=1)
gen.add_argument('-c', '--conf', help='Configuration to run', default='test')
gen.add_argument(
    '-s',
    '--start-time-strategy',
    help='How to assign job start times',
    default=0)

###############################################################################
# Job subcommand
###############################################################################

job = subparsers.add_parser('job', help='Run job')
job.add_argument('file', help='Job file')
job.add_argument('-w', '--working-dir', help='Working directory')
job.add_argument(
    '-o', '--out-dir', help='Output directory relative to working')
job.add_argument(
    '-i',
    '--in-dir',
    help='Input directory relative to working. Where app directory lives')
job.add_argument(
    '-t', '--time', help='Time individual jobs', action='store_false')
job.add_argument(
    '-a',
    '--add-all',
    help='Dump all simultaneously into queue and let pool sort out',
    action='store_true')
job.add_argument(
    '-n',
    '--num_workers',
    help='Maximum number of simultaneous jobs',
    type=int,
    default=1)
job.add_argument(
    '-u', '--turkey-mode', help='Run in turkey mode', action='store_true')

###############################################################################
# One-off run subcommand
###############################################################################

one = subparsers.add_parser('one', help='Run one app')
one.add_argument('app', help='App to run')
one.add_argument(
    '-n', '--num-threads', help='Number of threads', type=int, default=1)
one.add_argument('-c', '--conf', help='Configuration to run', default='test')
one.add_argument('-w', '--working-dir', help='Working directory')
one.add_argument(
    '-o', '--out-dir', help='Output directory relative to working')
one.add_argument(
    '-i',
    '--in-dir',
    help='Input directory relative to working. WHere app directory lives')
one.add_argument(
    '-e', '--executable', help='Executable if different from app name')
one.add_argument(
    '-s',
    '--output_to_stdout',
    help='Dump to stdout instead of file',
    action='store_true')
one.add_argument(
    '-m', '--mode', help='Which thread library to use', default='pthread')

###############################################################################
# policy commands
###############################################################################

policy = subparsers.add_parser('policy', help='Run according to policy file')
policy.add_argument('file', help='Policy JSON file')
policy.add_argument('-o', '--out_dir',
                    help='Output directory relative to working', default='out')

###############################################################################
# qsub cluster commands
###############################################################################

qsub = subparsers.add_parser('qsub', help='Run qsub jobs')
qsub.add_argument(
    '-a',
    '--apps',
    help='List of applications to generate from',
    default='pthread')
qsub.add_argument('-p', '--prefix', help='Job name prefix', default='job')
qsub.add_argument(
    '-n',
    '--num_workers',
    help='Maximum number of simultaneous jobs',
    type=int,
    default=5)
qsub.add_argument(
    '-c',
    '--num_cores',
    help='Maximum number of simultaneous jobs',
    type=int,
    default=mp.cpu_count())
qsub.add_argument('-r', '--run-script', help='Run script')
qsub.add_argument(
    '-j', '--array-bounds', help='Range of jobs to run', default='0-99')
qsub.add_argument(
    '-l',
    '--loop',
    help='Array job (without flag) or individual qsub',
    action='store_true')
qsub.add_argument(
    '-u', '--turkey-mode', help='Run in turkey mode', action='store_true')

###############################################################################
# Clean subcommand
###############################################################################

clean = subparsers.add_parser('clean', help='Clean up directory')

args = parser.parse_args()

if args.turkey_home is None:
    try:
        TURKEY_HOME = os.environ['TURKEY_HOME']
        args.turkey_home = TURKEY_HOME
    except KeyError, e:
        print 'ERROR: could not find TURKEY_HOME in environment. Please specify with -q.'
        sys.exit()
else:
    TURKEY_HOME = args.turkey_home

if args.cmd == 'server':
    subprocess.Popen([os.path.join(TURKEY_HOME, 'build/turkey_server')])
    os.wait()
elif args.cmd == 'client':

    subprocess.Popen([os.path.join(TURKEY_HOME, 'build/turkey_client')])
    os.wait()
elif args.cmd == 'qsub':

    turkey = ''
    if args.turkey_mode:
        turkey = '-u'

    if not args.loop:
        args.run_script = args.run_script or os.path.join(TURKEY_HOME,
                                                          'cluster/array.sh')
        os.system(
            'qsub -lselect=1:ncpus=%d -lplace=excl -J %s -v apps=%s,prefix=%s,workers=%d,mode=%s %s'
            % (args.num_cores, args.array_bounds, args.apps, args.prefix,
               args.num_workers, turkey, args.run_script, ))
    else:
        bounds = [int(bound) for bound in args.array_bounds.split('-')]
        for i in range(bounds[1] - bounds[0] + 1):
            args.run_script = args.run_script \
                or os.path.join(TURKEY_HOME, 'cluster/run.sh')
            os.system(
                'qsub -lselect=1:ncpus=%d -lplace=excl -v apps=%s,prefix=%s,workers=%d,index=%d,mode=%s %s'
                % (args.num_cores, args.apps, args.prefix, args.num_workers, i,
                   turkey, args.run_script, ))
elif args.cmd == 'build':

    if args.force:
        os.system('rm -rf %s' % os.path.join(TURKEY_HOME, 'build'))
    cwd = os.getcwd()
    os.chdir(TURKEY_HOME)
    os.system('mkdir -p build')
    os.chdir(os.path.join(TURKEY_HOME, 'build'))
    os.system('%s .. -DMAKE=%s && make %s' % (args.cmake_executable, args.app,
                                              ('-j' if args.parallel else '')))
    os.chdir(cwd)
elif args.cmd == 'data':

    data_executable = os.path.join(TURKEY_HOME, 'bin/data')
    if args.app in apps:
        os.system('%s %s' % (data_executable, args.app))
    else:
        for app in apps:
            os.system('%s %s' % (data_executable, app))
elif args.cmd == 'gen':

    subset = pthread
    if args.apps == 'tbb':
        subset = tbb

    working_dir = os.path.join(TURKEY_HOME, 'jobs')
    for i in range(args.num_jobs):
        os.system('mkdir -p %s' % os.path.join(working_dir, args.apps))
        with open(
                os.path.join(working_dir, args.apps, '%s-%08d.job' %
                             (args.prefix, i)),
                'w') as job_file:
            for j in range(args.num_tasks):
                task_index = randint(0, len(subset) - 1)
                job_file.write(','.join([
                    str(0), subset[task_index], args.conf, args.apps,
                    str(args.num_threads)
                ]) + '\n')
elif args.cmd == 'job':

    if args.time:
        os.system('date')

    if args.working_dir == None:
        args.working_dir = os.path.join(TURKEY_HOME, 'jobs')

    if args.in_dir == None:
        args.in_dir = TURKEY_HOME

    job = Job(args)
    if args.add_all:
        pool_size = min(job.ntasks, args.num_workers)
        pool = mp.Pool(pool_size)
        if args.turkey_mode:
            pool.map(lambda task: task.run(threads=int(mp.cpu_count()
                                                       / pool_size), wait=True), job.task_array)
        else:
            pool.map(lambda task: task.run(wait=True), job.task_array)
    else:
        job.run()
elif args.cmd == 'one':

    if args.executable == None:
        args.executable = args.app

    if args.working_dir == None:
        args.working_dir = os.path.join(TURKEY_HOME, 'out')

    if args.out_dir == None:
        args.out_dir = '.'

    if args.in_dir == None:
        args.in_dir = TURKEY_HOME

    out_dir = os.path.join(args.working_dir, args.out_dir)
    task = Task(
        [
            0,
            0,
            args.app,
            args.conf,
            args.mode,
            args.num_threads,
        ],
        out_dir,
        args.in_dir,
        executable=args.executable,
        output_to_stdout=args.output_to_stdout,
        TURKEY_HOME=TURKEY_HOME, )
    task.run()

    os.wait()
elif args.cmd == 'policy':
    pol = Policy(args.file, args.out_dir, TURKEY_HOME)
    pol.run()

elif args.cmd == 'clean':
    os.system('rm -rf build')
else:
    print parser.print_help()
