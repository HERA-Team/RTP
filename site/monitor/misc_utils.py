'''
paper.site.misc_utils

author | Immanuel Washington

Functions
---------
time_val | processes time to be human readable
str_val | processes time to give human readable unit
get_set_strings | acquires all possible values for set strings
get_dropdowns | acquires keys and values for dropdown lists
get_jd_from_datetime | calculates start and end julian dates from datetimes
get_utc_from_datetime | calculates utc time from datetime
'''
from datetime import datetime
from convert import gcal_to_jd

def time_val(value):
    '''
    determines how much time to divide by and divides time by that to make human readable

    Parameters
    ----------
    value | float: numerical time value

    Returns
    -------
    float: numerical time value divided

    >>> time_val(143)
    143
    >>> time_val(675)
    11
    '''
    time_val = 1 if value < 500 else 60 if value < 3600 else 3600 if value < 86400 else 86400

    return value / time_val

def str_val(value):
    '''
    determines which time unit to use

    Parameters
    ----------
    value | float: numerical time value

    Returns
    -------
    str: time unit

    >>> time_val(143)
    seconds ago
    >>> time_val(675)
    minutes ago
    '''
    str_val = 'seconds' if value < 500 else 'minutes' if value < 3600 else 'hours' if value < 86400 else 'days'
    str_val = ' '.join((str_val, 'ago'))

    return str_val

def get_set_strings():
    '''
    output a list of set strings for main filterable fields

    Returns
    -------
    tuple:
        list[str]: set strings for polarization
        list[str]: set strings for era type
        list[str]: set strings for host
        list[str]: set strings for filetype
    '''
    pol_strs = ('all', 'xx', 'xy', 'yx', 'yy')
    era_type_strs = ('all', 'None')
    host_strs = ('all', 'pot1', 'pot2', 'pot3', 'pot4', 'pot5', 
                 'folio', 'pot8', 'nas1', 'nas2', 'nas5', 'node16')
    filetype_strs = ('uv', 'uvcRRE', 'npz', 'uvc', 'uvcR', 'uvcRE')

    return pol_strs, era_type_strs, host_strs, filetype_strs

def get_dropdowns():
    '''
    output a list of tuples which indicate dropdown strings and values other than default value

    Returns
    -------
    tuple:
        tuple[str]: keys and values for polarization
        tuple[str]: keys and values for era type
        tuple[str]: keys and values for host
        tuple[str]: keys and values for filetype
    '''
    pol_dropdown = (('all', 'all'), ('xx', 'xx'), ('xy', 'xy'), ('yx', 'yx'), ('yy', 'yy'), ('any', 'any'))
    era_type_dropdown = (('None', 'None'), ('all', 'all'),)
    host_dropdown = (('folio', 'folio'), ('all', 'all'), ('pot1', 'pot1'), ('pot2', 'pot2'),
                        ('pot3', 'pot3'), ('pot8', 'pot8'), ('nas1', 'nas1'), ('node16', 'node16'))
    filetype_dropdown = (('uv', 'raw'), ('all', 'all'), ('uvcRRE', 'compressed'), ('npz', 'flags'),
                         ('uvc', 'uvc'), ('uvcR', 'uvcR'), ('uvcRE', 'uvcRE'))

    return pol_dropdown, era_type_dropdown, host_dropdown, filetype_dropdown

def get_jd_from_datetime(start_time=None, end_time=None):
    '''
    generates julian date from datetime -- either object or string

    Parameters
    ----------
    start_time | object/str: start time --defaults to None
    end_time | object/str: end time --defaults to None

    Returns
    -------
    tuple:
        float: time start of julian date
        float: time end of julian date
    OR
    float: time start of julian date
    '''
    time_start = None
    time_end = None
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S')
    if start_time is not None:
        time_start = gcal_to_jd(start_time.year, start_time.month, start_time.day, start_time.hour, start_time.minute, start_time.second)
    if end_time is not None:
        time_end = gcal_to_jd(end_time.year, end_time.month, end_time.day, end_time.hour, end_time.minute, end_time.second)
    if time_end is None:
        return time_start

    return time_start, time_end

def get_utc_from_datetime(date_time):
    '''
    generates utc in seconds from datetime object

    Parameters
    ----------
    date_time | object: datetime object

    Returns
    -------
    int: utc in seconds
    '''
    utc = (date_time - datetime(1970, 1, 1)).total_seconds()

    return utc
