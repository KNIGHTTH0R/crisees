
function get_hash() {
	return location.hash.replace( /^#/, '');
}

$('a').live('click', function(e) {
	var $link = $(this);
	
	if (($link.attr('href').lastIndexOf('event/', 0) === 0) ||
		($link.attr('href').lastIndexOf('add/', 0) === 0) ||
		($link.attr('href').lastIndexOf('about/', 0) === 0)) {
		e.preventDefault();
		location.hash = $link.attr('href');
	}
	
});

$(window).hashchange(function() {
	if (get_hash() == '')
		loadFirst();
	else
		switchTab();
});

function loadFirst() {
	var $first = $('#tabs ul li').first().find('a').attr('href');
	location.hash = $first;
	switchTab();
}

function switchTab() {
	// Stop all timers and reset all global event variables for the new tab
	$(document).stopTime();
	
	map = null;
	map_markers = null;
	wait_period = null;
	since = null;
	query_list_active = false;

	time_mode = null;

	graph_id = null;
	graph_end_time = null;
	graph_ms = null;
	graph_length = null;
	graph_string = null;
	graph_start = 0;
	graph_end = 15;
	graph_historic_start = null;
	graph_historic_end = null;
	
	$('#tabs > ul > li a').each(function() {
		$(this).removeClass('selected');
	});
	
	$('#tabs > ul > li a[href="' + get_hash() + '"]').addClass('selected');
	
	$('#event_container').empty();
	$('#event_container').show();
	$('#error_container').hide();
	
	$('#event_container').load(get_hash(), function(response, status, xhr) {
		if (status == 'error') {
			$('#event_container').empty();
			$('#event_container').hide();
			$('#error_container').show();
		}
		
		$('.live_scrollable').tinyscrollbar();
		$('.media_scrollable').tinyscrollbar({ axis: 'x'});
	});
}

$(window).load(function() {
	if (get_hash())
		switchTab();
	else
		loadFirst();
});
