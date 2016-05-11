//http://stackoverflow.com/questions/1144783/replacing-all-occurrences-of-a-string-in-javascript
String.prototype.replaceAll = function (find, replace) {
    var str = this;
    return str.replace(new RegExp(find.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'), 'g'), replace);
};

$(function() {
    setTime();
    setButton();

    //global ajax vars
    window.dataSummaryTableRequest = null;
    window.daySummaryTableRequest = null;
    window.obsTableRequest = null;
    window.fileTableRequest = null;

    getObservations(false);
});

function getDateTimeString(now) {
    var month = ('0' + (now.getUTCMonth() + 1)).slice(-2);
    var date = ('0' + now.getUTCDate()).slice(-2);
    var hours = ('0' + now.getUTCHours()).slice(-2);
    var minutes = ('0' + now.getUTCMinutes()).slice(-2);
    return now.getUTCFullYear() + '/' + month + '/' + date + ' ' + hours + ':' + minutes;
};

function getDate(datestr) {
    var year = datestr.substring(0, 4);
    var month = datestr.substring(5, 7);
    var day = datestr.substring(8, 10);
    var hour = datestr.substring(11, 13);
    var minute = datestr.substring(14, 16);
    return new Date(Date.UTC(year, month - 1, day, hour, minute, 0));
};

function convertDateTimesToJD(startDate, endDate){
};

function convertJDtoDateTimes(jdstart, jdend){
};

function abortRequestIfPending(request) {
    if (request) {
        request.abort();
        return null;
    }
    return request;
};

function setTime() {
    var startDatePicker = $('#datepicker_start');
    var endDatePicker = $('#datepicker_end');
    startDatePicker.datetimepicker();
    endDatePicker.datetimepicker();

    if (startDatePicker.val().length > 0 && endDatePicker.val().length > 0) {
        // The date pickers have already been filled with values, which means we're viewing a set.
        // Nothing needs to be done.
    } else if (sessionStorage.startDate && sessionStorage.endDate) {
        startDatePicker.val(sessionStorage.startDate);
        endDatePicker.val(sessionStorage.endDate);
    } else {
        var now = new Date();
        var nowStr = getDateTimeString(now);

        var MS_PER_DAY = 86400000;
        var yesterday = new Date(now.getTime() - MS_PER_DAY);
        var yesterdayStr = getDateTimeString(yesterday);

        startDatePicker.val(yesterdayStr);
        endDatePicker.val(nowStr);

        sessionStorage.startDate = yesterdayStr;
        sessionStorage.endDate = nowStr;
    }

    var jd_startPicker = $('#jd_start');
    var jd_endPicker = $('#jd_end');

    if (jd_startPicker.val().length > 0 && jd_endPicker.val().length > 0) {
        // The date pickers have already been filled with values, which means we're viewing a set.
        // Nothing needs to be done.
    } else if (sessionStorage.jd_start && sessionStorage.jd_end) {
        jd_startPicker.val(sessionStorage.jd_start);
        jd_endPicker.val(sessionStorage.jd_end);
    } else {
        var jd_head = '2455903';
        var jd_tail = '2455904';
        jd_startPicker.val(jd_head);
        jd_endPicker.val(jd_tail);

        sessionStorage.jd_start = jd_head;
        sessionStorage.jd_end = jd_tail;
    }
};

function setButton(){
    var checked_val = $("input[name='date']:checked").val();
    if (checked_val === '1') {
        document.getElementsByName('dateButton')[0].disabled = true;
        document.getElementsByName('dateButton')[0].style.background = '#F4F4F4';
        document.getElementsByName('dateButton')[0].style.color = '#F4F4F4';
        document.getElementsByName('jDateButton')[0].disabled = false;
        document.getElementsByName('jDateButton')[0].style.background = '';
        document.getElementsByName('jDateButton')[0].style.color = '';
    } else {
        document.getElementsByName('dateButton')[0].disabled = false;
        document.getElementsByName('dateButton')[0].style.background = '';
        document.getElementsByName('dateButton')[0].style.color = '';
        document.getElementsByName('jDateButton')[0].disabled = true;
        document.getElementsByName('jDateButton')[0].style.background = '#F4F4F4';
        document.getElementsByName('jDateButton')[0].style.color = '#F4F4F4';
    }
};

function getDataHist(startUTC, endUTC, jd_start, jd_end, polarization, era_type, host, filetype) {
    window.dataHistRequest = abortRequestIfPending(window.HistRequest);

    window.dataHistRequest = $.ajax({
        type: 'POST',
        url: '/data_hist',
        data: {
            'starttime': startUTC,
            'endtime': endUTC,
            'jd_start': jd_start,
            'jd_end': jd_end,
            'polarization': polarization,
            'era_type': era_type,
            'host': host,
            'filetype': filetype,
        },
        success: function(data) {
            $('#data_hist').html(data);
        },
        dataType: 'html'
    });
};

function getObsTable(startUTC, endUTC, jd_start, jd_end, polarization, era_type) {
    window.obsTableRequest = abortRequestIfPending(window.obsTableRequest);

    window.obsTableRequest = $.ajax({
        type: 'POST',
        url: '/obs_table',
        data: {
            'starttime': startUTC,
            'endtime': endUTC,
            'jd_start': jd_start,
            'jd_end': jd_end,
            'polarization': polarization,
            'era_type': era_type,
        },
        success: function(data) {
            $('#obs_table').html(data);
        },
        dataType: 'html'
    });
};

function getFileTable(startUTC, endUTC, jd_start, jd_end, host, filetype, polarization, era_type) {
    window.fileTableRequest = abortRequestIfPending(window.fileTableRequest);

    window.fileTableRequest = $.ajax({
        type: 'POST',
        url: '/file_table',
        data: {
            'starttime': startUTC,
            'endtime': endUTC,
            'jd_start': jd_start,
            'jd_end': jd_end,
            'host': host,
            'filetype': filetype,
            'polarization': polarization,
            'era_type': era_type,
        },
        success: function(data) {
            $('#file_table').html(data);
        },
        dataType: 'html'
    });
};

function getDataTable(startUTC, endUTC, jd_start, jd_end) {
    window.dataSummaryTableRequest = abortRequestIfPending(window.dataSummaryTableRequest);

    window.dataSummaryTableRequest = $.ajax({
        type: 'POST',
        url: '/data_summary_table',
        data: {
            'starttime': startUTC,
            'endtime': endUTC,
            'jd_start': jd_start,
            'jd_end': jd_end,
        },
        success: function(data) {
            $('#data_summary_table').html(data);
        },
        dataType: 'html'
    });
};

function getDayTable(startUTC, endUTC, jd_start, jd_end, polarization, era_type) {
    window.daySummaryTableRequest = abortRequestIfPending(window.daySummaryTableRequest);

    window.daySummaryTableRequest = $.ajax({
        type: 'POST',
        url: '/day_summary_table',
        data: {
            'starttime': startUTC,
            'endtime': endUTC,
            'jd_start': jd_start,
            'jd_end': jd_end,
            'polarization': polarization,
            'era_type': era_type,
        },
        success: function(data) {
            $('#day_summary_table').html(data);
        },
        dataType: 'html'
    });
};

function parseDate() {
    var start = $('#datepicker_start').val();
    var end = $('#datepicker_end').val();
    re = /^\d{4}\/\d{2}\/\d{2} \d{2}:\d{2}$/;

    var jd_start = $('#jd_start').val();
    var jd_end = $('#jd_end').val();

    // Update the sessionStorage
    sessionStorage.startDate = start;
    sessionStorage.endDate = end;

    sessionStorage.jd_start = jd_start;
    sessionStorage.jd_end = jd_end;

    var startDate, endDate;

    if (start.match(re)) {
        startDate = getDate(start);
    } else {
        alert('Invalid datetime format: ' + start);
        return;
    }

    if (end.match(re)) {
        endDate = getDate(end);
    } else {
        alert('Invalid datetime format: ' + end);
        return;
    }

    // Make each date into a string of the format 'YYYY-mm-ddTHH:MM:SSZ', which is the format used in the local database.
    var startUTC = startDate.toISOString().slice(0, 19) + 'Z';
    var endUTC = endDate.toISOString().slice(0, 19) + 'Z';

    return {
        startUTC: startUTC,
        endUTC: endUTC,
        jd_start: jd_start,
        jd_end: jd_end
    };
};

function parseQuery() {
    var polarization = $('#polarization_dropdown').val();
    var era_type = $('#era_type_dropdown').val();
    var host = $('#host_dropdown').val();
    var filetype = $('#filetype_dropdown').val();

    return {
        polarization: polarization,
        era_type: era_type,
        host: host,
        filetype: filetype
    };
};

function getObservations(loadTab) {
    window.saveTableRequest = abortRequestIfPending(window.saveTableRequest);

    $('#obs_table').html('<img src="/static/images/ajax-loader.gif" class="loading"/>');
    $('#file_table').html('<img src="/static/images/ajax-loader.gif" class="loading"/>');
    $('#data_summary_table').html('<img src="/static/images/ajax-loader.gif" class="loading"/>');
    $('#day_summary_table').html('<img src="/static/images/ajax-loader.gif" class="loading"/>');

    var dateTime = parseDate();
    var jd_start = dateTime.jd_start;
    var jd_end = dateTime.jd_end;
    var startUTC = dateTime.startUTC;
    var endUTC = dateTime.endUTC;

    var query = parseQuery();
    var polarization = query.polarization;
    var era_type = query.era_type;
    var host = query.host;
    var filetype = query.filetype;

    var fullLink = '/?starttime=' + startUTC +
                   '&endtime=' + endUTC +
                   '&jd_start=' + jd_start +
                   '&jd_end=' + jd_end +
                   '&host=' + host +
                   '&filetype=' + filetype +
                   '&polarization=' + polarization +
                   '&era_type=' + era_type;

    if (loadTab) {
        window.saveTableRequest = $.ajax({
            type: 'POST',
            url: '/',
            data: {
                'starttime': startUTC,
                'endtime': endUTC,
                'jd_start': jd_start,
                'jd_end': jd_end,
                'host': host,
                'filetype': filetype,
                'polarization': polarization,
                'era_type': era_type,
            },
            success: function(data) {
                location.href = fullLink
            },
            dataType: 'html'
        });
    } else {
        getObsTable(startUTC, endUTC, jd_start, jd_end, polarization, era_type);
        getFileTable(startUTC, endUTC, jd_start, jd_end, host, filetype, polarization, era_type);
        //getDataHist(startUTC, endUTC, jd_start, jd_end, polarization, era_type, host, filetype);
        getDataTable(startUTC, endUTC, jd_start, jd_end);
        getDayTable(startUTC, endUTC, jd_start, jd_end, polarization, era_type);
    }
};
