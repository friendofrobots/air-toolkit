function get_filtered() {
    filter_data = {};
    if (filters) {
	filter_data['filters'] = filters;
    }
    if (likes) {
	filter_data['likes'] = likes;
    }
    $.get('/context/friends/filtered', filter_data, function(data) {
        if (data['error']) {
            $('#error').text(data['error']).show();
	    $("#thinking-cover").hide();
        } else if (data['people']) {
	    $('#friends').empty();
	    for ( var i in data['people'] ) {
		friend = '<li class="friend object"><span class="friend-id">'+
		    data['people'][i][0]+'</span><div class="image-holder">'+
		    '<img src="https://graph.facebook.com/'+data['people'][i][2]+'/picture?type=normal" />'+
		    '</div><div class="title-holder">'+data['people'][i][1]+'</div>'+
		    '<input class="friend-select" type="checkbox" value="'+data['people'][i][0]+
		    '" name="people"></input></li>';
		$('#friends').append(friend);
	    }

	    for ( var relation in data['filters'] ) {
		$('#rel-'+relation+' ul').empty()
		for ( var i in data['filters'][relation] ) {
		    filter = '<li class="filter property">'+
			'<span class="property-id">'+data['filters'][relation][i][0]+'</span>'+
			'<span class="fakelink"><span class="filter-name">'+
			data['filters'][relation][i][1]+'</span> <span class="filter-activity">'+
			'('+data['filters'][relation][i][2]+')</span></span></li>';
		    f = $('#rel-'+relation+' ul').append(filter);
		    if (filters.indexOf(''+data['filters'][relation][i][0]) >-1) {
			f.children(':last-child').addClass('active');
		    }
		}
		$('#rel-'+relation+' ul:parent').show()
	    }
	    $('#toplikes ul').empty()
	    for ( var i in data['likes'] ) {
		like = '<li class="filter like">'+
		    '<span class="like-id">'+data['likes'][i][0]+'</span>'+
		    '<span class="fakelink"><span class="filter-name">'+
		    data['likes'][i][1]+'</span> <span class="filter-activity">'+
		    '('+data['likes'][i][2]+')</span></span></li>';
		l = $('#toplikes ul').append(like);
		if (likes.indexOf(''+data['likes'][i][0]) >-1) {
		    l.children(':last-child').addClass('active');
		}
	    }
	    $("#thinking-cover").hide();

	    category_name = $('.active').map(function() {
		return $(this).parent().parent().find('h3').text()+'-'+$(this).find('.filter-name').text();
	    }).get().join(', ');
	    $('#group-name').val(category_name);

	    set_handlers();
	    $('.friend-select').prop('checked',true).change();
	    show_hide_submit();
        } else {
            $('#error').text('something terrible has happened').show();
	}
    });
}

function filter_handler(event) {
    if (!$(this).hasClass('active')) {
	if ($(this).hasClass('property')) {
	    var property_id = $(this).find('.property-id').text();
	    filters.push(property_id);
	} else {
	    var like_id = $(this).find('.like-id').text();
	    likes.push(like_id);
	}
	    $(this).addClass('active');
    } else {
	if ($(this).hasClass('property')) {
	    var property_id = $(this).find('.property-id').text();
	    var idx = filters.indexOf(property_id);
	    if (idx != -1) {
		filters.splice(idx, 1);
	    }
	} else {
	    var like_id = $(this).find('.like-id').text();
	    var idx = likes.indexOf(like_id);
	    if (idx != -1) {
		likes.splice(idx, 1);
	    }
	}
	$(this).removeClass('active');
    }
    $("#thinking-cover").show();
    get_filtered();
}

function selected_handler(event) {
    $friend = $(this).find('.friend-select');
    if (!$friend.prop('checked')) {
	$friend.prop('checked',true).change();
    } else {
	$friend.prop('checked',false).change();
    }
    show_hide_submit();
}

function set_handlers() {
    $('.filter').click(filter_handler);
    $('.friend-select').change(function(event) {
	if ($(this).prop('checked')) {
	    $(this).parent().addClass('selected');
	} else {
	    $(this).parent().removeClass('selected');
	}
    });
    $('.friend').click(selected_handler);
}

function show_hide_submit() {
    if ($('.friend-select:checked').length==0) {
	$('#group-submit').fadeOut();
    } else {
	$('#group-submit').fadeIn();
    }
}

var filters = []
var likes = []

$(document).ready(function() {
    set_handlers();
    $('#select-all').click(function(event) {
	$('.friend-select').prop('checked',true).change();
	show_hide_submit();
    });
    $('#select-none').click(function(event) {
	$('.friend-select').prop('checked',false).change();
	show_hide_submit();
    });
    $('.friend-select').prop('checked',true).change();
});
