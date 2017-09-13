#! /usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
# Copyright 2017 the HERA Collaboration
# Licensed under the 2-clause BSD license.

# This script will take pickle files containing RTP process events or
# process records that were not successfully added to M&C at the time of
# creation and backfill them into the databse. See RTP/lib/mc_utils.py for
# more details and how these files are created.

from __future__ import print_function
import os
import pickle
from astropy.time import Time
from hera_mc import mc

parser = mc.get_mc_argument_parser()
parser.add_argument('files', metavar='files', type=str, nargs='+',
                    help='pickle files to read and enter into db.')
parser.add_argument('--type', dest='filetype', type=str, default=None,
                    help='File type to add to db. Must be {pe, pr} for '
                    'RTP process event or process record.')
args = parser.parse_args()
mc_db = mc.connect_to_mc_db(args)
mcs = mc_db.sessionmaker()

files = args.files
filetype = args.filetype

for fn in files:
    with open(fn, 'r') as f:
        pkl = pickle.load(f)

    tval = pkl['time']
    t = Time(val=tval, format='gps')
    obsid = pkl['obsid']

    if filetype == 'pe':
        event = pkl['event']
        args = (t, obsid, event)

        func = mcs.add_rtp_process_event
    elif filetype == 'pr':
        pipeline_list = pkl['pipeline_list']
        rtp_version = pkl['rtp_git_version']
        rtp_hash = pkl['rtp_git_hash']
        hera_qm_version = pkl['hera_qm_git_version']
        hera_qm_hash = pkl['hera_qm_git_hash']
        hera_cal_version = pkl['hera_cal_git_version']
        hera_cal_hash = pkl['hera_cal_git_hash']
        pyuvdata_version = pkl['pyuvdata_git_version']
        pyuvdata_hash = pkl['pyuvdata_git_hash']
        args = (t, obsid, pipeline_list, rtp_version, rtp_hash, hera_qm_version,
                hera_qm_hash, hera_cal_version, hera_cal_hash, pyuvdata_version,
                pyuvdata_hash)

        func = mcs.add_rtp_process_record
    elif filetype is None:
        raise ValueError("Please specify a filetype with --type. Must be 'pe' or 'pr'.")
    else:
        raise ValueError("Unrecognized filetype {}. Must be 'pe' or 'pr'.".format(filetype))

    # add it to the database
    print("Adding {} to the databse...".format(fn))
    func(*args)

    # remove file
    os.remove(fn)
