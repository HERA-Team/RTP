'''
RTP.site.monitor.views

author | Immanuel Washington

Functions
---------
db_objs | gathers database objects for use
index | shows main page
obs_hist | creates histogram
obs_table | shows observation table
file_table | shows file table
time_fix | fixes times for observation input
page_args | gathers page arguments for use
page_form | gathers page form info for use
obs_filter | filters observation query
file_filter | filters file query
index | shows main page
stream_plot | streaming plot example
data_hist | creates histogram
search_obs | shows observation table
save_obs | generates observation json file
search_file | shows file table
save_files | generates file json file
data_summary_table | shows data summary table
day_summary_table | shows day summary table
'''
from __future__ import print_function
import os
import sys
base_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(base_dir))
from flask_app import monitor_app as app
import datetime
import json
from flask import render_template, flash, redirect, url_for,\
                  request, g, make_response, Response, jsonify
from sqlalchemy import func
import rdbi
import misc_utils

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
        all_query = s.query(obs_table, func.count(obs_table))\
                      .group_by(func.substr(obs_table.date, 1, 7))
        all_query = tuple((int(float(q.date)), count) for q, count in all_query.all())
        all_days, all_counts = zip(*all_query)

        obs_query = s.query(obs_table, func.count(obs_table))\
                     .filter(obs_table.status == 'COMPLETE')\
                     .group_by(func.substr(obs_table.date, 1, 7))
        obs_query = ((int(float(q.date)), count) for q, count in obs_query.all())
        obs_counts = [count if day in all_days else 0 for day, count in obs_query]
        #obs_days, obs_counts = zip(*obs_query)
        obs_days = []

    return render_template('obs_hist.html',
                            obs_days=obs_days, obs_counts=obs_counts,
                            all_days=all_days, all_counts=all_counts)

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

@app.route('/alert_log', methods = ['GET', 'POST'])
def alert_log():
    '''
    saves file metadata as json

    Returns
    -------
    html: json file
    '''
    obsnum = request.args.get('obsnum')

    dbi, obs_table, file_table, log_table = db_objs()
    with dbi.session_scope() as s:
        log_query = s.query(log_table).filter(log_table.obsnum == obsnum)

        entry_list = [rtp_log.to_dict() for rtp_log in log_query.order_by(log_table.lognum.asc()).all()]

    for entry in entry_list:
        for index, log in enumerate(entry['logtext'].strip().split('\n')):
            entry['logtext_{index}'.format(index=index)] = log
        del entry['logtext']
        
    log_data =  json.dumps(entry_list, sort_keys=True,
                           indent=4, default=rdbi.decimal_default)

    print(log_data)
    return log_data
    #return Response(response=json.dumps(entry_list, sort_keys=True,
    #                indent=4, default=rdbi.decimal_default),
    #                status=200, mimetype='application/json',
    #                headers={'Content-Disposition': 'attachment; filename=file.json'})

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

def time_fix(jdstart, jdend, starttime=None, endtime=None):
    '''
    fixes times for observations

    Parameters
    ----------
    jdstart | str: starting time of julian date
    jdend | str: ending time of julian date
    starttime | str: string of start time --defaults to None
    endtime | str: string of end time --defaults to None

    Returns
    -------
    tuple:
        float(5): julian date start time
        float(5): julian date end time
    '''
    try:
        jd_start = round(float(jdstart), 5)
        jd_end = round(float(jdend), 5)
    except:
        jd_start = None
        jd_end = None

    if jd_start == None:
        startdatetime = datetime.datetime.strptime(starttime, '%Y-%m-%dT%H:%M:%SZ')
        enddatetime = datetime.datetime.strptime(endtime, '%Y-%m-%dT%H:%M:%SZ')
        start_utc, end_utc = misc_utils.get_jd_from_datetime(startdatetime,
                                                             enddatetime)
    else:
        start_utc, end_utc = jd_start, jd_end

    return start_utc, end_utc

def page_args():
    '''
    outputs relevant page argument info

    Returns
    -------
    tuple:
        float: julian start date
        float: julian end date
        str: polarization
        str: era type
        str: host
        str: filetype
    '''
    jdstart = request.args.get('jd_start', 2456617)
    jdend = request.args.get('jd_end', 2456620)
    starttime = request.args.get('starttime', None)
    endtime = request.args.get('endtime', None)

    pol = request.args.get('polarization', 'any')
    era_type = request.args.get('era_type', 'None')
    host = request.args.get('host', 'all')
    filetype = request.args.get('filetype', 'all')

    start_utc, end_utc = time_fix(jdstart, jdend, starttime, endtime)

    return start_utc, end_utc, pol, era_type, host, filetype

