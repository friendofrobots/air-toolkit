$(document).ready(function() {
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
