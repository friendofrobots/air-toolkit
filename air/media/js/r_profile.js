$(document).ready(function() {
    $(".tab").click(function() {
	var cat_id = $(this).attr('id');
	$('.active').removeClass('active');
	$(this).addClass('active');
	$(".filter").show();
	for (var i in mapping[cat_id]) {
	    $("#"+mapping[cat_id][i]).find('.filter').hide();
	}
    });
});
