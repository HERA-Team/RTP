'''
paper.convert

author | Immanuel Washington

Functions
---------
hours_to_degrees
hours_to_radians
degrees_to_hours
radians_to_hours
decimal_to_sexagesimal
sexagesimal_to_decimal
ipart | integer part of number as float
gcal_to_jd | gregorian time date to julian date
jd_to_gcal | julian date to gregorian time date
time_to_decimal
decimal_to_time
date_to_juliandate
datetime_to_juliandate
juliandate_to_modifiedjd
modifiedjd_to_juliandate
datetime_to_modifiedjd
juliandate_to_gmst
utc_to_gmst
gmst_to_utc
juliandate_to_utc
modifiedjd_to_utc
gmst_to_lst
lst_to_gmst
utc_to_lst
gps_to_utc
utc_to_gps
gps_from_string
gps_to_lst
gps_to_datetime
datetime_to_gps
'''
from __future__ import print_function
from time import strptime
import datetime
import math
import calendar
import numpy as np

LEAP_SECONDS = (('July 1, 2015', 17),
                ('July 1, 2012', 16),
                ('January 1, 2009', 15),
                ('January 1, 2006', 14),
                ('January 1, 1999', 13),
                ('July 1, 1997', 12),
                ('January 1, 1996', 11),
                ('July 1, 1994', 10),
                ('July 1, 1993', 9),
                ('July 1, 1992', 8),
                ('January 1, 1991', 7),
                ('January 1, 1990', 6),
                ('January 1, 1988', 5),
                ('July 1, 1985', 4),
                ('July 1, 1983', 3),
                ('July 1, 1982', 2),
                ('July 1, 1981', 1))

MJD_0 = 2400000.5
MJD_JD2000 = 51544.5

def hours_to_degrees(angle):
    '''
    converts decimal hours to degrees

    Parameters
    ----------
    hours | float: angle in decimal hours

    Returns
    -------
    float: angle in degrees

    >>> hours_to_degrees(5.1)
    76.5
    '''
    return angle * 15.

def hours_to_radians(angle):
    '''
    converts decimal hours to radians

    Parameters
    ----------
    hours | float: angle in decimal hours

    Returns
    -------
    float: angle in radians

    >>> hours_to_radians(5.1)
    1.3351768777756621
    '''
    return np.radians(hours_to_degrees(angle))

def degrees_to_hours(angle):
    '''
    converts degrees to decimal hours

    Parameters
    ----------
    angle | float: angle in degrees

    Returns
    -------
    float: angle in decimal hours

    >>> degrees_to_hours(12)
    0.8
    '''
    return angle / 15.

def radians_to_hours(angle):
    '''
    converts degrees to decimal hours

    Parameters
    ----------
    angle | float: angle in degrees

    Returns
    -------
    float: angle in decimal hours

    >>> radians_to_hours(12)
    45.836623610465857
    '''
    return degrees_to_hours(np.degrees(angle))

def decimal_to_sexagesimal(decimal):
    '''
    convert decimal hours or degrees to sexagesimal

    Parameters
    ----------
    decimal | float: decimal number to be converted to sexagismal

    Returns
    -------
    tuple:
        int: hours
        int: minutes
        float: seconds
    OR
    tuple:
        int: degrees
        int: arcminutes
        float: arcseconds

    >>> decimal_to_sexagesimal(10.1)
    (10, 5, 59.999999999998721)
    '''
    fractional, integral = np.modf(decimal)
    min_fractional, minutes = np.modf(fractional * 60)
    seconds = min_fractional * 60.

    return integral.astype(int), minutes.astype(int), seconds

def sexagesimal_to_decimal(hd, minutes, seconds):
    '''
    convert sexagesimal hours or degrees to decimal
    Warning! Ensure each part has the correct sign
    e.g. -111d36m12s should be entered as (-111, -36, -12)

    Parameters
    ----------
    hd | float: hours or degrees.
    minutes | float: minutes or arcminutes
    seconds | float: seconds or arcseconds

    Returns
    -------
    float: decimal hours or degrees

    >>> sexagesimal_to_decimal(10, 5, 59.999999999998721)
    10.1
    '''
    return hd + minutes / 60. + seconds / 3600.

def ipart(num):
    '''
    gets integer part of number as float

    Parameters
    ----------
    num | float: number

    Returns
    -------
    float: number as a float rounded to 0 decimal places

    >>> ipart(15.63423)
    15.0
    '''
    return float(int(num))

