function update(data){
    $('#start').hide();
    $('#downloading').show();
    $('#stage'+data['stage']).show();
    if (data['stage'] == 1) {
        $('#count').text(data['completed']);
        $('#total').text(data['total']);
    }
}
function getStatus() {
    $.get('/download/status/', function(data) {
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
                if (data['stage'] == 4) {
                    setTimeout(function() {
                            window.location = "http://air.xvm.mit.edu:8000/";
                        },1000);
                }
            }
        });
}

$(document).ready(function() {
        if (started) {
            getStatus();
            setInterval(getStatus,5000);
        }
        $('#start').click(function() {
                $.post('/download/start/',function(data) {
                        if (data['error']) {
                            if (data['stage']) {
                                update(data);
                            } else {
                                $('#error').text(data['error']).show();
                                $('#starting').hide();
                                $('#downloading').show();
                            }
                        } else {
                            update(data);
                        }
                        setInterval(getStatus,5000);
                });
        });
});
