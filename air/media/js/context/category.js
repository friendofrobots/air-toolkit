var interval_id = 0;

function start_creation() {
    $("#processing-start").hide();
    $.post('/t/category/'+category_id+'/start/', {
	'startvalue':.3,
	'threshold':.2,
	'decayrate':.25,
    }, function(data) {
        if (data['error']) {
	    $('#error').text(data['error']).show();
        } else {
            update_creation(data);
            interval_id = setInterval(creation_status,5000);
        }
    });
    return false;
}

function update_creation(data) {
    $("#processing-status").show()
    if (data['status'] != "completed") {
	rounds = '';
	for (var i in data['status']) {
	    r = parseInt(i)+1;
	    rounds += "<p>Round "+r+": "+data['status'][i]+" object firing</p>";
	}
	$('#processing-details').html(rounds);
    } else {
	window.location.reload('true');
    }
}

function creation_status() {
    $.get('/t/category/status/'+category_id, function(data) {
        if (data['error']) {
            $('#creation-error').text(data['error']).show();
	    clearInterval(interval_id);
        } else {
            update_creation(data);
        }
    });
}

$(document).ready(function() {
    $('#category-people-more').click(function() {
	$('#category-people-hidden').slideToggle('fast');
    });
    $('#processing-start').click(start_creation);
    $('#edit-title').click(function() {
	$('#category-title').hide();
	$('#edit-textbox').show();
    });
    $('#edit-textbox').keyup(function(event) {
	if (event.which == '13') { // ENTER
	    $.post('/t/category/rename/', {
		'name':$('#edit-textbox').val(),
		'category_id':category_id,
	    }, function(data) {
		if (data['name']) {
		    $('#category-name').text(data['name']);
		    $('#edit-textbox').val(data['name']);
		    $('#notify-'+category_id+' a').text(data['name']);
		    $('#edit-textbox').hide();
		    $('#category-title').show();
		}
	    });
	} else if (event.which == '27') { // ESCAPE
	    $('#edit-textbox').hide();
	    $('#category-title').show();
	}
    });
    if (started) {
	creation_status();
        interval_id = setInterval(creation_status,5000);
    }
    $.post('/t/category/'+category_id+'/read/',function() {
	$('#notify-'+category_id).removeClass('unread');
	new_unr = parseInt($('#unread-count').text()) - 1;
	if (new_unr < 1) {
	    $('#unread-count').removeClass('unread-red');
	    $('#unread-count').text('0');
	} else {
	    $('#unread-count').text(new_unr);
	}
    });
});