def gcal_to_jd(year, month, day, hour=None, minute=None, second=None):
    '''
    converts gregorian date into julian date

    Parameters
    ----------
    year | int: gregorian year
    month | int: gregorian month
    day | int: gregorian day
    hour | Optional[int]: gregorian hour
    minute | Optional[int]: gregorian minute
    second | Optional[float]: gregorian second

    Returns
    -------
    tuple:
        float: modified jd,
        float(5): julian date

    >>> gcal_to_jd(1993, 10, 25, 2, 0, 5)
    2449285.58339
    '''
    year = int(year)
    month = int(month)
    day = int(day)

    a = ipart((month - 14) / 12.0)
    jd = ipart((1461 * (year + 4800 + a)) / 4.0)
    jd += ipart((367 * (month - 2 - 12 * a)) / 12.0)
    x = ipart((year + 4900 + a) / 100.0)
    jd -= ipart((3 * x) / 4.0)
    jd += day - 2432075.5  # was 32075; add 2400000.5

    jd -= 0.5  # 0 hours; above JD is for midday, switch to midnight.
    #add to jd for hms 
    if hour:
        jd += hour / (24.0)
    if minute:
        jd += minute / (24.0 * 60)
    if second:
        jd += second / (24.0 * 60 * 60)

    return MJD_0 + round(jd, 5)

def jd_to_gcal(jd1, jd2):
    '''
    convert julian date into partial gregorian date

    Parameters
    ----------
    jd1 | float: modified jd
    jd2 | float: actual julian date

    Returns
    -------
    tuple: 
        int: year
        int: month
        int: day
        float: fractional value of the gregorian day

    >>> jd_to_gcal(2400000.5, 49285.08339)
    (1993, 10, 25, 0.08338999999978114)
    '''
    from math import modf

    jd1_f, jd1_i = modf(jd1)
    jd2_f, jd2_i = modf(jd2)

    jd_i = jd1_i + jd2_i

    f = jd1_f + jd2_f

    # Set JD to noon of the current date. Fractional part is the
    # fraction from midnight of the current date.
    if -0.5 < f < 0.5:
        f += 0.5
    elif f >= 0.5:
        jd_i += 1
        f -= 0.5
    elif f <= -0.5:
        jd_i -= 1
        f += 1.5

    l = jd_i + 68569
    n = ipart((4 * l) / 146097.0)
    l -= ipart(((146097 * n) + 3) / 4.0)
    i = ipart((4000 * (l + 1)) / 1461001)
    l -= ipart((1461 * i) / 4.0) - 31
    j = ipart((80 * l) / 2447.0)
    day = l - ipart((2447 * j) / 80.0)
    l = ipart(j / 11.0)
    month = j + 2 - (12 * l)
    year = 100 * (n - 49) + i + l

    return int(year), int(month), int(day), f

def time_to_decimal(time):
    '''
    converts a time/datetime object into decimal time

    Parameters
    ----------
    time | object: datetime.time or datetime.datetime object

    Returns
    -------
    float: input time
    '''
    return (time.hour + time.minute / 60. + time.second / 3600. +
            time.microsecond / 3600000000.)

def decimal_to_time(hours):
    '''
    converts decimal time to a time object

    Parameters
    ----------
    hours | float: input time

    Returns
    -------
    object: datetime.time

    >>> decimal_to_time(17.6)
    datetime.time(17, 36)
    '''
    hours, minutes, seconds = decimal_to_sexagesimal(hours)
    seconds_frac, seconds = math.modf(seconds)
    seconds = int(seconds)
    microseconds = int(seconds_frac * 1e6)

    return datetime.time(hours, minutes, seconds, microseconds)

def date_to_juliandate(year, month, day):
    '''
    convert year, month, and day to a Julian Date

    Julian Date is the number of days since noon on January 1, 4713 B.C.
    So the returned date will end in .5 because the date refers to midnight.

    Parameters
    ----------
    year | int: A Gregorian year (B.C. years are negative)
    month | int: A Gregorian month (1-12)
    day | int: A Gregorian day (1-31)

    Returns
    -------
    float(5): The Julian Date for the given year, month, and day

    >>> date_to_juliandate(1993, 10, 25)
    2449285.5
    '''
    year1 = year
    month1 = month

    if year1 < 0:
        year1 += 1
    if month in [1, 2]:
        year1 -= 1
        month1 = month + 12

    if year1 > 1582 or (year1 == 1582 and month >= 10 and day >= 15):
        A = int(year1 / 100)
        B = 2 - A + int(A / 4)
    else:
        B = 0

    if year1 < 0:
        C = int((365.25 * year1) - 0.75)
    else:
        C = int(365.25 * year1)

    D = int(30.6001 * (month1 + 1))

    return B + C + D + day + 1720994.5

