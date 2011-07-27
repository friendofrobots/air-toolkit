function getresults(query) {
    if (last_value == query) {
	return;
    } else if (!query) {
	$('#results').empty();
	$('#toppages').show();
	return;
    }
    $("#thinking-cover").show();
    $.get('/context/pages/lookup/', {'query':query,'page_num':1}, function(data) {
        if (data['error']) {
            $('#error').text(data['error']).show();
	    $("#thinking-cover").hide();
        } else if (data['results']) {
	    $('#results').empty();
	    for ( var i in data['results'] ) {
		likedbys = []
		for ( var l in data['results'][i][4] ) {
		    likedbys.push('<li class="liked-by-person">'+data['results'][i][4][l]+'</li>');
		}
		page = '<li class="page"><span class="page-id">'+data['results'][i][0]+'</span>'+
		    '<div class="page-img fakelink"><img src="https://graph.facebook.com/'+
		    data['results'][i][2]+'/picture?type=normal" /></div><div class="page-title fakelink">'+
		    data['results'][i][1]+'</div>'+'<div class="page-category">'+data['results'][i][3]+
		    '</div><ul class="liked-by">'+'Liked by: '+likedbys.join(', ')+
		    '</ul><input class="page-select" type="radio" '+'value="'+data['results'][i][0]+
		    '" name="seed"></input></li>';
		$('#results').append(page);
	    }
	    $('#toppages').hide();
	    $('#results .page-img, #results .page-title').click(function() {
		$(this).parent().find('.page-select').prop('checked',true);
		$('#page-form').submit();
	    });	
	    $("#thinking-cover").hide();
	}
    });
    last_value = query;
}

var last_timeout = false;
var last_value = "";
var page_num = 1;

$(document).ready(function() {
    $('#searchbox').keyup(function(event) {
	clearTimeout(last_timeout);
	last_timeout = false;
	if (event.which == '13') { // ENTER
	    getresults($('#searchbox').val());
	} else if (event.which == '27') { // ESCAPE
	    return;
	} else {
	    last_timeout = setTimeout(function() {
		getresults($('#searchbox').val());
	    },1000);
	}
    });
    $('#toppages .page-img, #toppages .page-title').click(function() {
	$(this).parent().find('.page-select').prop('checked',true);
	$('#page-form').submit();
    });
});