def page_form():
    '''
    outputs relevant page form info

    Returns
    -------
    tuple:
        float: julian start date
        float: julian end date
        str: polarization
        str: era type
        str: host
        str: filetype
    '''
    jdstart = request.form.get('jd_start', 2456617)
    jdend = request.form.get('jd_end', 2456620)
    starttime = request.form.get('starttime', None)
    endtime = request.form.get('endtime', None)

    pol = request.form.get('polarization', 'any')
    era_type = request.form.get('era_type', 'None')
    host = request.form.get('host', 'all')
    filetype = request.form.get('filetype', 'all')

    start_utc, end_utc = time_fix(jdstart, jdend, starttime, endtime)

    return start_utc, end_utc, pol, era_type, host, filetype

def obs_filter(obs_query, obs_table, start_utc, end_utc, pol, era_type):
    '''
    filters observation query

    Parameters
    ----------
    obs_query | object: SQLalchemy observation table query object
    obs_table | object: SQLalchemy observation table object
    start_utc | float: starting julian date
    end_utc | float: ending julian date
    pol | str: polarization to limit
    era_type | str: era type to limit

    Returns
    -------
    object: observation query
    '''
    obs_query = obs_query.filter(obs_table.date >= start_utc)\
                         .filter(obs_table.date <= end_utc)
    if pol != 'any':
        obs_query = obs_query.filter(obs_table.pol == pol)
    if era_type not in ('all', 'None'):
        obs_query = obs_query.filter(obs_table.era_type == era_type)

    return obs_query

def file_filter(file_query, file_table, host, filetype):
    '''
    filters file query

    Parameters
    ----------
    file_query | object: SQLalchemy file table query object
    file_table | object: SQLalchemy file table object
    host | str: host to limit
    filetype | str: file type to limit

    Returns
    -------
    object: file query
    '''
    if host != 'all':
        file_query = file_query.filter(file_table.host == host)
    if filetype != 'all':
        file_query = file_query\
                    .filter(func.substring_index(file_table.filename, '.', -1) == filetype)

    return file_query

@app.route('/search', methods=['GET', 'POST'])
def search():
    '''
    start page of the website
    grabs time data

    Returns
    -------
    html: index
    '''
    polarization_dropdown, era_type_dropdown,\
    host_dropdown, filetype_dropdown = misc_utils.get_dropdowns()

    start_utc, end_utc, pol, era_type, host, filetype = page_args()

    dbi, obs_table, file_table, log_table = db_objs()

    with dbi.session_scope() as s:
        days = list(range(int(start_utc), int(end_utc) + 1))
        #get julian_day, count for files, split by raw/compressed
        file_query = s.query(file_table, func.count(file_table))\
                      .join(obs_table)
        file_query = obs_filter(file_query, obs_table,
                                start_utc, end_utc,
                                pol, era_type)
        file_query = file_filter(file_query, file_table, host, filetype)

        file_query = file_query\
                    .group_by(func.substr(obs_table.date, 1, 7))\
                    .order_by(func.substr(obs_table.date, 1, 7).asc())\
                    .all()
        file_query = ((q.observation.julian_day, count) for q, count in file_query)
        try:
            f_days, f_day_counts = zip(*file_query)
        except:
            f_days = days
            f_day_counts = [0] * len(days)

        #get julian_day, count for observation
        obs_query = s.query(func.substr(obs_table.date, 1, 7),
                            func.count(obs_table))
        obs_query = obs_filter(obs_query, obs_table,
                               start_utc, end_utc,
                               pol, era_type)

        obs_query = obs_query.group_by(func.substr(obs_table.date, 1, 7))\
                             .order_by(func.substr(obs_table.date, 1, 7).asc())\
                             .all()
        try:
            j_days, j_day_counts = zip(*obs_query)
        except:
            j_days = days
            j_day_counts = [0] * len(days)

    return render_template('search.html',
                            polarization_dropdown=polarization_dropdown,
                            era_type_dropdown=era_type_dropdown,
                            host_dropdown=host_dropdown,
                            filetype_dropdown=filetype_dropdown,
                            start_utc=start_utc, end_utc=end_utc,
                            pol=pol, d_pol=pol,
                            era_type=era_type, d_et=era_type,
                            host=host, d_host=host,
                            filetype=filetype, d_ft=filetype,
                            days=days,
                            f_days=f_days, f_day_counts=f_day_counts,
                            j_days=j_days, j_day_counts=j_day_counts)

