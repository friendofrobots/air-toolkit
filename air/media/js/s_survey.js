var question_number = 1;

$(document).ready(function() {
    $('#survey-bar').toggle(function() {
	$(this).text('Hide Survey');
	$('#survey-questions').slideDown();
	$('#survey-spacer').css('height','160px');
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
	    if (question_number != 4) {
		$('#survey-right').show();
	    }
	    if (question_number == 1) {
		$('#survey-left').hide();
	    }
	}
	return false;
    });
    $('#survey-right').click(function(event) {
	if (question_number != 4) {
	    $('#q'+question_number).removeClass('activeq');
	    question_number++;
	    $('#q'+question_number).addClass('activeq');
	    if (question_number != 1) {
		$('#survey-left').show();
	    }
	    if (question_number == 4) {
		$('#survey-right').hide();
	    }
	}
	return false;
    });
    $('#survey').hover(function(){
	if (question_number != 1) {
	    $('#survey-left').show();
	}
	if (question_number != 4) {
	    $('#survey-right').show();
	}
    }, function() {
	$('#survey-left').hide();
	$('#survey-right').hide();
    });
});