def datetime_to_juliandate(dt):
    '''
    convert a datetime object in UTC to a Julian Date

    Parameters
    ----------
    dt | object: datetime object

    Returns
    -------
    float: The Julian Date for the given datetime object
    '''
    A = date_to_juliandate(dt.year, dt.month, dt.day)
    B = time_to_decimal(dt.time()) / 24.

    return A + B

def juliandate_to_modifiedjd(juliandate):
    '''
    convert a Julian Date to a Modified Julian Date

    Parameters
    ----------
    juliandate | float: a Julian Date
    
    Returns
    -------
    float: the Modified Julian Date

    >>> juliandate_to_modifiedjd(2449285.5)
    49285.0
    '''
    return juliandate - 2400000.5

def modifiedjd_to_juliandate(modifiedjd):
    '''
    convert a Modified Julian Date to Julian Date

    Parameters
    ----------
    modifiedjf | float: a Modified Julian Date

    Returns
    -------
    float: Julian Date

    >>> modifiedjd_to_juliandate(49285.0)
    2449285.5
    '''
    return modifiedjd + 2400000.5

def datetime_to_modifiedjd(dt):
    '''
    convert a datetime object in UTC to a Modified Julian Date

    Parameters
    ----------
    dt | object: datetime object

    Returns
    -------
    float: the Modified Julian Date
    '''
    jd = datetime_to_juliandate(dt)

    return juliandate_to_modifiedjd(jd)

def juliandate_to_gmst(juliandate):
    '''
    convert a Julian Date to Greenwich Mean Sidereal Time

    Parameters
    ----------
    juliandate | float: Julian Date

    Returns
    -------
    float: decimal hours in GMST

    >>> juliandate_to_gmst(2455903.0)
    17.060789746482214
    '''
    jd0 = int(juliandate - .5) + .5  # Julian Date of previous midnight
    h = (juliandate - jd0) * 24.  # Hours since mightnight
    # Days since J2000 (Julian Date 2451545.)
    d0 = jd0 - 2451545.
    d = juliandate - 2451545.
    t = d / 36525.  # Centuries since J2000

    gmst = (6.697374558 + 0.06570982441908 * d0 + 1.00273790935 * h +
            0.000026 * t * t)

    return gmst % 24.

def utc_to_gmst(dt):
    '''
    convert a datetime object in UTC time to Greenwich Mean Sidereal Time

    Parameters
    ----------
    dt | object: datetime object in UTC time

    Returns
    -------
    float: decimal hours in GMST

    >>> utc_to_gmst(datetime.datetime(2011, 12, 7, 12, 0))
    17.060789746482214
    '''
    jd = datetime_to_juliandate(dt)

    return juliandate_to_gmst(jd)

def gmst_to_utc(dt):
    '''
    convert datetime object in Greenwich Mean Sidereal Time to UTC

    Note: this requires a datetime object, not just the decimal hours.

    Parameters
    ----------
    dt | object: datetime object in GMST time

    Returns
    -------
    datetime object: datetime object in UTC
    '''
    jd = date_to_juliandate(dt.year, dt.month, dt.day)

    d = jd - 2451545.
    t = d / 36525.
    t0 = 6.697374558 + (2400.051336 * t) + (0.000025862 * t * t)
    t0 %= 24

    GST = (time_to_decimal(dt.time()) - t0) % 24
    UT = GST * 0.9972695663

    time = decimal_to_time(UT)

    return dt.replace(hour=time.hour, minute=time.minute, second=time.seconds,
                      microsecond=time.microsecond)

def juliandate_to_utc(juliandate):
    '''
    convert Julian Date to datetime object in UTC

    Parameters
    ----------
    juliandate | float: a Julian Date

    Returns
    -------
    object: datetime object in UTC time

    >>> juliandate_to_utc(2455903.0)
    datetime.datetime(2011, 12, 7, 12, 0)
    '''
    juliandate += .5
    jd_frac, jd_int = math.modf(juliandate)

    if jd_int > 2299160:
        A = int((jd_int - 1867216.25) / 36524.25)
        B = jd_int + 1 + A - int(A / 4)
    else:
        B = jd_int

    C = B + 1524
    D = int((C - 122.1) / 365.25)
    E = int(365.25 * D)
    G = int((C - E) / 30.6001)

    day = C - E + jd_frac - int(30.6001 * G)

    if G < 13.5:
        month = G - 1
    else:
        month = G - 13
    month = int(month)

    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715
    year = int(year)

    day_frac, day = math.modf(day)

    day = int(day)
    date = datetime.date(year, month, day)
    hours = day_frac * 24  # fractional part of day * 24 hours

    time = decimal_to_time(hours)

    return datetime.datetime.combine(date, time)

