'''
rtp.site.monitor.views

author | Immanuel Washington

Functions
---------
db_objs | gathers database objects for use
page_args | gathers page arguments for use
page_form | gathers page form info for use
obs_filter | filters observation query
file_filter | filters file query
index | shows main page
stream_plot | streaming plot example
data_hist | creates histogram
obs_table | shows observation table
save_obs | generates observation json file
file_table | shows file table
save_files | generates file json file
data_summary_table | shows data summary table
day_summary_table | shows day summary table
'''
from flask import render_template, flash, redirect, url_for, request, g, make_response, Response, jsonify
import json
import time
from datetime import datetime
from rtp.site.flask_app import monitor_app as app, monitor_db as db
import dbi as rdbi
from sqlalchemy import func
import numpy as np

def db_objs():
    '''
    outputs database objects

    Returns
    -------
    tuple:
        object: database interface object
        object: observation table object
        object: file table object
    '''
    dbi = rdbi.DataBaseInterface()
    obs_table = rdbi.Observation
    file_table = rdbi.File

    return dbi, obs_table, file_table
"""
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
    jdstart = request.args.get('jd_start', 2455903)
    jdend = request.args.get('jd_end', 2455904)
    starttime = request.args.get('starttime', None)
    endtime = request.args.get('endtime', None)

    polarization = request.args.get('polarization', 'all')
    era_type = request.args.get('era_type', 'None')
    host = request.args.get('host', 'folio')
    filetype = request.args.get('filetype', 'uv')

    start_utc, end_utc = time_fix(jdstart, jdend, starttime, endtime)

    return start_utc, end_utc, polarization, era_type, host, filetype

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
    jdstart = request.form.get('jd_start', 2455903)
    jdend = request.form.get('jd_end', 2455904)
    starttime = request.form.get('starttime', None)
    endtime = request.form.get('endtime', None)

    polarization = request.form.get('polarization', 'all')
    era_type = request.form.get('era_type', 'None')
    host = request.form.get('host', 'folio')
    filetype = request.form.get('filetype', 'uv')

    start_utc, end_utc = time_fix(jdstart, jdend, starttime, endtime)

    return start_utc, end_utc, polarization, era_type, host, filetype
"""
def obs_filter(obs_query, obs_table, start_utc, end_utc, polarization, era_type):
    '''
    filters observation query

    Parameters
    ----------
    obs_query | object: SQLalchemy observation table query object
    obs_table | object: SQLalchemy observation table object
    start_utc | float: starting julian date
    end_utc | float: ending julian date
    polarization | str: polarization to limit
    era_type | str: era type to limit

    Returns
    -------
    object: observation query
    '''
    obs_query = obs_query.filter(obs_table.time_start >= start_utc)\
                         .filter(obs_table.time_end <= end_utc)
    if polarization != 'any':
        obs_query = obs_query.filter(obs_table.polarization == polarization)
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
    filetype | str: era type to limit

    Returns
    -------
    object: file query
    '''
    if host != 'all':
        file_query = file_query.filter(file_table.host == host)
    if filetype != 'all':
        file_query = file_query.filter(file_table.filetype == filetype)

    return file_query

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
    start_utc, end_utc, polarization, era_type, host, filetype = page_args()

    dbi, obs_table, file_table = db_objs()

    with dbi.session_scope() as s:
        days = list(range(int(start_utc), int(end_utc) + 1))
        #get julian_day, count for files, split by raw/compressed
        file_query = s.query(file_table, func.count(file_table))\
                      .join(obs_table)
        file_query = obs_filter(file_query, obs_table, start_utc, end_utc, polarization, era_type)
        file_query = file_filter(file_query, file_table, host, filetype)

        file_query = file_query.group_by(obs_table.julian_day).order_by(obs_table.julian_day.asc()).all()
        file_query = ((q.observation.julian_day, count) for q, count in file_query)
        try:
            f_days, f_day_counts = zip(*file_query)
        except:
            f_days = days
            f_day_counts = [0] * len(days)

        #get julian_day, count for observation
        obs_query = s.query(obs_table.julian_day, func.count(obs_table))
        obs_query = obs_filter(obs_query, obs_table, start_utc, end_utc, polarization, era_type)

        obs_query = obs_query.group_by(obs_table.julian_day).order_by(obs_table.julian_day.asc()).all()
        try:
            j_days, j_day_counts = zip(*obs_query)
        except:
            j_days = days
            j_day_counts = [0] * len(days)

    return render_template('index.html',
                            start_utc=start_utc, end_utc=end_utc,
                            polarization=polarization, d_pol=polarization,
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
    start_utc, end_utc, polarization, era_type, host, filetype = page_form()

    dbi, obs_table, file_table = db_objs()

    with dbi.session_scope() as s:
        file_query = s.query(file_table, func.count(file_table))\
                      .join(obs_table)
        file_query = obs_filter(file_query, obs_table, start_utc, end_utc, polarization, era_type)
        file_query = file_filter(file_query, file_table, host, filetype)
        file_query = file_query.group_by(obs_table.julian_day).order_by(obs_table.julian_day.asc()).limit(1)

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
    start_utc, end_utc, polarization, era_type, host, filetype = page_form()

    dbi, obs_table, file_table = db_objs()

    with dbi.session_scope() as s:
        days = list(range(int(start_utc), int(end_utc) + 1))
        #get julian_day, count for files, split by raw/compressed
        file_query = s.query(file_table, func.count(file_table))\
                      .join(obs_table)
        file_query = obs_filter(file_query, obs_table, start_utc, end_utc, polarization, era_type)
        file_query = file_filter(file_query, file_table, host, filetype)

        file_query = file_query.group_by(obs_table.julian_day).order_by(obs_table.julian_day.asc()).all()
        file_query = ((q.observation.julian_day, count) for q, count in file_query)
        try:
            f_days, f_day_counts = zip(*file_query)
        except:
            f_days = days
            f_day_counts = [0] * len(days)

        #get julian_day, count for observation
        obs_query = s.query(obs_table.julian_day, func.count(obs_table))
        obs_query = obs_filter(obs_query, obs_table, start_utc, end_utc, polarization, era_type)

        obs_query = obs_query.group_by(obs_table.julian_day).order_by(obs_table.julian_day.asc()).all()
        try:
            j_days, j_day_counts = zip(*obs_query)
        except:
            j_days = days
            j_day_counts = [0] * len(days)

    return render_template('data_hist.html',
                            f_days=f_days, f_day_counts=f_day_counts,
                            j_days=j_days, j_day_counts=j_day_counts)

@app.route('/obs_table', methods = ['POST'])
def obs_table():
    '''
    generate observation table for histogram bar

    Returns
    -------
    html: observation table
    '''
    start_utc, end_utc, polarization, era_type, host, filetype = page_form()

    output_vars = ('obsnum', 'julian_date', 'polarization', 'length')

    dbi, obs_table, file_table = db_objs()
    with dbi.session_scope() as s:
        obs_query = s.query(obs_table)
        obs_query = obs_filter(obs_query, obs_table, start_utc, end_utc, polarization, era_type)
        obs_query = obs_query.order_by(obs_table.julian_date.asc()).all()

        log_list = [{var: getattr(obs, var) for var in output_vars} for obs in obs_query]

    return render_template('obs_table.html',
                            log_list=log_list, output_vars=output_vars,
                            start_time=start_utc, end_time=end_utc,
                            polarization=polarization, era_type=era_type)

@app.route('/file_table', methods = ['GET', 'POST'])
def file_table():
    '''
    generate file table for histogram bar

    Returns
    -------
    html: file table
    '''
    start_utc, end_utc, polarization, era_type, host, filetype = page_form()

    output_vars = ('host', 'source', 'obsnum', 'filesize')

    dbi, obs_table, file_table = db_objs()
    with dbi.session_scope() as s:
        file_query = s.query(file_table).join(obs_table)
        file_query = obs_filter(file_query, obs_table, start_utc, end_utc, polarization, era_type)
        file_query = file_filter(file_query, file_table, host, filetype)
        
        log_list = [{var: getattr(rtp_file, var) for var in output_vars}
                    for rtp_file in file_query.order_by(obs_table.time_start.asc()).all()]

    return render_template('file_table.html',
                            log_list=log_list, output_vars=output_vars,
                            start_time=start_utc, end_time=end_utc,
                            host=host, filetype=filetype)

@app.route('/day_summary_table', methods=['POST'])
def day_summary_table():
    '''
    summary of data in main databases

    Returns
    -------
    html: day summary table
    '''
    start_utc, end_utc, polarization, era_type, host, filetype = page_form()

    dbi, obs_table, file_table = db_objs()

    with dbi.session_scope() as s:
        pol_query = s.query(obs_table.julian_day, obs_table.polarization, func.count(obs_table))
        pol_query = obs_filter(pol_query, obs_table, start_utc, end_utc, polarization, era_type)
        pol_query = pol_query.group_by(obs_table.julian_day, obs_table.polarization).order_by(obs_table.julian_day.asc()).all()

        pol_map = tuple((julian_day, pol, count) for julian_day, pol, count in pol_query)

    return render_template('day_summary_table.html', pol_map=pol_map)
