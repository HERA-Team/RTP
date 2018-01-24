import nose.tools as nt
import cPickle as pickle

# PCL: kludge to import mc_utils module -- will go away in repo reorg
import sys
import os
import time
import math
import numpy as np
basedir = os.path.dirname(os.path.realpath(__file__)).replace("unit_tests", "")
sys.path.append(basedir + 'lib')
sys.path.append(basedir + 'bin')

from astropy.time import Time, TimeDelta
from hera_mc.tests import TestHERAMC
import hera_mc.utils
import hera_mc.geo_location
import mc_utils
import version as rtpversion
import hera_qm.version
import hera_cal.version
import pyuvdata.version

class TestMCUtils(TestHERAMC):
    def setUp(self):
        super(TestMCUtils, self).setUp()
        self.test_db.create_tables()

        # Time and obsid
        time = Time.now()
        obsid = hera_mc.utils.calculate_obsid(time)
        self.time = time
        self.obsid = obsid
        self.observation_values = [time, time + TimeDelta(10 * 60, format='sec'),
                                   obsid]

        # M&C cruft
        stn = 'cofa'
        prefix = 'COFA'
        st = hera_mc.geo_location.StationType()
        st.station_type_name = stn
        st.prefix = prefix
        self.test_session.add(st)
        self.test_session.commit()
        gl = hera_mc.geo_location.GeoLocation()
        gl.station_name = prefix + '_null'
        gl.station_type_name = stn
        gl.datum = 'WGS84'
        gl.tile = '34J'
        gl.northing = 6601181.0
        gl.easting = 541007.0
        gl.elevation = 1051.69
        gl.created_gpstime = 1172530000
        self.test_session.add(gl)
        self.test_session.commit()

        # RTP server status
        hostname = 'localhost'
        ip_addr = '127.0.0.1'
        ncpu = 8
        cpu_usage = 4.5
        uptime = 17.2
        vmem_pct = 68.2
        vmem_tot = 8.
        du_pct = 28.4
        du_tot = 127.5
        self.server_status = [hostname, ip_addr, ncpu, cpu_usage, uptime, vmem_pct,
                              vmem_tot, du_pct, du_tot]

        # RTP Status
        status = 'OK'
        dt_check_min = 4.98
        ntasks = 6
        dt_boot_hr = 48.2
        self.rtp_status = [status, dt_check_min, ntasks, dt_boot_hr]

        # RTP Process Event
        status = 'started'
        self.process_event = [obsid, status]

        # RTP Process Record
        self.workflow_actions = ['UV', 'ANT_METRICS', 'FIRSTCAL', 'OMNICAL', 'XRFI']
        self.workflow_actions_endfile = ['CLEAN_ANT_METRICS', 'CLEAN_XRFI']

        # RTP Task Resource Record
        self.task_name = 'OMNICAL'
        self.task_name2 = 'FIRSTCAL'
        self.start_time = Time.now()
        self.stop_time = self.start_time + TimeDelta(10 * 60, format='sec')
        self.max_memory = 16.2
        self.avg_cpu_load = 1.

    def test_add_mc_server_status(self):
        # add to db
        mc_utils.add_mc_server_status(*self.server_status, mcs=self.test_session)

        # retrieve record and check that it matches
        result = self.test_session.get_server_status('rtp', self.time
                                                     - TimeDelta(2, format='sec'))
        nt.assert_equal(len(result), 1)

        # the time of the entry is not controlled by RTP, but check other entries
        result = result[0]
        nt.assert_equal(result.hostname, self.server_status[0])
        nt.assert_equal(result.ip_address, self.server_status[1])
        nt.assert_equal(result.num_cores, self.server_status[2])
        nt.assert_equal(result.cpu_load_pct, self.server_status[3])
        nt.assert_equal(result.uptime_days, self.server_status[4])
        nt.assert_equal(result.memory_used_pct, self.server_status[5])
        nt.assert_equal(result.memory_size_gb, self.server_status[6])
        nt.assert_equal(result.disk_space_pct, self.server_status[7])
        nt.assert_equal(result.disk_size_gb, self.server_status[8])

    def test_add_mc_rtp_status(self):
        # add to db
        mc_utils.add_mc_rtp_status(*self.rtp_status, mcs=self.test_session)

        # retrieve record and check that it matches
        result = self.test_session.get_rtp_status(self.time - TimeDelta(2, format='sec'))
        nt.assert_equal(len(result), 1)

        # the time of the entry is not controlled by RTP, so don't check that
        result = result[0]
        nt.assert_equal(result.status, self.rtp_status[0])
        nt.assert_equal(result.event_min_elapsed, self.rtp_status[1])
        nt.assert_equal(result.num_processes, self.rtp_status[2])
        nt.assert_equal(result.restart_hours_elapsed, self.rtp_status[3])

    def test_add_mc_process_event(self):
        # add observation to db
        self.test_session.add_obs(*self.observation_values)
        obs_result = self.test_session.get_obs()
        nt.assert_equal(len(obs_result), 1)

        # add process event to db
        mc_utils.add_mc_process_event(*self.process_event, mcs=self.test_session)

        # retrieve record and check that it matches
        result = self.test_session.get_rtp_process_event(self.time - TimeDelta(2, format='sec'))
        nt.assert_equal(len(result), 1)

        # the time of the entry is not controlled by RTP, so don't check taht
        result = result[0]
        nt.assert_equal(result.obsid, self.process_event[0])
        nt.assert_equal(result.event, self.process_event[1])

        # also test dumping a dict to disk
        # feeding in nonsense for an MCSession will trigger the "except" branch
        mc_utils.add_mc_process_event(*self.process_event, mcs='blah',
                                      outdir=os.getcwd())

        # read in pickle from disk
        # there should only be one
        for fn in os.listdir(os.getcwd()):
            if 'pe_' in fn:
                pe_fn = fn
                break

        with open(pe_fn, 'r') as f:
            info_dict = pickle.load(f)

        # check that dictionary entries match data
        nt.assert_equal(info_dict['obsid'], self.process_event[0])
        nt.assert_equal(info_dict['event'], self.process_event[1])

        # clean up after ourselves
        os.remove(pe_fn)

    def test_add_mc_process_record(self):
        # add observation to db
        self.test_session.add_obs(*self.observation_values)
        obs_result = self.test_session.get_obs()
        nt.assert_equal(len(obs_result), 1)

        # add process record to db
        mc_utils.add_mc_process_record(self.obsid, self.workflow_actions, mcs=self.test_session)

        # retrieve record and check that it matches
        result = self.test_session.get_rtp_process_record(self.time - TimeDelta(2, format='sec'))
        nt.assert_equal(len(result), 1)

        # check versioning info from other packages
        rtp_info = rtpversion.construct_version_info()
        hera_qm_info = hera_qm.version.construct_version_info()
        hera_cal_info = hera_cal.version.construct_version_info()
        pyuvdata_info = pyuvdata.version.construct_version_info()

        rtp_version = rtp_info['version']
        rtp_hash = rtp_info['git_hash']
        hera_qm_version = hera_qm_info['version']
        hera_qm_hash = hera_qm_info['git_hash']
        hera_cal_version = hera_cal_info['version']
        hera_cal_hash = hera_cal_info['git_hash']
        pyuvdata_version = pyuvdata_info['version']
        pyuvdata_hash = pyuvdata_info['git_hash']

        # the time of the entry is not controlled by RTP, so don't check that
        result = result[0]
        pipeline = ','.join(self.workflow_actions)
        nt.assert_equal(result.obsid, self.obsid)
        nt.assert_equal(result.pipeline_list, pipeline)
        nt.assert_equal(result.rtp_git_version, rtp_version)
        nt.assert_equal(result.rtp_git_hash, rtp_hash)
        nt.assert_equal(result.hera_qm_git_version, hera_qm_version)
        nt.assert_equal(result.hera_qm_git_hash, hera_qm_hash)
        nt.assert_equal(result.hera_cal_git_version, hera_cal_version)
        nt.assert_equal(result.hera_cal_git_hash, hera_cal_hash)
        nt.assert_equal(result.pyuvdata_git_version, pyuvdata_version)
        nt.assert_equal(result.pyuvdata_git_hash, pyuvdata_hash)

        # test adding workflow_actions and workflow_actions_endfile
        # sleep to prevent a conflict with existing entry
        time.sleep(2)
        mc_utils.add_mc_process_record(self.obsid, self.workflow_actions,
                                       self.workflow_actions_endfile, mcs=self.test_session)

        # retrieve the record and check that it matches
        result = self.test_session.get_rtp_process_record(self.time - TimeDelta(2, format='sec'),
                                                          stoptime=self.time + TimeDelta(1e3, format='sec'))
        nt.assert_equal(len(result), 2)

        # check that everything is correct
        result = result[1]
        pipeline = ','.join(self.workflow_actions + self.workflow_actions_endfile)
        nt.assert_equal(result.obsid, self.obsid)
        nt.assert_equal(result.pipeline_list, pipeline)
        nt.assert_equal(result.rtp_git_version, rtp_version)
        nt.assert_equal(result.rtp_git_hash, rtp_hash)
        nt.assert_equal(result.hera_qm_git_version, hera_qm_version)
        nt.assert_equal(result.hera_qm_git_hash, hera_qm_hash)
        nt.assert_equal(result.hera_cal_git_version, hera_cal_version)
        nt.assert_equal(result.hera_cal_git_hash, hera_cal_hash)
        nt.assert_equal(result.pyuvdata_git_version, pyuvdata_version)
        nt.assert_equal(result.pyuvdata_git_hash, pyuvdata_hash)

        # test dumping to a pickle and reading it back in
        # feeding in nonsense for an MCSession will trigger the "except" branch
        mc_utils.add_mc_process_record(self.obsid, self.workflow_actions,
                                       self.workflow_actions_endfile, mcs='blah',
                                       outdir=os.getcwd())

        # read in pickle from disk
        # there should only be one
        for fn in os.listdir(os.getcwd()):
            if 'pr_' in fn:
                pr_fn = fn
                break

        with open(pr_fn, 'r') as f:
            info_dict = pickle.load(f)

        # check that dictionary entries match data
        nt.assert_equal(info_dict['obsid'], self.obsid)
        nt.assert_equal(info_dict['pipeline_list'], pipeline)
        nt.assert_equal(info_dict['rtp_git_version'], rtp_version)
        nt.assert_equal(info_dict['rtp_git_hash'], rtp_hash)
        nt.assert_equal(info_dict['hera_qm_git_version'], hera_qm_version)
        nt.assert_equal(info_dict['hera_qm_git_hash'], hera_qm_hash)
        nt.assert_equal(info_dict['hera_cal_git_version'], hera_cal_version)
        nt.assert_equal(info_dict['hera_cal_git_hash'], hera_cal_hash)
        nt.assert_equal(info_dict['pyuvdata_git_version'], pyuvdata_version)
        nt.assert_equal(info_dict['pyuvdata_git_hash'], pyuvdata_hash)

        # clean up after ourselves
        os.remove(pr_fn)


    def test_add_mc_task_resource_record(self):
        # add observation to db
        self.test_session.add_obs(*self.observation_values)
        obs_result = self.test_session.get_obs()
        nt.assert_equal(len(obs_result), 1)

        # add process record to db
        mc_utils.add_mc_task_resource_record(self.obsid, self.task_name, self.start_time, self.stop_time,
                                             self.max_memory, self.avg_cpu_load, mcs=self.test_session)

        # retrieve record and check that it matches
        result = self.test_session.get_rtp_task_resource_record(self.time - TimeDelta(2, format='sec'))
        nt.assert_equal(len(result), 1)

        # the time of the entry is not controlled by RTP, so don't check that
        result = result[0]
        nt.assert_equal(result.obsid, self.obsid)
        nt.assert_equal(result.task_name, self.task_name)
        nt.assert_equal(result.start_time, math.floor(self.start_time.gps))
        nt.assert_equal(result.stop_time, math.floor(self.stop_time.gps))
        nt.assert_true(np.isclose(result.max_memory, self.max_memory))
        nt.assert_true(np.isclose(result.avg_cpu_load, self.avg_cpu_load))

        # test adding with no memory or cpu load
        # change task name to avoid conflict
        mc_utils.add_mc_task_resource_record(self.obsid, self.task_name2, self.start_time, self.stop_time,
                                             mcs=self.test_session)

        # retrieve the record and check that it matches
        result = self.test_session.get_rtp_task_resource_record(self.start_time - TimeDelta(2, format='sec'),
                                                                stoptime=self.time + TimeDelta(1e3, format='sec'))
        nt.assert_equal(len(result), 2)

        # check that everything is correct
        result = result[1]
        nt.assert_equal(result.obsid, self.obsid)
        nt.assert_equal(result.task_name, self.task_name2)
        nt.assert_equal(result.start_time, math.floor(self.start_time.gps))
        nt.assert_equal(result.stop_time, math.floor(self.stop_time.gps))

        # test dumping to a pickle and reading it back in
        # feeding in nonsense for an MCSession will trigger the "except" branch
        mc_utils.add_mc_task_resource_record(self.obsid, self.task_name, self.start_time, self.stop_time,
                                             mcs='blah', outdir=os.getcwd())

        # read in pickle from disk
        # there should only be one
        for fn in os.listdir(os.getcwd()):
            if 'trr_' in fn:
                trr_fn = fn
                break

        with open(trr_fn, 'r') as f:
            info_dict = pickle.load(f)

        # check that dictionary entries match data
        nt.assert_equal(info_dict['obsid'], self.obsid)
        nt.assert_equal(info_dict['task_name'], self.task_name)
        nt.assert_equal(info_dict['start_time'], math.floor(self.start_time.gps))
        nt.assert_equal(info_dict['stop_time'], math.floor(self.stop_time.gps))

        # clean up after ourselves
        os.remove(trr_fn)
