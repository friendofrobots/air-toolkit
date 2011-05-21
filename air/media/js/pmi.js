$(document).ready(function() {
    $('.show').one('click',function() {
	show = this;
	$.getJSON('/pmis/'+$(this).next().text(),function(data) {
	    var lis = [];
	    for (var index in data['pmis']) {
		lis.push('<li>'+data['pmis'][index][0]+' : '+data['pmis'][index][1]+'</li>');
	    }
	    $(show).prev().html(lis.join('\n'));
	});
    });
    $('.show').toggle(function() {
	$(this).prev().show('slow');
	$(this).text('[-]');
    },function() {
	$(this).prev().hide('slow');
	$(this).text('[+]');
    });

    $('.add-seed').click(add_seed);
    $('.delete-seed').click(delete_seed);
    $('#toggle-creation-options legend').toggle(function() {
	$('#toggle-creation-options legend').text('Hide Options');
	$('#toggle-creation-options ul').slideToggle('fast');
    }, function() {
	$('#toggle-creation-options legend').text('Show Options');
	$('#toggle-creation-options ul').slideToggle('fast');
    });
});

function add_seed(event) {
    add_button = event.currentTarget;
    $.post('/category/add/'+$(add_button).next('.seed-id').text(),function(data) {
	if (!data['error']) {
	    new_seed = '<li id="seed-'+data['id']+'"><h3>'+data['name']+'<span class="delete-seed"> [x]</span><span class="seed-id">'+data['id']+'</span></h3></li>';
	    $('#seeds').append(new_seed);
	    $('#seed-'+data['id']+' .delete-seed').click(delete_seed);
	    $(add_button).removeClass('add-seed').addClass('delete-seed').text('[x]');
	    $(add_button).unbind().click(delete_seed);
	    $('#donebutton').attr('disabled','');
	}
    });
}

function delete_seed(event) { 
    delete_button = event.currentTarget;
    $.post('/category/delete/'+$(delete_button).next('.seed-id').text(),function(data) {
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
