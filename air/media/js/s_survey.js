$(document).ready(function() {
    $('#survey-left').click(function(event) {
	if (question_number != 1) {
	    $('#q'+question_number).removeClass('activeq');
	    question_number--;
	    $('#q'+question_number).addClass('activeq');
	    if (question_number != 9) {
		$('#survey-right').show();
	    }
	    if (question_number == 1) {
		$('#survey-left').hide();
	    }
	}
	return false;
    });
    $('#survey-right').click(function(event) {
	if (question_number != 9) {
	    $('#q'+question_number).removeClass('activeq');
	    question_number++;
	    $('#q'+question_number).addClass('activeq');
	    if (question_number != 1) {
		$('#survey-left').show();
	    }
	    if (question_number == 9) {
		$('#survey-right').hide();
	    }
	}
	return false;
    });
    $('#survey').hover(function(){
	if (question_number != 1) {
	    $('#survey-left').show();
	}
	if (question_number != 9) {
	    $('#survey-right').show();
	}
    }, function() {
	$('#survey-left').hide();
	$('#survey-right').hide();
    });
});
