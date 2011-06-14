$(document).ready(function() {
    $('.filled-bar').css('width',function() {
	console.log(this);
	return (parseFloat($(this).parent().next().text())*100.0)+'px';
    });
});
