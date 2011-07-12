$(document).ready(function() {
    $(".filter").show();
    for (var i in cat_likes) {
	$("#"+cat_likes[i]).find('.filter').hide();
    }
});
