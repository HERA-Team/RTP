$(function() {
    window.fileTableRequest = null;
    window.obsTableRequest = null;
    window.fileHistRequest = null;
    window.progHistRequest = null;

    $('#obs_table').html('<img src="/static/images/ajax-loader.gif" class="loading"/>');
    $('#file_table').html('<img src="/static/images/ajax-loader.gif" class="loading"/>');
    $('#file_hist').html('<img src="/static/images/ajax-loader.gif" class="loading"/>');
    $('#prog_hist').html('<img src="/static/images/ajax-loader.gif" class="loading"/>');

    launchHists();
    launchTables();
});

function abortRequestIfPending(request) {
    if (request) {
        request.abort();
        return null;
    }
    return request;
};

function launchHists() {
    window.fileHistRequest = abortRequestIfPending(window.fileHistRequest);
    window.progHistRequest = abortRequestIfPending(window.progHistRequest);

    window.fileHistRequest = $.ajax({
        type: 'POST',
        url: '/file_hist',
        success: function(data) {
            $('#file_hist').html(data);
        },
        dataType: 'html'
    });

    window.progHistRequest = $.ajax({
        type: 'POST',
        url: '/prog_hist',
        success: function(data) {
            $('#prog_hist').html(data);
        },
        dataType: 'html'
    });
};

function launchTables() {
    window.fileTableRequest = abortRequestIfPending(window.fileTableRequest);
    window.obsTableRequest = abortRequestIfPending(window.obsTableRequest);

    window.fileTableRequest = $.ajax({
        type: 'POST',
        url: '/file_table',
        success: function(data) {
            $('#file_table').html(data);
        },
        dataType: 'html'
    });

    window.obsTableRequest = $.ajax({
        type: 'POST',
        url: '/obs_table',
        success: function(data) {
            $('#obs_table').html(data);
        },
        dataType: 'html'
    });
};
