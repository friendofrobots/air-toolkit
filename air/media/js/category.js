$(document).ready(function() {
    $('.filled-bar').css('width',function() {
	return (parseFloat($(this).parent().next().text())*100.0)+'px';
    });
});