def modifiedjd_to_utc(modifiedjd):
    '''
    convert a Modified Julian Date to datetime object in UTC

    Parameters
    ----------
    juliandate | float: a Modified Julian Date

    Returns
    -------
    object: datetime object in UTC time

    >>> modifiedjd_to_utc(49285.0)
    datetime.datetime(1993, 10, 25, 0, 0)
    '''
    juliandate = modifiedjd_to_juliandate(modifiedjd)

    return juliandate_to_utc(juliandate)

def gmst_to_lst(hours, longitude):
    '''
    convert Greenwich Mean Sidereal Time to Local Sidereal Time

    Parameters
    ----------
    hours | float: decimal hours in GMST
    longitude | float: location in degrees, E positive

    Returns
    -------
    float: decimal hours in LST

    >>> gmst_to_lst(14, 20)
    15.333333333333334
    '''
    longitude_time = degrees_to_hours(longitude)
    lst = hours + longitude_time
    lst %= 24

    return lst

def lst_to_gmst(hours, longitude):
    '''
    convert Local Sidereal Time to Greenwich Mean Sidereal Time

    Parameters
    ----------
    hours | float: decimal hours in LST
    longitude | float: location in degrees, E positive

    Returns
    -------
    float: decimal hours in GMST

    >>> lst_to_gmst(15, 60)
    11.0
    '''
    longitude_time = degrees_to_hours(longitude)
    gmst = hours - longitude_time
    gmst %= 24

    return gmst

def utc_to_lst(dt, longitude):
    '''
    convert UTC to Local Sidereal Time

    Parameters
    ----------
    dt | object: datetime object in UTC
    longitude | float: location in degrees, E positive

    Returns
    -------
    float: decimal hours in LST
    '''
    gmst = utc_to_gmst(dt)

    return gmst_to_lst(gmst, longitude)

def gps_to_utc(timestamp):
    '''
    convert GPS time to UTC

    Parameters
    ----------
    timestamp | float: GPS timestamp in seconds

    Returns
    -------
    float: UTC timestamp in seconds
    '''
    offset = next((seconds for date, seconds in LEAP_SECONDS
                   if timestamp >= utc_from_string(date)), 0)

    return timestamp - offset

def utc_to_gps(timestamp):
    '''
    convert UTC to GPS time

    Parameters
    ----------
    timestamp | float: UTC timestamp in seconds

    Returns
    -------
    float: GPS timestamp in seconds
    '''
    offset = next((seconds for date, seconds in LEAP_SECONDS
                   if timestamp >= utc_from_string(date)), 0)

    return timestamp + offset

def utc_from_string(date):
    '''
    convert a date string to UTC

    Parameters
    ----------
    date | str: date string

    Returns
    -------
    float: UTC timestamp in seconds
    '''
    t = strptime(date, '%B %d, %Y')

    return calendar.timegm(t)

def gps_from_string(date):
    '''
    convert a date string to GPS time

    Parameters
    ----------
    date | str: date string

    Returns
    -------
    float: GPS timestamp in seconds
    '''
    t = strptime(date, '%B %d, %Y')

    return utc_to_gps(calendar.timegm(t))

def gps_to_lst(timestamp, longitude):
    '''
    convert a GPS timestamp to lst

    Parameters
    ----------
    timestamp | float: GPS timestamp in seconds
    longitude | float: location in degrees, E positive

    Returns
    -------
    float: decimal hours in LST
    '''
    utc_timestamp = gps_to_utc(timestamp)
    utc = datetime.datetime.utcfromtimestamp(utc_timestamp)

    return utc_to_lst(utc, longitude)

def gps_to_datetime(timestamp):
    '''
    convert a GPS timestamp to datetime object

    Parameters
    ----------
    timestamp | float: GPS timestamp in seconds.

    Returns
    -------
    object: datetime object
    '''
    gps_dt = datetime.datetime.utcfromtimestamp(timestamp)

    return gps_dt

def datetime_to_gps(dt):
    '''
    convert a GPS datetime object to a timestamp

    Parameters
    ----------
    dt | object: GPS datetime object

    Returns
    -------
    float: GPS timestamp in seconds
    '''
    timestamp = calendar.timegm(dt.timetuple())

    return timestamp

if __name__ == '__main__':
    print('This is a module!')
