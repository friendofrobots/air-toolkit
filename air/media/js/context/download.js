var interval_id = 0;

function update(data){
    $('#downloading').show();
    if (data['stage'] == 0) {
	clearInterval(interval_id);
    }
    if (data['stage'] > 0) {
	$('#stage1').show();
	$('#prepare1').hide();
	$('#working1').css('display','inline-block');
	if (data['stage'] == 1) {
	    w = (1.*data['completed'])/(1.*data['total'])*$('#status'+data['stage']).parent().width();
            $('#status1').width(w);
            $('#count1').text(data['completed']);
            $('#total1').text('/'+data['total']);
	    if (data['completed'] == data['total']) {
		$('#stage2').show();
		$('#prepare2').css('display','inline-block');
	    }
	} else {
	    $('#status1').width('100%');
            $('#count1').text('done');
            $('#total1').hide();
	}
    }
    if (data['stage'] > 1) {
	$('#stage2').show();
	$('#prepare2').hide();
	$('#working2').css('display','inline-block');
	if (data['stage'] == 2) {
	    w = (1.*data['completed'])/(1.*data['total'])*$('#status'+data['stage']).parent().width();
            $('#status2').width(w);
            $('#count2').text(data['completed']);
            $('#total2').text('/'+data['total']);
	} else {
            $('#status2').width('100%');
            $('#count2').text('done');
            $('#total2').hide();
	}
    }
    if (data['stage'] == 3) {
	$('#download-finished').show('fast');
	clearInterval(interval_id);
	setTimeout(function() {
	    $('#downloading').hide('fast');
	    $('#friends-button').show('fast');
	    $('#pages-button').show('fast');
	},1000);
    }
}
function getStatus() {
    $.get('/t/download/status/', function(data) {
	if (data['stage']) {
            update(data);
        }
        if (data['error']) {
            $('#error').text(data['error']).show();
            if (!data['stage']) {
                $('#starting').hide();
                $('#downloading').show();
            }
	}
    });
}

$(document).ready(function() {
    if (started) {
        getStatus();
        interval_id = setInterval(getStatus,3000);
    }
    $('#show-perms').click(function() {
	$(this).hide();
	$('#perms').show();
    });
    $('#start').click(function() {
	$(this).hide();
	$('#perms').hide();
	$('#show-perms').show();
	$('#stage1').show();
	$('#prepare1').css('display','inline-block');
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
            interval_id = setInterval(getStatus,3000);
        });
    });
});
