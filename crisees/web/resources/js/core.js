var months = ['Jan',
			  'Feb',
			  'Mar',
			  'Apr',
			  'May',
			  'Jun',
			  'Jul',
			  'Aug',
			  'Sept',
			  'Oct',
			  'Nov',
			  'Dec']

/*
 * Binding code - latches on to any anchor which is clicked. If the URL
 * of the anchor is one of the URLs in the conditional block below,
 * normal behaviour is aborted and the subsequent commands are executed.
 */
$('a').live('click', function(event) {
	var clicked = $(this);
	
	if (clicked.attr('href') == '!toggle-anchor') {
		event.preventDefault();
		toggle_active(clicked.attr('id'));
	}
	else if ((clicked.attr('href') == '!queries') || (clicked.attr('href') == '!sources') || (clicked.attr('href') == '!time')) {
		event.preventDefault();
		toggle_modal(clicked.attr('id'));
	}
	else if (clicked.attr('href') == '!toggle-query-operator') {
		event.preventDefault();
		toggle_query_operator(clicked.attr('id'));
	}
	else if (clicked.attr('href') == '!toggle-query-active') {
		event.preventDefault();
		toggle_query_active(clicked.attr('id'));
	}
	else if (clicked.attr('href') == '!delete-query') {
		event.preventDefault();
		delete_query(clicked.attr('id'));
	}
	else if (clicked.attr('href') == '!toggle-source-active') {
		event.preventDefault();
		toggle_source_active(clicked.attr('id'));
	}
	else if (clicked.attr('href') == '!pan-map') {
		event.preventDefault();
		pan_map(clicked.attr('id'));
	}
	else if (clicked.attr('href') == '!search-stream') {
		event.preventDefault();
		search_stream(clicked.attr('id'));
	}
	else if (clicked.attr('href') == '!search-stream-sentiment') {
		event.preventDefault();
		search_sentiment(clicked.attr('id'));
	}
	else if (clicked.attr('href') == '!reset-stream') {
		event.preventDefault();
		search_stream(clicked.attr('id'));
	}
	else if (clicked.attr('href') == '!toggle-query-list') {
		event.preventDefault();
		toggle_query_list(clicked.attr('id'));
	}
	
	// If we get here and we haven't entered any conditional block,
	// we resume normal behaviour (i.e. go to where the link says).
	
});

$('input').live('click', function(event) {
	var clicked = $(this);
	
	if (clicked.attr('id').substring(0, 17) == 'queries-term-add-') {
		toggle_query_add(clicked.attr('id'));
	}
	else if (clicked.attr('id').substring(0, 25) == 'live-stream-search-field-') {
		toggle_search_box(clicked.attr('id'));
	}
	else if (clicked.attr('id') == 'map-add-box-name') {
		add_map_name();
	}
	else if (clicked.attr('id') == 'map-add-box-create') {
		add_create();
	}
});

$('input').live('blur', function(event) {
	var clicked = $(this);
	
	if (clicked.attr('id').substring(0, 17) == 'queries-term-add-') {
		change_query_add(clicked.attr('id'));
	}
	else if (clicked.attr('id').substring(0, 13) == 'queries-term-') {
		change_query_text(clicked.attr('id'));
	}
	else if (clicked.attr('id').substring(0, 26) == 'live-stream-search-field-') {
		toggle_search_box(clicked.attr('id'));
	}
	else if (clicked.attr('id') == 'map-add-box-name') {
		add_map_name();
	}
});

$('.stream-search').live('keyup', function(event) {
	if (event.which == 13) {
		search_stream($(this).attr('id'));
	}
});

$('#map-add-box-distance').live('keyup', function(event) {
	define_add_map_polygon();
});

$('input').live('change', function(event) {
	var changed = $(this);
	
	/*if (changed.attr('id').substring(0, 13) == 'queries-term-') {
		change_query_text(changed.attr('id'));
	}*/
});

/*
 * Looks out for a click on the modal background.
 */
$('#modalback').live('click', function() {
	toggle_modal();
});

/*
 * Responsible for updating the API status indicator at the top right of
 * an event tab should the API become unavailable during normal operation
 * of the web application.
 */
function api_update_status(is_available) {
	var static_prefix = $('#static-prefix').attr('value');
	
	if (is_available) {
		$('#api-status-image').attr('src', static_prefix + 'images/icons/data_ok.png');
		$('#api-status-text').html("API Available");
	}
	else {
		$('#api-status-image').attr('src', static_prefix + 'images/icons/data_stop.png');
		$('#api-status-text').html("<strong>API Unavailable</strong>");
	}
}

/*
 * Returns the event id from an anchor.
 * Depreciated - use get_id_information()
 */
function get_id_from_anchor(anchor_id) {
	return anchor_id.substring(
				anchor_id.lastIndexOf('-') + 1,
				anchor_id.length);
}

/*
 * Toggles the state (active/inactive) of a modal dialog.
 * This is based on the anchor ID passed to this function.
 */