@app.route('/stream_plot', methods = ['GET', 'POST'])
def stream_plot():
    '''
    generate streaming data

    Returns
    -------
    '''
    start_utc, end_utc, pol, era_type, host, filetype = page_form()

    dbi, obs_table, file_table, log_table = db_objs()

    with dbi.session_scope() as s:
        file_query = s.query(file_table, func.count(file_table))\
                      .join(obs_table)
        file_query = obs_filter(file_query, obs_table,
                                start_utc, end_utc,
                                pol, era_type)
        file_query = file_filter(file_query, file_table, host, filetype)
        file_query = file_query.group_by(func.substr(obs_table.date, 1, 7))\
                               .order_by(func.substr(obs_table.date, 1, 7)\
                               .asc())\
                               .limit(1)

        file_count = [count for q, count in file_query]

    return jsonify({'count': file_count})

@app.route('/data_hist', methods = ['POST'])
def data_hist():
    '''
    generate histogram for data

    Returns
    -------
    html: histogram
    '''
    start_utc, end_utc, pol, era_type, host, filetype = page_form()

    dbi, obs_table, file_table, log_table = db_objs()
    with dbi.session_scope() as s:
        days = list(range(int(start_utc), int(end_utc) + 1))
        #get julian_day, count for files, split by raw/compressed
        file_query = s.query(file_table, func.count(file_table))\
                      .join(obs_table)
        file_query = obs_filter(file_query, obs_table,
                                start_utc, end_utc,
                                pol, era_type)
        file_query = file_filter(file_query, file_table, host, filetype)

        file_query = file_query.group_by(func.substr(obs_table.date, 1, 7))\
                               .order_by(func.substr(obs_table.date, 1, 7)\
                               .asc())\
                               .all()
        file_query = ((int(float(q.observation.date)), count) for q, count in file_query)
        try:
            f_days, f_day_counts = zip(*file_query)
        except:
            f_days = days
            f_day_counts = [0] * len(days)

        #get julian_day, count for observation
        obs_query = s.query(func.substr(obs_table.date, 1, 7),
                            func.count(obs_table))
        obs_query = obs_filter(obs_query, obs_table,
                               start_utc, end_utc,
                               pol, era_type)

        obs_query = obs_query.group_by(func.substr(obs_table.date, 1, 7))\
                             .order_by(func.substr(obs_table.date, 1, 7)\
                             .asc())\
                             .all()
        try:
            j_days, j_day_counts = zip(*obs_query)
        except:
            j_days = days
            j_day_counts = [0] * len(days)

    return render_template('data_hist.html',
                            f_days=f_days, f_day_counts=f_day_counts,
                            j_days=j_days, j_day_counts=j_day_counts)

@app.route('/search_obs', methods = ['POST'])
def search_obs():
    '''
    generate observation table for histogram bar

    Returns
    -------
    html: observation table
    '''
    start_utc, end_utc, pol, era_type, host, filetype = page_form()

    output_vars = ('obsnum', 'date', 'pol', 'length')

    dbi, obs_table, file_table, log_table = db_objs()
    with dbi.session_scope() as s:
        obs_query = s.query(obs_table)
        obs_query = obs_filter(obs_query, obs_table,
                               start_utc, end_utc,
                               pol, era_type)
        obs_query = obs_query.order_by(obs_table.date.asc()).all()

        log_list = [{var: getattr(obs, var) for var in output_vars} for obs in obs_query]

    return render_template('search_obs.html',
                            log_list=log_list, output_vars=output_vars,
                            start_time=start_utc, end_time=end_utc,
                            pol=pol, era_type=era_type)

@app.route('/save_obs', methods = ['GET'])
def save_obs():
    '''
    saves observations as json

    Returns
    -------
    html: json file
    '''
    start_utc, end_utc, pol, era_type, host, filetype = page_args()

    dbi, obs_table, file_table, log_table = db_objs()
    with dbi.session_scope() as s:
        obs_query = s.query(obs_table)
        obs_query = obs_filter(obs_query, obs_table,
                               start_utc, end_utc,
                               pol, era_type)
        obs_query = obs_query.order_by(obs_table.date.asc()).all()

        entry_list = [obs.to_dict() for obs in obs_query]

    return Response(response=json.dumps(entry_list, sort_keys=True,
                    indent=4, default=rdbi.decimal_default),
                    status=200, mimetype='application/json',
                    headers={'Content-Disposition': 'attachment; filename=obs.json'})

