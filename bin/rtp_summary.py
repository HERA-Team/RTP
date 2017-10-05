#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-

"""
Summarize a given night's RTP status, and generate a report.
"""

from __future__ import print_function, division
from astropy.time import Time
import datetime
import optparse

# hacky way to import RTP libraries for interfacing with DB
import os
import sys
basedir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, os.path.join(basedir, 'lib'))
sys.path.insert(0, os.path.join(basedir, 'bin'))

from dbi import DataBaseInterface, Observation
from still import get_dbi_from_config, SpawnerClass

def main(args):
    # define option parsing function
    o = optparse.OptionParser()
    o.set_usage('rtp_summary.py')
    o.set_description(__doc__)
    o.add_option('--config_file', help='RTP configuration file; default=etc/rtp_hera_h1c.cfg',
                 default='etc/rtp_hera_h1c.cfg', type=str)
    o.add_option('--date', help='JD for which to generate the status report;'
                 ' defaults to the current JD, minus 1 (i.e., the previous night\'s observation',
                 default=0, type=int)
    opts, args = o.parse_args(args)

    # create a database interface
    spawner = SpawnerClass()
    spawner.config_file = os.path.join(basedir, opts.config_file)
    dbi = get_dbi_from_config(spawner.config_file)
    dbi.test_db()

    # summarize the status of the specified JD's observation
    if opts.date == 0:
        # get today's JD, subtract one to get yesterday, and make a new time
        # object for computing the (Gregorian) calendar date
        t = Time.now()
        jd_of_interest = int(t.jd) - 1
        t = Time(val=jd_of_interest, format='jd')
    else:
        t = Time(val=opts.date, format='jd')
        jd_of_interest = opts.date
    # convert JD to unix epoch to create datetime object, for writing human dates
    date = datetime.datetime.fromtimestamp(t.unix)
    datestr = date.strftime('%a %b %d, %Y')

    # query database
    s = dbi.Session()
    obsnums = s.query(Observation).filter(
        Observation.obsnum.like('zen.{:d}%'.format(jd_of_interest))).all()
    nobs = len(obsnums)

    if nobs == 0:
        print("No observations for JD {0:d} ({1})\n".format(jd_of_interest, datestr))
        return
    else:
        # categorize observations
        ncomplete = 0
        nworking = 0
        nfailed = 0
        for obs in obsnums:
            if obs.status == "COMPLETE":
                ncomplete += 1
            elif obs.current_stage_in_progress == "FAILED":
                nfailed += 1
            else:
                nworking += 1
        s.close()

        # make sure we didn't have any observations fall through the cracks
        if ncomplete + nfailed + nworking != nobs:
            print("Had {:d} total observations, {:d} complete, {:d} working, {:d} failed;"
                  " totals don\'t match!".format(nobs, ncomplete, nworking, nfailed))
            return

        # write out report
        pct_comp = ncomplete / nobs * 100
        pct_work = nworking / nobs * 100
        pct_fail = nfailed / nobs * 100
        print("RTP report for JD {0:d} ({1})\n".format(jd_of_interest, datestr))
        print("Number of observations: {:d}".format(nobs))
        print("Number finished processing: {0:d} ({1:d}%)".format(ncomplete, int(pct_comp)))
        print("Number currently processing: {0:d} ({1:d}%)".format(nworking, int(pct_work)))
        print("Number failed: {0:d} ({1:d}%)".format(nfailed, int(pct_fail)))
        return

if __name__ == '__main__':
    main(sys.argv[1:])