function toggle_modal(anchor_id) {
	if (anchor_id == undefined) {
		var modal_divs = $('div[id^="modal-"]');
		var modal_background = $('#modalback');
		
		modal_divs.slideUp(400, function() {
			modal_divs.css('display', 'none');
			modal_divs.html('');
			
			modal_background.fadeOut(300);
		});
		
		return;
	}
	
	var id = get_id_from_anchor(anchor_id);
	var mode = anchor_id.substring(0, anchor_id.indexOf('-'));
	var event_name = $('#event-name-' + id).attr('value');
	var modal_div = $('#modal-' + id);
	var modal_background = $('#modalback');
	var current = $('#modal-current-' + id).attr('value');
	
	if (modal_div.css('display') == 'none') {	
		
		$.ajax({
			url: 'event/' + event_name + '/' + mode + '/',
			dataType: 'html',
			complete: function(xhr, textStatus) {
				if (xhr.status == 598) {
					api_update_status(false);
					modal_div.slideUp();
					modal_div.html('');
					
					return;
				}
				
				if (mode == 'time') {
					var realtime_value = $('#time-real-slider-value-' + id);
					realtime_value.html(wait_period);
				}
				
				modal_background.fadeIn(300, function() {
					modal_div.slideDown(400, function () {
						$('.modal_content').tinyscrollbar();
						
						if (mode == 'time') {
							initialise_time_box(id);
						}
						
						if (mode == 'queries') {
							var queries_list = $('#queries-list-' + id);
							
							if (query_list_active) {
								$('#queries-list-toggle-show-' + id).html('<strong>Click to hide</strong>');
								$('#queries-list-toggle-show-' + id).attr('id', 'queries-list-toggle-hide-' + id);
							}
							
							queries_list.sortable({
								handle: '.draggable',
								update: function() {
									var sequence = [];
									
									queries_list.children('li').each(function(index, element) {
										var query_id = get_id_information(element.id, 2);
										sequence.push(query_id);
									});
									
									$.ajax({
										url: 'event/' + event_name + '/queries/order/?sequence=' + sequence,
										complete: function(xhr, textStatus) {
											if (xhr.status == 598)
												api_update_status(false);
										},
										success: function(data) {
											api_update_status(true);
											var queries = $('input[id^="queries-term-"]');
											
											queries.css('color', '#FFF');
											queries.animate({'color': "#0A0B42"} , 1500);
										}
									});
									
									update_query_list(id);
								}
							});
						}
					});
				});
			},
			success: function(data) {
				api_update_status(true);
				modal_div.html(data);
			}
		});
	}
	else {
		modal_div.slideUp(400, function() {
			modal_div.css('display', 'none');
			modal_div.html('');
			
			if ((current != undefined) && (current != mode))
				toggle_modal(anchor_id);
			else
				modal_background.fadeOut(300);
		});
	}
	
}

/*
 * Returns a string representing the Date object date in the format
 * YYYY-MM-DDTHH:MM:SS
 */
function server_date(date) {
	var year = date.getFullYear();
	var month = zero_padding(date.getMonth() + 1, 2);
	var day = zero_padding(date.getDate(), 2);
	var hour = zero_padding(date.getHours(), 2);
	var minute = zero_padding(date.getMinutes(), 2);
	var second = zero_padding(date.getSeconds(), 2);
	
	return year + "-" + month + "-" + day + "T" + hour + ":" + minute + ":" + second;
}

/*
 * Returns a string representing Date date as a locale-specific string.
 */
function friendly_date(date) {
	return date.toLocaleDateString() + " " + date.toLocaleTimeString();
}

/*
 * Returns a string representing Date date in the format used for displaying
 * in the live stream of information.
 */
function live_stream_date(date) {
	var year = date.getFullYear();
	var month = months[date.getMonth()];
	var day = zero_padding(date.getDate(), 2);
	var hour = zero_padding(date.getHours(), 2);
	var minute = zero_padding(date.getMinutes(), 2);
	var second = zero_padding(date.getSeconds(), 2);
	
	return day + " " + month + " " + year + ", " + hour + ":" + minute + ":" + second;
}

/*
 * Pads a number represented by a string with the number specified by
 * count.
 */
function zero_padding(number, count) {
	number = number.toString();
	
	while (number.length < count) {
		number = "0" + number;
	}
	
	return number;
}

/*
 * Returns the difference between two dates.
 */
function date_diff(date1, date2) {
	return date2 - date1;
}

/*
 * Returns the value representing how many days the passed integer - ms -
 * representing milliseconds - corresponds to.
 */
function days_from_ms(ms) {
	var DAY = 1000 * 60 * 60 * 24;
	return ms / DAY;
}

/*
 * Returns information from ID string id_string at position position.
 * The string is split at the occurence of a dash (-).
 */
function get_id_information(id_string, position) {
	var occurences = id_string.replace(/[^-]/g, '').length;
	var i = 0;
	
	if (position > occurences) {
		return false;
	}
	
	for (i = 1; i <= occurences; i++ ) {
		var index_of = id_string.indexOf('-', 0);
		id_string = id_string.substring(index_of + 1, id_string.length);
		
		if (i == position) {
			var index_of = id_string.indexOf('-', 0);
			
			if (index_of == -1) {
				return id_string;
			}
			
			return id_string.substring(0, index_of);
		}
		
	}
	
	return false;
}
