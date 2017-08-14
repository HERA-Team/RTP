#! /usr/bin/env python
"""
Input a list of files and insert into the db.  The files must exist and be findable on the filesystem
NB filenames must be FULL PATH. If the root is not '/' for all files it will exit

KEY NOTE: Assumes all files are contiguous.  I sort the files by jd and then match up neighboring pols as neighbors for the
   ddr algorithm

"""
#  Setup the lib path ./lib/  as a spot to check for python libraries
import optparse
import os
import sys
import re
import numpy as n
import socket
import traceback

basedir = os.path.dirname(os.path.realpath(__file__))[:-3]
sys.path.append(basedir + 'lib')

from dbi import DataBaseInterface
#from dbi import add_observations
from dbi import jdpol2obsnum
from dbi import Still
from still import get_dbi_from_config
from still import SpawnerClass
from still import WorkFlow
from still import process_client_config_file


def file2jd(zenuv):
    return re.findall(r'\d+\.\d+', zenuv)[0]


def file2pol(zenuv):
    return re.findall(r'\.(.{2})\.', zenuv)[0]

o = optparse.OptionParser()
o.set_usage('add_observations.py *.uv')
o.set_description(__doc__)
o.add_option('--length', type=float, help='length of the input observations in minutes [default=average difference between filenames]')
o.add_option('-t', action='store_true', help='Test. Only print, do not touch db')
o.add_option('--overwrite', action='store_true',
             help='Default action is to skip obsrvations already in the db. Setting this option overrides this safety feature and attempts anyway')
opts, args = o.parse_args(sys.argv[1:])

# connect to the database

# Jon : set this up correctly, read conf file
config_file = basedir + 'etc/still.cfg'

sg = SpawnerClass()
wf = WorkFlow()

sg.config_file = config_file
process_client_config_file(sg, wf)

dbi = get_dbi_from_config(config_file)
dbi.test_db()  # Testing the database to make sure we made a connection, its fun..

# dbi = DataBaseInterface()

# check that all files exist
for filename in args:
    print filename
    assert(filename.startswith('/'))
    assert(os.path.exists(filename))

# now run through all the files and build the relevant information for the db
# get the pols
pols = []
jds = []
for filename in args:
    pols.append(file2pol(filename))
    jds.append(float(file2jd(filename)))

jds = n.array(jds)
nights = list(set(jds.astype(n.int)))
if opts.length is not None:
    djd = opts.length / 60. / 24
else:
    jds_onepol = n.sort([jd for i, jd in enumerate(jds) if pols[i] == pols[0] and jd.astype(int) == nights[0]])
    djd = n.mean(n.diff(jds_onepol))
    print("setting length to %s days") % djd

pols = list(set(pols))  # these are the pols I have to iterate over
print("found the following pols:")
for pol in pols:
    print("   %s") % pol

print("found the following nights:")
for night in nights:
    print("   %s") % night

for night in nights:
    print("adding night %s") % night
    obsinfo = []
    nightfiles = [filename for filename in args if int(float(file2jd(filename))) == night]
    print len(nightfiles)
    for pol in pols:
        # filter off all pols but the one I'm currently working on
        files = [filename for filename in nightfiles if file2pol(filename) == pol]
        files.sort()
        for i, filename in enumerate(files):
            obsnum = str(jdpol2obsnum(float(file2jd(filename)), file2pol(filename), djd))
            try:
                dbi.get_obs(obsnum)
                if opts.overwrite:
                    raise(StandardError)
                print filename, "found in db, skipping"
            except:
                obsinfo.append({
                    'obsnum': obsnum,
                    'date': float(file2jd(filename)),
                    'date_type': "julian",
                    'pol': file2pol(filename),
                    'host': socket.gethostname(),
                    'filename': filename,
                    'outputhost': '',
                    'status': '',
                    'length': djd  # note the db likes jd for all time units
                })
    for i, obs in enumerate(obsinfo):
        filename = obs['filename']
        if i != 0:
            if n.abs(obsinfo[i - 1]['date'] - obs['date']) < (djd * 1.2):
                obsinfo[i].update({'neighbor_low': obsinfo[i - 1]['date']})
        if i != (len(obsinfo) - 1):
            if n.abs(obsinfo[i + 1]['date'] - obs['date']) < (djd * 1.2):
                obsinfo[i].update({'neighbor_high': obsinfo[i + 1]['date']})
    # assert(len(obsinfo)==len(args))
    if opts.t:
        print "NOT ADDING OBSERVATIONS TO DB"
        print "HERE is what would have been added"
        for obs in obsinfo:
            print("Filename : %s, obsnum: %s") % (obs['filename'], obs['obsnum'])
            print("neighbors - Low: %s  High: %s") % (obs.get('neighbor_low', None),
                                                      obs.get('neighbor_high', None))
    elif len(obsinfo) > 0:
        print("adding %s observations to the still db") % len(obsinfo)
        try:
            dbi.add_observations(obsinfo, "NEW")
        except:
            traceback.print_exc(file=sys.stdout)

            print("problem, could not add observations to the database!")

print "done"
