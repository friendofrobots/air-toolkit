$(document).ready(function() {
    $('#notify-top').click(function() {
	$('#notifications').slideToggle('fast');
    });
    setInterval(function() {
	$.get('/t/category/notifications/',function(data) {
	    if (data['success']) {
		for (var i in data['unread']) {
		    if (!$('#notify-'+data['unread'][i][0]).hasClass('unread')) {
			$('#notify-'+data['unread'][i][0]).addClass('unread');
		    }
		}
		$('#unread-count').text(data['unread'].length);
		if (data['unread'].length>0) {
		    $('#unread-count').addClass("unread-red");
		}
	    }
	});
    },10000);
});
