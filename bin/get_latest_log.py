#! /usr/bin/env python
"""
Print out the latest log item associated with the specified obsnum.

"""
from __future__ import absolute_import, division, print_function

import argparse
import os.path
import sys

# Path futzing

basedir = os.path.dirname(os.path.realpath(__file__))[:-3]
sys.path.append(basedir + 'lib')

from dbi import Observation
from still import process_client_config_file, WorkFlow, SpawnerClass, StillDataBaseInterface


# Arguments

parser = argparse.ArgumentParser(
    description='Get the latest log item associated with an observation.')
parser.add_argument('--config_file', dest='config_file', required=False, default=basedir + 'etc/still.cfg',
                    help="Path to the RTP config file")
parser.add_argument('obsnum', type=str, metavar='OBSNUM',
                    help='The "obsnum" to query.')
args = parser.parse_args()


# Set up stuff

sg = SpawnerClass()
wf = WorkFlow()

sg.config_file = args.config_file
process_client_config_file(sg, wf)
dbi = StillDataBaseInterface(
    sg.dbhost, sg.dbport, sg.dbtype, sg.dbname, sg.dbuser, sg.dbpasswd, test=False)


# Let's do it.

info = dbi.get_obs_latest_log(args.obsnum)

if info is None:
    print ('No log items associated with obsnum %r.' % (args.obsnum,))
else:
    print ('Stage:', info['stage'])
    print ('Exit status:', info['exit_status'])
    print ('Start time:', info['start_time'])
    print ('End time:', info['end_time'])
    print ('Text:')
    print (info['logtext'])