@app.route('/search_file', methods = ['GET', 'POST'])
def search_file():
    '''
    generate file table for histogram bar

    Returns
    -------
    html: file table
    '''
    start_utc, end_utc, pol, era_type, host, filetype = page_form()

    output_vars = ('host', 'filename', 'obsnum')

    dbi, obs_table, file_table, log_table = db_objs()
    with dbi.session_scope() as s:
        file_query = s.query(file_table).join(obs_table)
        file_query = obs_filter(file_query, obs_table,
                                start_utc, end_utc,
                                pol, era_type)
        file_query = file_filter(file_query, file_table, host, filetype)
        
        log_list = [{var: getattr(rtp_file, var) for var in output_vars}
                    for rtp_file in file_query.order_by(obs_table.date.asc()).all()]

    return render_template('search_file.html',
                            log_list=log_list, output_vars=output_vars,
                            start_time=start_utc, end_time=end_utc,
                            host=host, filetype=filetype)

@app.route('/save_files', methods = ['GET'])
def save_files():
    '''
    saves file metadata as json

    Returns
    -------
    html: json file
    '''
    start_utc, end_utc, pol, era_type, host, filetype = page_args()

    dbi, obs_table, file_table, log_table = db_objs()
    with dbi.session_scope() as s:
        file_query = s.query(file_table).join(obs_table)
        file_query = obs_filter(file_query, obs_table,
                                start_utc, end_utc,
                                pol, era_type)
        file_query = file_filter(file_query, file_table, host, filetype)

        entry_list = [rtp_file.to_dict() for rtp_file in file_query.order_by(obs_table.date.asc()).all()]

    return Response(response=json.dumps(entry_list, sort_keys=True,
                    indent=4, default=rdbi.decimal_default),
                    status=200, mimetype='application/json',
                    headers={'Content-Disposition': 'attachment; filename=file.json'})

@app.route('/data_summary_table', methods=['POST'])
def data_summary_table():
    '''
    summary of data in main databases

    Returns
    -------
    html: data summary table
    '''
    start_utc, end_utc, pol, era_type, host, filetype = page_form()

    pol_strs, era_type_strs,\
    host_strs, filetype_strs = misc_utils.get_set_strings()
    file_map = {host_str: {filetype_str: {'file_count': 0}\
                for filetype_str in filetype_strs} for host_str in host_strs}

    dbi, obs_table, file_table, log_table = db_objs()
    with dbi.session_scope() as s:
        file_query = s.query(file_table.host,
                             func.substring_index(file_table.filename, '.', -1),
                             func.count(file_table))\
                      .group_by(file_table.host,
                                func.substring_index(file_table.filename, '.', -1))\
                      .all()
        for host, filetype, count in file_query:
            file_map[host][filetype].update({'file_count': count})

    all_file_strs = host_strs + filetype_strs
    file_total = {all_file_str: {'count': 0} for all_file_str in all_file_strs}

    for host in host_strs:
        for filetype in filetype_strs:
            file_count = file_map[host][filetype]['file_count']
            file_total[filetype]['count'] += file_count
            file_total[host]['count'] += file_count

    no_files = {filetype: {'file_count': 0} for filetype in filetype_strs}
    host_strs = tuple(host for host, filetype_dict in file_map.items()\
                           if filetype_dict != no_files)

    return render_template('data_summary_table.html',
                            host_strs=host_strs, filetype_strs=filetype_strs,
                            file_map=file_map, file_total=file_total)

@app.route('/day_summary_table', methods=['POST'])
def day_summary_table():
    '''
    summary of data in main databases

    Returns
    -------
    html: day summary table
    '''
    start_utc, end_utc, pol, era_type, host, filetype = page_form()

    dbi, obs_table, file_table, log_table = db_objs()

    with dbi.session_scope() as s:
        pol_query = s.query(func.substr(obs_table.date, 1, 7), obs_table.pol, func.count(obs_table))
        pol_query = obs_filter(pol_query, obs_table, start_utc, end_utc, pol, era_type)
        pol_query = pol_query.group_by(func.substr(obs_table.date, 1, 7), obs_table.pol).order_by(func.substr(obs_table.date, 1, 7).asc()).all()

        pol_map = tuple((julian_day, pol, count) for julian_day, pol, count in pol_query)

    return render_template('day_summary_table.html', pol_map=pol_map)
