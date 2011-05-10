$(document).ready(function() {
	$('.filter').offset($(this).parent().offset());
	$(".tab").click(function() {
		var cat_id = $(this).attr('id');
		$('.tab').css('background-color','#fff');
		$(this).css('background-color','#ccc'); // change to a darker color
		$(".filter").hide();
		for (var key in mapping) {
		    if (mapping[key] == cat_id) {
			$("#"+key).find('.filter').show();
		    }
		}
	    });
});
