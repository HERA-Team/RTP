'''
RTP.site.monitor.views

author | Immanuel Washington

Functions
---------
db_objs | gathers database objects for use
index | shows main page
stream_plot | streaming plot example
obs_hist | creates histogram
obs_table | shows observation table
file_table | shows file table
'''
import os
import sys
base_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(base_dir))
from flask_app import monitor_app as app
import rdbi
import datetime
from flask import render_template, flash, redirect, url_for, request, g, make_response, Response, jsonify
from sqlalchemy import func

def db_objs():
    '''
    outputs database objects

    Returns
    -------
    tuple:
        object: database interface object
        object: observation table object
        object: file table object
        object: log table object
    '''
    dbi = rdbi.DataBaseInterface()
    obs_table = rdbi.Observation_
    file_table = rdbi.File_
    log_table = rdbi.Log_

    return dbi, obs_table, file_table, log_table

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    '''
    start page of the website
    grabs time data

    Returns
    -------
    html: index
    '''
    #dbi, obs_table, file_table, log_table = db_objs()

    #with dbi.session_scope() as s:
    #    pass

    return render_template('index.html')

@app.route('/stream_plot', methods = ['GET', 'POST'])
def stream_plot():
    '''
    generate streaming data

    Returns
    -------
    '''
    dbi, obs_table, file_table, log_table = db_objs()

    with dbi.session_scope() as s:
        pass

    return jsonify({'count': file_count})

@app.route('/obs_hist', methods = ['POST'])
def obs_hist():
    '''
    generate histogram for data

    Returns
    -------
    html: histogram
    '''
    dbi, obs_table, file_table, log_table = db_objs()

    with dbi.session_scope() as s:
        obs_query = s.query(obs_table, func.count(obs_table))\
                     .filter(obs_table.status == 'COMPLETE')\
                     .group_by(func.substr(obs_table.date, 1, 7))
        obs_query = ((int(float(q.date)), count) for q, count in obs_query.all())
        obs_days, obs_counts = zip(*obs_query)
        all_query = s.query(obs_table, func.count(obs_table))\
                      .group_by(func.substr(obs_table.date, 1, 7))
        all_query = ((q, count) for q, count in all_query.all())
        all_days, all_counts = zip(*all_query)

    return render_template('obs_hist.html',
                            obs_days=obs_days, obs_counts=obs_counts,
                            all_counts=all_counts)

@app.route('/prog_hist', methods = ['POST'])
def prog_hist():
    '''
    generate histogram for data

    Returns
    -------
    html: histogram
    '''
    dbi, obs_table, file_table, log_table = db_objs()

    statuses = ('NEW','UV_POT', 'UV_NFS', 'UV', 'UVC', 'CLEAN_UV', 'UVCR', 'CLEAN_UVC',
                'ACQUIRE_NEIGHBORS', 'UVCRE', 'NPZ', 'UVCRR', 'NPZ_POT',
                'CLEAN_UVCRE', 'UVCRRE', 'CLEAN_UVCRR', 'CLEAN_NPZ',
                'CLEAN_NEIGHBORS', 'UVCRRE_POT', 'CLEAN_UVCRRE', 'CLEAN_UVCR',
                'COMPLETE')

    with dbi.session_scope() as s:
        file_query = s.query(file_table, func.count(file_table))\
                      .join(obs_table)\
                      .filter(obs_table.status != 'COMPLETE')\
                      .group_by(obs_table.status)
        file_query = ((q.observation.status, count) for q, count in file_query.all())
        file_status, file_counts = zip(*file_query)

        file_status, file_counts = zip(*sorted(zip(file_status, file_counts), key=lambda x: statuses.index(x[0])))

    return render_template('prog_hist.html',
                            file_status=file_status, file_counts=file_counts)

