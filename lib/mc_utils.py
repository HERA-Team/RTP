from __future__ import print_function, division, absolute_import
import math
import cPickle as pickle
import astropy.time as atime
import hera_mc.mc_session as mc_session

import version as rtp.version
import hera_qm.version
import hera_cal.version
import pyuvdata.version


def add_mc_server_status(hostname, ip_addr, ncpu, cpu_usage, vmem_pct,
                         vmem_tot, du_pct, du_tot):
    """
    Add an RTP server status to the HERA M&C database.

    This function adds a server status for a computation node (i.e., "still") to
    the M&C database. This contains basic telemetry information, like current CPU
    load and memory usage.

    Args:
    hostname: string
       Hostname of the computation node
    ip_addr: string
       IP address of the computation node
    ncpu: integer
       Number of CPUs on the computation node
    cpu_usage: float
       Current CPU load of the computation node (specifically,
       the 5 minute load average)
    vmem_pct: float
       Percentage of memory in use of the computation node
    vmem_tot: float
       Total size (in GiB) of memory on the computation node
    du_pct: float
       Percentage of disk in use of the computation node
    du_tot: float
       Total size (in GiB) of memory on the computation node

    Return:
    None
    """
    # get the current time
    t = atime.Time.now()

    # add to hera_mc
    mcs = mc_session.MCSession()
    mcs.add_server_status('rtp', hostname, ip_addr, t, ncpu, cpu_usage, vmem_pct,
                          vmem_tot, du_pct, du_tot)
    return


def add_mc_rtp_status(status, dt_check_min, ntasks, dt_boot_hr):
    """
    Add a server status to the RTP subsystem table in HERA M&C database.

    Args:
    status: string
       Status of the server ("OK", "DURESS", "OFFLINE", etc.)
    dt_check_min: float
       Time since last check-in, in minutes
    ntasks: integer
       Number of tasks assigned to system
    dt_boot_hr: float
       Time since last reboot, in hours

    Return:
    None
    """
    # get the current time
    t = atime.Time.now()

    # add to hera_mc
    mc_session.add_rtp_status(t, status, dt_check_min, ntasks, dt_check_hr)
    return


def add_process_event(obsid, status):
    """
    Add the status of an RTP process (i.e., obsid workflow) to HERA M&C database.

    This function adds the status of the specified obsid's workflow to the
    database. This is helpful for seeing when a particular task was started,
    and whether it finished successfully or errored while processing.

    Since we want to be able to backfill this information if M&C is not reachable,
    in the event we can't connect to the db, we will dump to disk (as a pickle)
    to be read in later.

    Args:
    obsid: string
       Obsid of the process
    status: string
       Status to add to db. Should be one of: queued, started, finished, error

    Return:
    None
    """
    # get time
    t = atime.Time.now()

    try:
        mc_session.add_rtp_process_event(t, obsid, status)
    except:
        # save to disk
        gps_sec = math.floor(t.gps)
        info_dict = {"time": t, "obsid": obsid, "event": status}
        filename = "pe_{0}_{1}.pkl".format(self.obs, str(int(gps_sec)))
        with open(filename, 'w') as f:
            pickle.dump(info_dict, f)

    return


def add_process_record(obsid, workflow_actions, workflow_actions_endfile=None):
    """
    Add the final record of steps for an RTP process to the HERA M&C database.

    This function adds the list of steps taken for a particular obsid to the
    database. This is useful for being able to accurately reconstruct the
    history of analysis steps taken for each part of the pipeline.

    In addition to information about the workflow, we include the git information
    of the key software components used to perform the analysis. This assures that
    a perfect reconstruction of the steps taken can be recreated.

    As with the process events, if the M&C database is unreachable, the data is
    saved to disk to be backfilled later.

    Args:
    obsid: string
       Obsid of the process
    workflow_actions: list of strings
       List of tasks in the workflow
    workflow_actions_endfile: list of strings, optional
       List of tasks after the main portion of the workflow is completed

    Return:
    None
    """
    # get time
    t = atime.Time.now()

    # make CSV list of pipeline steps
    if (workflow_actions_endfile is not None
        and workflow_actions_endfile != ''):
        workflow = workflow_actions + workflow_actions_endfile
        pipeline = ','.join(workflow)
    else:
        pipeline = ','.join(workflow_actions)

    # get git info for different packages
    rtp_info = rtp.version.construct_version_info()
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

    try:
        mc_session.add_rtp_process_record(t, obsid, pipeline, rtp_version, rtp_hash,
                                          hera_qm_version, hera_qm_hash,
                                          hera_cal_version, hera_cal_hash,
                                          pyuvdata_version, pyuvdata_hash)
    except:
        # save to disk to read later
        gps_sec = math.floor(t.gps)
        info_dict = {"time": t, "obsid": self.obs, "pipeline_list": pipeline, "rtp_git_version": rtp_version,
                     "rtp_git_hash": rtp_hash, "hera_qm_git_version": hera_qm_version, "hera_qm_git_hash": hera_qm_hash,
                     "hera_cal_git_version": hera_cal_version, "hera_cal_git_hash": hera_cal_hash,
                     "pyuvdata_git_version": pyuvdata_version, "pyuvdata_git_hash": pyuvdata_hash}
        filename = "pr_{0}_{1}.pkl".format(self.obs, str(int(gps_sec)))
        with open(filename, 'w') as f:
            pickle.dump(info_dict, f)

    return
