function getStatus() {
    $.get('/t/category/status/', function(data) {
        if (data['error']) {
            if (data['stage']) {
                update(data);
            } else {
                $('#error').text(data['error']).show();
                $('#starting').hide();
                $('#downloading').show();
            }
        } else if (data['stage']) {
            update(data);
            if (data['stage'] == 2) {
                setTimeout(function() {
                    window.location = "http://air.xvm.mit.edu/category/"+data['id'];
                },1000);
            }
        }
    });
}

$(document).ready(function() {
    //if (started) {
    //  getStatus();
    //    setInterval(getStatus,5000);
    //}
});
