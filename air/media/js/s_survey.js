var question_number = 1;

$(document).ready(function() {
    $('#survey-bar').toggle(function() {
	$(this).text('Hide Survey');
	$('#survey-questions').slideDown();
	$('#survey-spacer').css('height','205px');
    }, function() {
	$(this).text('Show Survey');
	$('#survey-questions').slideUp();
	$('#survey-spacer').css('height','20px');
    });
    $('#survey-left').click(function(event) {
	if (question_number != 1) {
	    $('#q'+question_number).removeClass('activeq');
	    question_number--;
	    $('#q'+question_number).addClass('activeq');
	    if (question_number != 7) {
		$('#survey-right').show();
	    }
	    if (question_number == 1) {
		$('#survey-left').hide();
	    }
	}
	return false;
    });
    $('#survey-right').click(function(event) {
	if (question_number != 7) {
	    $('#q'+question_number).removeClass('activeq');
	    question_number++;
	    $('#q'+question_number).addClass('activeq');
	    if (question_number != 1) {
		$('#survey-left').show();
	    }
	    if (question_number == 7) {
		$('#survey-right').hide();
	    }
	}
	return false;
    });
    $('#survey').hover(function(){
	if (question_number != 1) {
	    $('#survey-left').show();
	}
	if (question_number != 7) {
	    $('#survey-right').show();
	}
    }, function() {
	$('#survey-left').hide();
	$('#survey-right').hide();
    });


    /****** Questions ******/
    $('#q1 .question-radio').click(function() {
        $.post('/survey/post/'+category_id+'/individual', {
            'individual':$('input:radio[name=individual]:checked').val()
        }, function(data) {
            // I should probably show the data has been uploaded
        });
    });
    $('#q2 input:text').blur(function() {
        field = $(this).attr('id');
        post_data = {};
        post_data[field] = $(this).val();
        $.post('/survey/post/'+category_id+'/subgroup', post_data, function(data) {
            // I should probably show the data has been uploaded
        });
    });
    $('#q3 #unifying').blur(function() {
        $.post('/survey/post/'+category_id+'/unifying', {
            'unifying':$('#unifying').val()
        }, function(data) {
            // I should probably show the data has been uploaded
        });
    });

    $('#q4 .surprise-image').click(function() {
        surprise_image = this
        $(surprise_image).addClass('selected');
        $('.object').click(function() {
            $(surprise_image).find('img').attr('src',$(this).find('img').attr('src'));
            page_id = $.trim($(this).find('.page-id').text());
            $(surprise_image).next().val(page_id);
            post_data = {};
            post_data[$(surprise_image).next().attr('id')] = page_id;
            $(surprise_image).removeClass('selected');
            $.post('/survey/post/'+category_id+'/surprise', post_data, function(data) {
            // I should probably show the data has been uploaded
            });
            $('.object').unbind('click');
            return false;
        });
    });

    $('#q4 .surprise-describe').blur(function() {
        field = $(this).attr('id');
        post_data = {};
        post_data[field] = $(this).val();
        $.post('/survey/post/'+category_id+'/surprise', post_data, function(data) {
            // I should probably show the data has been uploaded
        });
    });
    $('#q5 .question-radio').click(function() {
        $.post('/survey/post/'+category_id+'/actor', {
            'actor':$('input:radio[name=actor]:checked').val()
        }, function(data) {
            // I should probably show the data has been uploaded
        });
    });
    $('#q6 .question-radio').click(function() {
        $.post('/survey/post/'+category_id+'/learned', {
            'learned':$('input:radio[name=learned]:checked').val()
        }, function(data) {
            // I should probably show the data has been uploaded
        });
    });
    $('#q7 #further-thoughts').blur(function() {
        $.post('/survey/post/'+category_id+'/further_thoughts', {
            'further_thoughts':$('#further-thoughts').val()
        }, function(data) {
            // I should probably show the data has been uploaded
        });
    });
});
