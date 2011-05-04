$(document).ready(function() {
	$('.show').toggle(function() {
		$(this).prev().show('slow');
		$(this).text('[-]');
	    },function() {
		$(this).prev().hide('slow');
		$(this).text('[+]');
	    });
    });