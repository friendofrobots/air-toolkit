$(document).ready(function() {
    $('.like').toggle(function() {
        if ($(this).next().is('empty')) {
            // get data from ajax call
        }
    },function() {
        $(this).hide('slow')
    });
});