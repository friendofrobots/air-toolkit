$(document).ready(function() {
    $("#changeName").click(function() {
	$.post('/t/category/rename/', {
	    'name':$('#rename').val(),
	    'category_id':$('#category_id').val()
	}, function(data) {
	    if (data['name']) {
		$('#cat-title').text(data['name']);
		$('#cat-'+data['id']).text(data['name']);
	    }
	});
    });
});
