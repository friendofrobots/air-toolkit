$(document).ready(function() {
	$("#changeName").click(function() {
		$.post('/reflect/rename/',{'name':$('#rename').val(),
			    'category_id':$('#category_id').val()},function(data) {
			if (data['name']) {
			    $('#rightContent h2').text(data['name']);
			}
		    },function(data) {
			var errored = true;
		    });
	    });
});
