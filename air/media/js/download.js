$(document).ready(function() {
    if (started) {
        $.get('/d/status/', function(data) {
            
        });
    }
    $('#start').click(function() {
        $.post('/d/start/',function(data) {
            if (data['error']) {
                if (data['stage']) {
                    start(data)
                } else {
                    $('#starting').text(data['error']).show();
                }
            } else {
                start(data);
            }
        });
    });
});


function start(data) {
    $('#start').hide();
    $('#starting').show();
    $('#stage'+data['stage']).show();
    if (data['stage'] == 1) {
        $('#completed').data['completed'];
        $('#total').data['total'];
    }
}