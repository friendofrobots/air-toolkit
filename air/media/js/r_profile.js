$(document).ready(function() {
    $('.category').height(function(index) {
	var h = Math.ceil($('.category_likes').eq(index).children().length/4)*146+45;
	return h;
    });
    $(".tab").click(function() {
	var cat_id = $(this).attr('id');
	$('.active').removeClass('active');
	$(this).addClass('active');
	$(".filter").show();
	for (var key in mapping) {
	    if (mapping[key] == cat_id) {
		$("#"+key).find('.filter').hide();
	    }
	}
    });
});