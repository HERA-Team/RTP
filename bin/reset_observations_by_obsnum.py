#! /usr/bin/env python
"""
Reset observations identified by their "obsnums", which are not necessarily
actually numbers.

"""
import argparse, os.path, sys

# Path futzing

basedir = os.path.dirname(os.path.realpath(__file__))[:-3]
sys.path.append(basedir + 'lib')

from dbi import Observation
from still import process_client_config_file, WorkFlow, SpawnerClass, StillDataBaseInterface


# Arguments

parser = argparse.ArgumentParser(description='Reset RTP observations with the given obsnums.')

parser.add_argument('--status', dest='status', required=False, default='',
                    help='set the observation to this status; default will be the first workflow action')

parser.add_argument('--config_file', dest='config_file', required=False, default=basedir + 'etc/still.cfg',
                    help="Path to the RTP config file")

parser.add_argument('obsnums', nargs='+', type=str, metavar='OBSNUM',
                    help='List of "obsnums" to reset.')

args = parser.parse_args()

# Set up stuff

sg = SpawnerClass()
wf = WorkFlow()

sg.config_file = args.config_file
process_client_config_file(sg, wf)
if args.status == '':
    args.status = wf.workflow_actions[0]

dbi = StillDataBaseInterface(sg.dbhost, sg.dbport, sg.dbtype, sg.dbname, sg.dbuser, sg.dbpasswd, test=False)

# Let's do it.

try:
    s = dbi.Session()
    obsnums = [o.obsnum for o in s.query(Observation).filter(Observation.obsnum.in_ (args.obsnums))]
    s.close()

    for obsnum in obsnums:
        dbi.set_obs_status(obsnum, args.status)
        dbi.set_obs_pid(obsnum, None)
        dbi.set_obs_still_host(obsnum, None)
        dbi.add_log(obsnum, args.status, "resetting (reset_observations_by_obsnum)", 0)
        dbi.update_obs_current_stage(obsnum, None)
except Exception as e:
    print("error: %s") % e
