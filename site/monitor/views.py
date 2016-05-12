'''
rtp.site.monitor.views

author | Immanuel Washington

Functions
---------
db_objs | gathers database objects for use
index | shows main page
stream_plot | streaming plot example
file_hist | creates histogram
obs_table | shows observation table
file_table | shows file table
'''
import datetime
from flask import render_template, flash, redirect, url_for, request, g, make_response, Response, jsonify
from rtp.site.flask_app import monitor_app as app, monitor_db as db
from rtp.site.monitor import dbi as rdbi
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
    obs_table = rdbi.Observation
    file_table = rdbi.File
    log_table = rdbi.Log

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

@app.route('/file_hist', methods = ['POST'])
def file_hist():
    '''
    generate histogram for data

    Returns
    -------
    html: histogram
    '''
    dbi, obs_table, file_table, log_table = db_objs()

    with dbi.session_scope() as s:
        file_query = s.query(file_table, func.count(file_table))\
                      .join(obs_table)\
                      .filter(obs_table.status != 'COMPLETE')\
                      .group_by(func.substr(file_table.filename, 5, 7))
        file_query = ((q.filename.split('.')[1], count) for q, count in file_query.all())
        file_days, file_counts = zip(*file_query)
        all_query = s.query(file_table, func.count(file_table))\
                      .group_by(func.substr(file_table.filename, 5, 7))
        all_query = ((q, count) for q, count in all_query.all())
        all_days, all_counts = zip(*all_query)

    return render_template('file_hist.html',
                            file_days=file_days, file_counts=file_counts,
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

    statuses = ('NEW','UV_POT', 'UV', 'UVC', 'CLEAN_UV', 'UVCR', 'CLEAN_UVC',
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

        working_FILEs = [(wf.to_dict(), wf.observation.current_stage_start_time) for wf in working_FILEs]
    #need some way to include time subtraction from current stage start time and current time
    utc = datetime.datetime.now()

    return render_template('file_table.html', working_FILEs=working_FILEs, utc=utc)
