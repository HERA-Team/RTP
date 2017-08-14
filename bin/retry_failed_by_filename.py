#! /usr/bin/env python
"""
For the observations matching a given file name, reset them to the initial
state *if* they are marked as having failed.

"""
from __future__ import print_function
import argparse
import os
import sys
import re
import logging


basedir = os.path.dirname(os.path.realpath(__file__))[:-3]
sys.path.append(basedir + 'lib')

from dbi import File, Observation
from still import process_client_config_file, WorkFlow, SpawnerClass, StillDataBaseInterface


def file2jd(zenuv):
    return re.findall(r'\d+\.\d+', zenuv)[0]


def file2pol(zenuv):
    return re.findall(r'\.(.{2})\.', zenuv)[0]


parser = argparse.ArgumentParser(
    description='Retry failed observations by filename.')

parser.add_argument('--reset', dest='reset', action='store_true',
                    help='Reset observation to start from beginning, not just retry currente step.')

parser.add_argument('-v', dest='debug', action='store_true',
                    help='set log level to debug')

parser.add_argument('--config_file', dest='config_file', required=False,
                    help="Specify the complete path to the config file")

parser.add_argument('names', nargs='+', type=str, metavar='FILENAME',
                    help="Names of the files to potentially retry.")

parser.set_defaults(config_file="%setc/still.cfg" % basedir)

args = parser.parse_args()

sg = SpawnerClass()
wf = WorkFlow()

sg.config_file = args.config_file
process_client_config_file(sg, wf)
reset_status = wf.workflow_actions[0]

# connect to the database
dbi = StillDataBaseInterface(
    sg.dbhost, sg.dbport, sg.dbtype, sg.dbname, sg.dbuser, sg.dbpasswd, test=False)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('retry_failed_by_filename.py')

if args.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


# Fairly straightforward ...

if args.reset:
    desc = 'reset'
else:
    desc = 'retry'

s = dbi.Session()

for name in args.names:
    try:
        # In current usage, the "obsnum" is the file basename.
        obsnum = os.path.basename(name)

        obs = s.query(Observation).filter(
            Observation.obsnum == obsnum).one_or_none()
        if obs is None:
            print("failed on filename \"%s\": nothing with that obsnum" % name)
            continue

        if obs.current_stage_in_progress not in ('FAILED', 'KILLED'):
            print("skipping \"%s\": current_stage is \"%s\", not FAILED or KILLED" % (name,
                                                                                      obs.current_stage_in_progress))
            continue

        print("issuing a %s for \"%s\"" % (desc, name))
        if args.reset:
            dbi.set_obs_status(obsnum, reset_status)
            dbi.set_obs_still_host(obsnum, None)
        dbi.update_obs_current_stage(obsnum, None)
        dbi.set_obs_pid(obsnum, None)
        dbi.add_log(obsnum, desc.upper(),
                    "doing a %s at user request" % desc, 0)
    except Exception as e:
        print("failed on filename \"%s\": %s" % (name, e), file=sys.stderr)

s.close()
