var interval_id = 0;

function add_seed(event) {
    add_button = event.currentTarget;
    $.post('/t/category/add/'+$(add_button).next('.seed-id').text(),function(data) {
	if (!data['error']) {
	    new_seed = '<li id="seed-'+data['id']+'"><h3>'+data['name']+'<span class="delete-seed"> [x]</span><span class="seed-id">'+data['id']+'</span></h3></li>';
	    $('#seeds').append(new_seed);
	    $('#seed-'+data['id']+' .delete-seed').click(delete_seed);
	    $(add_button).removeClass('add-seed').addClass('delete-seed').text('[x]');
	    $(add_button).unbind().click(delete_seed);
	    $('#start-creation').attr('disabled','');
	}
    });
}

function delete_seed(event) { 
    delete_button = event.currentTarget;
    $.post('/t/category/delete/'+$(delete_button).next('.seed-id').text(),function(data) {
	if (!data['error']) {
	    if ($(delete_button).parent().is('h3')) {
		$(delete_button).parent().parent().remove();
		$('#like-'+data['id']+' .delete-seed').removeClass('delete-seed').addClass('add-seed').text('[+]');
		$('#like-'+data['id']+' .add-seed').unbind().click(add_seed);
	    } else {
		$('#seed-'+data['id']).remove();
		$(delete_button).removeClass('delete-seed').addClass('add-seed').text('[+]');
		$(delete_button).unbind().click(add_seed);
	    }
	}
    });
}

function start_creation() {
    $('#start-creation').attr('disabled','disabled');
    $.post('/t/category/start/', $('#creation-form').serialize(), function(data) {
        if (data['error']) {
            if (data['status']) {
                update_creation(data);
            } else {
                $('#creation-error').text(data['error']);
		$('#creation-error').show();
                $('#creation-status').show();
            }
        } else {
            update_creation(data);
        }
        interval_id = setInterval(creation_status,3000);
    });
    return false;
}

function update_creation(data) {
    $("#start-creation").hide();
    $("#creation-status").show()
    if (data['status'] != "completed") {
	rounds = '';
	for (var i in data['status']) {
	    r = parseInt(i)+1;
	    rounds += "<p>Round "+r+": "+data['status'][i]+" object firing</p>";
	}
	$('#creation-rounds').html(rounds);
    } else {
	$('#creation-done').show()
	clearInterval(interval_id);
    }
}

function creation_status() {
    $.get('/t/category/status/'+$('#id_category_id').attr('value'), function(data) {
        if (data['error']) {
            if (data['status']) {
                update_creation(data);
            } else {
                $('#creation-error').text(data['error']).show();
                $('#creation-status').show();
            }
        } else {
            update_creation(data);
        }
    });

}

function show_pmi_func(pmi_fieldset) {
    return function() {
	pmi_fieldset.find('.pmi-box').show('slow');
	pmi_fieldset.find('legend').unbind().click(hide_pmi_func(pmi_fieldset));
    }
}
function hide_pmi_func(pmi_fieldset) {
    return function() {
	pmi_fieldset.find('.pmi-box').hide('slow');
	pmi_fieldset.find('legend').unbind().click(show_pmi_func(pmi_fieldset));
    }
}

$(document).ready(function() {
    $('.pmi-fieldset legend').one('click',function() {
	legend = this;
	$.getJSON('/t/pmis/'+$(legend).parent().find('.pmi-id').text(),function(data) {
	    var lis = [];
	    for (var index in data['pmis']) {
		lis.push('<li>'+data['pmis'][index][0]+' : '+data['pmis'][index][1]+'</li>');
	    }
	    $(legend).next().find('ul').html(lis.join('\n'));
	    show_pmi_func($(legend).parent())();
	});
    });
    $('.hide').click(function() {
	hide_pmi_func($(this).parent().parent())();
    });

    $('.add-seed').click(add_seed);
    $('.delete-seed').click(delete_seed);
    $('#creation-form').submit(start_creation);
    if (started) {
        interval_id = setInterval(creation_status,3000);
    }
    $('#toggle-creation-options legend').toggle(function() {
	$('#toggle-creation-options legend').text('Hide Options');
	$('#toggle-creation-options ul').slideToggle('fast');
    }, function() {
	$('#toggle-creation-options legend').text('Show Options');
	$('#toggle-creation-options ul').slideToggle('fast');
    });
});
