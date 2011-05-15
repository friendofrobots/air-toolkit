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
	
	$('.add-seed').click(function() {
		add_button = this;
		$.post('/category/add/'+$(add_button).next('.seed-id').text(),function(data) {
			if (!data['error']) {
			    new_seed = '<li><h3>'+data['name']+' <span class="delete-seed">[x]</span><span class="seed-id">'+data['id']+'</span></h3></li>';
			    $('#seeds').append(new_seed);
			    $(add_button).removeClass('add-seed').addClass('delete-seed').text('[-]');
			}
		    })
		    });
	$('.delete-seed').click(function() {
		add_button = this;
		$.post('/category/delete/'+$(add_button).next('.seed-id').text(),function(data) {
			if (!data['error']) {
			    if ($(add_button).parent().is('h3')) {
				$(add_button).parent().parent().remove();
				// need to find some way to remove it if it's in the likes too
			    } else {
				$('#seeds').append(new_seed);
				$(add_button).removeClass('delete-seed').addClass('add-seed').text('[+]');
			    }
			}
		    })
		    });
    });