@app.route('/obs_table', methods = ['POST'])
def obs_table():
    '''
    generate observation table for killed and failed observations

    Returns
    -------
    html: observation table
    '''
    dbi, obs_table, file_table, log_table = db_objs()
    with dbi.session_scope() as s:
        failed_obs = s.query(obs_table)\
                      .filter(obs_table.current_stage_in_progress == 'FAILED')\
                      .order_by(obs_table.current_stage_start_time)\
                      .all()
        killed_obs = s.query(obs_table)\
                      .filter(obs_table.current_stage_in_progress == 'KILLED')\
                      .order_by(obs_table.current_stage_start_time)\
                      .all()

        failed_obs = [fo.to_dict() for fo in failed_obs]
        killed_obs = [ko.to_dict() for ko in killed_obs]

    return render_template('obs_table.html', failed_obs=failed_obs, killed_obs=killed_obs)

@app.route('/file_table', methods = ['GET', 'POST'])
def file_table():
    '''
    generate file table for histogram bar

    Returns
    -------
    html: file table
    '''
    dbi, obs_table, file_table, log_table = db_objs()
    with dbi.session_scope() as s:
        #              .filter(obs_table.current_stage_in_progress != 'FAILED')\
        #              .filter(obs_table.current_stage_in_progress != 'KILLED')\
        file_query = s.query(file_table).join(obs_table)\
                      .filter((obs_table.current_stage_in_progress != 'FAILED') | (obs_table.current_stage_in_progress.is_(None)))\
                      .filter((obs_table.current_stage_in_progress != 'KILLED') | (obs_table.current_stage_in_progress.is_(None)))\
                      .filter(obs_table.status != 'NEW')\
                      .filter(obs_table.status != 'COMPLETE')\
                      .filter(obs_table.currentpid > 0)\
                      .order_by(obs_table.current_stage_start_time)
        working_FILEs = file_query.all()

        utc = datetime.datetime.now()
        working_FILEs = [(wf.to_dict(),
                          wf.observation.current_stage_in_progress,
                          int((utc - wf.observation.current_stage_start_time).total_seconds())) for wf in working_FILEs]

    return render_template('file_table.html', working_FILEs=working_FILEs)

