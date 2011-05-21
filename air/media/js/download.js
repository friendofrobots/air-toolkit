function update(data){
    $('#start').hide();
    $('#downloading').show();
    $('#stage'+data['stage']).show();
    if (data['stage'] < 3) {
        $('#count'+data['stage']).text(data['completed']);
        $('#total'+data['stage']).text(data['total']);
    }
}
function getStatus() {
    $.get('/t/download/status/', function(data) {
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
            if (data['stage'] == 3) {
		if (redirect) {
		    setTimeout(function() {
			window.location = "http://air.xvm.mit.edu/";
		    },1000);
		} else {
		    $('#getstarted').show();
		}
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
        $.post('/t/download/start/',function(data) {
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