@app.route('/summarize_still', methods = ['GET', 'POST'])
def summarize_still():
    '''
    generate summarize still page

    Returns
    -------
    html: summarize still page
    '''

    dbi, obs_table, file_table, log_table = db_objs()
    with dbi.session_scope() as s:
        OBSs = s.query(obs_table).order_by(obs_table.date)
        #JDs = (int(float(OBS.date)) for OBS in OBSs.all())
        nights = list(set(int(float(OBS.date)) for OBS in OBSs.all()))

        num_obs = s.query(obs_table)\
                   .count()
        num_progress = s.query(obs_table)\
                        .filter(obs_table.status != 'NEW')\
                        .filter(obs_table.status != 'COMPLETE')\
                        .count()
        num_complete = s.query(obs_table)\
                        .filter(obs_table.status == 'COMPLETE')\
                        .count()

        # TABLE #1: small table at top with:
        #total amount of observations, amount in progress, and amount complete

        all_complete = []
        all_total = []
        all_pending = []
        pending = 0

        completeness = []


        for night in nights:
            night_complete = s.query(obs_table)\
                              .filter(obs_table.date.like(str(night) + '%'))\
                              .filter(obs_table.status == 'COMPLETE')\
                              .count()
            night_total = s.query(obs_table)\
                           .filter(obs_table.date.like(str(night) + '%'))\
                           .count()
            OBSs = s.query(obs_table)\
                    .filter(obs_table.date.like(str(night) + '%'))
            obsnums = [OBS.obsnum for OBS in OBSs.all()]
            complete_obsnums = [OBS.obsnum for OBS in OBSs.all() if OBS.status != 'COMPLETE']

            pending = s.query(obs_table)\
                       .filter(obs_table.date.like(str(night) + '%'))\
                       .filter(obs_table.status != 'COMPLETE')\
                       .count()

            #pending = s.query(log_table)\
            #           .filter(log_table.obsnum.in_(complete_obsnums))\
            #           .count()
                       #.filter(log_table.obsnum.in_(obsnums))\
                       #.filter(log_table.stage != 'COMPLETE')\
                       #.filter(obs_table.status != 'COMPLETE')\

            all_complete.append(night_complete)
            all_total.append(night_total)
            all_pending.append(pending)

            # TABLE #3:
            #night_table: nights, complete, total, pending: histogram for each JD vs amount

            if s.query(log_table)\
                .filter(log_table.obsnum.in_(obsnums))\
                .count() < 1:
                completeness.append((night, 0, night_total, 'Pending'))
                #print(night, ':', 'completeness', 0, '/', night_total, '[Pending]')

            # TABLE #2a:
            #night completeness table

            try:
                LOG = s.query(log_table)\
                       .filter(log_table.obsnum.in_(obsnums))\
                       .order_by(log_table.timestamp.desc())\
                       .first()
                       #.one()
                       #I think this was an error, gets most recent log rather than
                       #making sure there is only one

                if LOG.timestamp > (datetime.datetime.utcnow() - datetime.timedelta(5.0)):
                    completeness.append((night, night_complete, night_total, LOG.timestamp))
                    #print(night, ':', 'completeness', night_complete, '/', night_total, LOG.timestamp)

                # TABLE #2b:
                #night completeness table with log timestamp for last entry

                FAIL_LOGs = s.query(log_table)\
                             .filter(log_table.exit_status > 0)\
                             .filter(log_table.timestamp > (datetime.datetime.utcnow() - datetime.timedelta(0.5)))\
                             .all()
                fail_obsnums = [LOG_ENTRY.obsnum for LOG_ENTRY in FAIL_LOGs]
            except:
                #print('No entries in LOG table')
                fail_obsnums = []


        # find all obses that have failed in the last 12 hours
        #print('observations pending: %s') % pending

        # break it down by stillhost
        #print('fails in the last 12 hours')

        fails = []
        f_obs = []

        f_stills = []
        f_counts = []

        if len(fail_obsnums) < 1:
            print('None')
        else:
            FAIL_OBSs = s.query(obs_table)\
                         .filter(obs_table.obsnum.in_(fail_obsnums))\
                         .order_by(obs_table.stillhost)\
                         .all()
            fail_stills = list(set([OBS.stillhost for OBS in FAIL_OBSs]))  # list of stills with fails

            for fail_still in fail_stills:
                # get failed obsnums broken down by still
                fail_count = s.query(obs_table)\
                              .filter(obs_table.obsnum.in_(fail_obsnums))\
                              .filter(obs_table.stillhost == fail_still)\
                              .count()
                #print('Fail Still : %s , Fail Count %s') % (fail_still, fail_count)
                fails.append((fail_still, fail_count))

            f_stills, f_counts = zip(*fails)

            # TABLE #4:
            # histogram with Still# and Failing Count


            #print('most recent fails')
            for FAIL_OBS in FAIL_OBSs:
            #    print(FAIL_OBS.obsnum, FAIL_OBS.status, FAIL_OBS.stillhost)
                f_obs.append((FAIL_OBS.obsnum, FAIL_OBS.status, FAIL_OBS.stillhost))

        # TABLE #5:
        #fail table with obsnum, status, and stillhost for each failed obs


        #print('Number of observations completed in the last 24 hours')

        good_obscount = s.query(log_table)\
                         .filter(log_table.exit_status == 0)\
                         .filter(log_table.timestamp > (datetime.datetime.utcnow() - datetime.timedelta(1.0)))\
                         .filter(log_table.stage == 'CLEAN_UVCRE')\
                         .count()  # HARDWF
        #print('Good count: %s') % good_obscount


        # TABLE #6:
        #Label at bottom with Good Observations #, i.e. number of obs completed within the last 24 hours

    return render_template('summarize_still.html',
                            num_obs=num_obs, num_progress=num_progress, num_complete=num_complete,
                            nights=nights,
                            all_complete=all_complete, all_total=all_total, all_pending=all_pending,
                            completeness=completeness,
                            f_stills=f_stills, f_counts=f_counts,
                            f_obs=f_obs, good_obscount=good_obscount)
