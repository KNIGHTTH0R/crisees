var map;
var map_markers;
var wait_period;
var since;
var query_list_active = false;

/* Which time mode is Crisees operating in? */
var time_mode;

/* Global variables for the historic graph element */
var graph_id;
var graph_end_time;
var graph_ms;
var graph_length;
var graph_string;
var graph_start = 0;
var graph_end = 15;
var graph_historic_start;
var graph_historic_end;

function initialise_map(id) {
	var longitude = parseFloat($('#event-longitude-' + id).attr('value'));
	var latitude = parseFloat($('#event-latitude-' + id).attr('value'));
	
	if (map_markers) {
		map.removeLayer(map_markers);
	}
	else {
		map = new L.Map('map-' + id);
	}
	
	map_markers = new L.LayerGroup();
	map.addLayer(map_markers);
	
	var cloudmadeUrl = 'http://{s}.tile.cloudmade.com/8f8d09efa7cf4722a00a22454de7094f/997/256/{z}/{x}/{y}.png',
	cloudmadeAttrib = 'Map data &copy; 2011 OpenStreetMap contributors. Sexed up for Crisees',
	cloudmade = new L.TileLayer(cloudmadeUrl, {maxZoom: 18, attribution: cloudmadeAttrib});
	
	var london = new L.LatLng(latitude, longitude);
	
	map.setView(london, 13).addLayer(cloudmade);
}

function initialise_stream(event_id) {
	wait_period = 10;
	since = null;
	time_mode = 'realtime';
	
	refresh_stream(event_id);
	$(document).everyTime(wait_period.toString() + "s", function() { refresh_stream(event_id); }, 0);
}

function refresh_stream(event_id) {
	var active = $('#event-name-active-' + event_id).attr('value');
	var event_name = $('#event-name-' + event_id).attr('value');
	var list_parent = $('#live-stream-list-' + event_id);
	var other_parent = $('#live-media-list-' + event_id);
	var header = $('#live-stream-header-' + event_id);
	var url = 'event/' + event_name + '/stream/?';
	var search_query = $('#live-stream-search-field-' + event_id).val();
	var sentiment = determine_sentiment(event_id);
	
	if (search_query == "Enter a search query") {
		search_query = undefined;
	}
	
	if (time_mode == 'historic') {
		header.html("<em>Historic</em> Event Stream");
		url += 'start=' + server_date(graph_historic_start) + '&end=' + server_date(graph_historic_end) + '&limit=0';
		
		if (search_query != undefined) {
			url += '&query=' + search_query;
		}
		
		if (sentiment) {
			url += '&sentiment=' + sentiment;
		}
		
		$(document).stopTime();
		
		list_parent.html('');
		other_parent.html('');
		other_parent.parent().css('width', '125px');
		
		$('.live_scrollable').tinyscrollbar_update();
		$('.media_scrollable').tinyscrollbar_update();
		
		initialise_map(event_id);
		
		populate_stream(event_id, list_parent, other_parent, url);
		return false;
	}
	
	if (!active && since) {
		$(document).stopTime();
		
		if (search_query != undefined) {
			url += '&query=' + search_query;
		}
		
		if (sentiment) {
			url += '&sentiment=' + sentiment;
		}
		
		header.html("<em>Live</em> Event Stream");
		
		list_parent.html('');
		other_parent.html('');
		other_parent.parent().css('width', '125px');
		
		$('.live_scrollable').tinyscrollbar_update();
		$('.media_scrollable').tinyscrollbar_update();
		
		initialise_map(event_id);
		
		populate_stream(event_id, list_parent, other_parent, url);
		return false;
	}
	
	if (sentiment) {
		url += '&sentiment=' + sentiment;
	}
	
	if (since) {
		url += '&since=' + since;
	}
	else {
		list_parent.html('');
		other_parent.html('');
		other_parent.parent().css('width', '125px');
	}
	
	if (search_query != undefined) {
		url += '&query=' + search_query;
	}
	
	header.html("<em>Live</em> Event Stream");
	populate_stream(event_id, list_parent, other_parent, url);
	return true;
}

function populate_stream(event_id, list_parent, other_parent, url) {
	$.ajax({
		url: url,
		complete: function(xhr, textStatus) {
			if (xhr.status == 598)
				api_update_status(false);
		},
		success: function(data) {
			api_update_status(true);
			
			if (data['count'] > 0) {
				var text = "";
				var other_count = 0;
				var other_prev_count = 0;
				var other = "";
				
				for (item in data['items']) {
					if (data['items'][item]['geographical'] == 1 || data['items'][item]['geographical'] == 2) {
						add_map_point(data['items'][item]['longitude'],
									  data['items'][item]['latitude'],
									  data['items'][item]['source_id'],
									  data['items'][item]['item_id'],
									  data['items'][item]['geographical'])
					}
					
					if (data['items'][item]['media'] == 'text') {
						text = text + generate_text_element(event_id, data['items'][item]);
					}
					else {
						other = other + generate_other_element(event_id, data['items'][item]);
						other_count++;
					}
				}
				
				other_prev_count = other_parent.children().length;
				
				list_parent.prepend(text);
				other_parent.prepend(other);
				
				other_parent.parent().css('width', (125 * (other_prev_count + other_parent.children().length)) + 'px');
				
				$('.live_scrollable').tinyscrollbar_update();
				$('.media_scrollable').tinyscrollbar_update();
			}
			
			since = data['since_time'];
		}
	});
}

function add_map_point(longitude, latitude, source_id, item_id, type) {
	var static_prefix = $('#static-prefix').attr('value');
	longitude = parseFloat(longitude);
	latitude = parseFloat(latitude);
	
	if (type == 1) {
		var map_green_icon = L.Icon.extend({
			iconUrl    : static_prefix + 'images/leaflet/green.png',
			shadowUrl  : static_prefix + 'images/leaflet/shadow.png',
			iconSize   : new L.Point(32, 32),
			shadowSize : new L.Point(59, 32),
			iconAnchor : new L.Point(15, 32),
			popupAnchor: new L.Point(0, -34),
		});
		
		var inst = new map_green_icon();
		
		marker = new L.Marker(new L.LatLng(longitude, latitude), {icon: inst});
		map_markers.addLayer(marker);
	}
	else {
		var map_red_icon = L.Icon.extend({
			iconUrl    : static_prefix + 'images/leaflet/red.png',
			shadowUrl  : static_prefix + 'images/leaflet/shadow.png',
			iconSize   : new L.Point(32, 32),
			shadowSize : new L.Point(59, 32),
			iconAnchor : new L.Point(15, 32),
			popupAnchor: new L.Point(0, -34),
		});
		
		var inst = new map_red_icon();
		
		marker = new L.Marker(new L.LatLng(longitude, latitude), {icon: inst});
		map_markers.addLayer(marker);
	}
	
}

function pan_map(anchor_id) {
	var source_id = get_id_information(anchor_id, 3);
	var item_id = get_id_information(anchor_id, 4);
	var event_id = get_id_information(anchor_id, 5);
	
	var longitude = 'list-geo-longitude-' + source_id + '-' + item_id + '-' + event_id;
	var latitude = 'list-geo-latitude-' + source_id + '-' + item_id + '-' + event_id;
	
	longitude = parseFloat($('#' + longitude).attr('value'));
	latitude = parseFloat($('#' + latitude).attr('value'));
	
	var location = new L.LatLng(longitude, latitude);
	map.setView(location, 17);
}

function generate_other_element(event_id, data) {
	var static_prefix = $('#static-prefix').attr('value');
	
	return "<li><a href='" + data['link'] + "' title='Click to view this content on " + data['source_name'] + ".' style=\"background: url('" + static_prefix + "images/sources/" + data['source_id'] + "_64.png') no-repeat 50%;\"'><img src='" + data['thumbnail'] + "' alt='' /></a></li>";
}

function generate_text_element(event_id, data) {
	var static_prefix = $('#static-prefix').attr('value');
	var geographical = '';
	var sentiment = '';
	
	if (data['geographical'] == 1 || data['geographical'] == 2) {
		var id = data['source_id'] + '-' + data['item_id'] + '-' + data['event_id'];
		var longitude_field = "<input type='hidden' id='list-geo-longitude-" + id + "' value='" + data['longitude'] + "' />";
		var latitude_field = "<input type='hidden' id='list-geo-latitude-" + id + "' value='" + data['latitude'] + "' />";
		var image;
		
		if (data['geographical'] == 1) {
			image = 'globe.png';
		}
		else {
			image = 'globe_question.png';
		}
		
		geographical = "<a href='!pan-map' id='list-geo-icon-" + id + "' title='Geographical information detected; click to pan'><img src='" + static_prefix + "images/icons/" + image + "' alt='Planet Earth' /></a>" + longitude_field + latitude_field;
	}
	
	if (data['sentiment'] != undefined) {
		sentiment = parseFloat(data['sentiment']).toFixed(2);
		
		if (sentiment > 0.0) {
			sentiment = "<span class='sentiment green' title='Sentiment Value'>" + sentiment + "</span>";
		}
		else if (sentiment < 0.0) {
			sentiment = "<span class='sentiment red' title='Sentiment Value'>" + sentiment + "</span>";
		}
		else {
			sentiment = "<span class='sentiment' title='Sentiment Value'>" + sentiment + "</span>";
		}
	}
	
	return text = "<li><span class='text'>" + data['body'] + "</span><span class='bottom'><a href='" + data['link'] + "' title='Click to view this content on " + data['source_name'] + ".'><img src='" + static_prefix + "images/sources/" + data['source_id'] + "_20.png' alt='" + data['source_name'] + "' /></a>" + geographical + sentiment + "<span class='time'>" + live_stream_date(new Date(data['creation_time'])) + "</span></span></li>";
}

/*
 * Makes an AJAX call back to the server to toggle the active state of
 * an event, denoted by the id of the anchor of the clicked link.
 * 
 * The API is unavailable if a HTTP status code of 598 is returned from
 * the server. This function also updates the necessary components in
 * the DOM to signify the new active state if the request succeeds.
 */
function toggle_active(anchor_id) {
	var id = get_id_from_anchor(anchor_id);
	
	var event_name = $('#event-name-' + id).attr('value');
	var static_prefix = $('#static-prefix').attr('value');
	var active_element = $('#event-name-active-' + id);
	
	$.ajax({
		url: 'event/' + event_name + '/active/',
		complete: function(xhr, textStatus) {
			if (xhr.status == 598)
				api_update_status(false);
		},
		success: function(data) {
			api_update_status(true);
			
			if (data['id'] == id) {
				if (data['active']) {
					$('#tab-' + id).toggleClass('red green');
					$('#active-anchor-' + id).toggleClass('red green');
					$('#active-text-' + id).html("Sourcing");
					
					$('#active-image-' + id).attr('src', static_prefix + 'images/icons/play.png');
					active_element.attr('value', 'true');
					
					refresh_stream(id);
					$(document).stopTime();
					$(document).everyTime(wait_period.toString() + "s", function() { refresh_stream(id); }, 0);
				}
				else {
					$('#tab-' + id).toggleClass('green red');
					$('#active-anchor-' + id).toggleClass('green red');
					$('#active-text-' + id).html("Not Sourcing");
					
					$('#active-image-' + id).attr('src', static_prefix + 'images/icons/stop.png');
					active_element.attr('value', '');
				}
			}
		}
	});
}

function initialise_time_box(id) {
	var realtime_slider = $('#time-real-slider-' + id);
	var historic_slider = $('#time-historic-slider-' + id);
	var historic_histogram = $('#time-historic-histogram-' + id);
	var realtime_value = $('#time-real-slider-value-' + id);
	var event_name = $('#event-name-' + id).attr('value');
	var info = $('#time-historic-slider-text-' + id);
	
	var start_time = new Date($('#event-created-' + id).attr('value'));
	var end_time = null;
	
	if (time_mode == 'realtime') {
		$('#time-real-' + id).addClass('green');
		$('#time-historic-' + id).removeClass('green');
	}
	else {
		$('#time-real-' + id).removeClass('green');
		$('#time-historic-' + id).addClass('green');
	}
	
	if (graph_id) {
		if (graph_id != id) {
			graph_id = id;
			graph_end_time = null;
			graph_ms = null;
			graph_length = null;
			graph_string = null;
			graph_start = 0;
			graph_end = 15;
		}
	}
	
	if (graph_string) {
		info.html(graph_string);
	}
	else {
		info.html("Drag the slider to select a historic date range.");
	}
	
	realtime_slider.slider({
		animate: true,
		value: wait_period,
		min: 5,
		max: 60,
		step: 1,
		slide: function(event, ui) {
			realtime_value.html(ui.value);
			wait_period = ui.value;
			
			if (time_mode != 'realtime') {
				since = null;
				time_mode = 'realtime';
				
				refresh_stream(id);
				
				$('#time-real-' + id).addClass('green');
				$('#time-historic-' + id).removeClass('green');
				
				graph_historic_start = null;
				graph_historic_end = null;
			}
			
			$(document).stopTime();
			$(document).everyTime(wait_period.toString() + "s", function() { refresh_stream(id); }, 0);
		},
	});
	
	$.ajax({
		url: 'event/' + event_name + '/stream/?limit=0&time_only=1',
		complete: function(xhr, textStatus) {
			if (xhr.status == 598)
				api_update_status(false);
		},
		success: function(data) {
			api_update_status(true);
			graph_end_time = new Date(data['since_time']);
			
			var days_diff = days_from_ms(date_diff(start_time, graph_end_time));
			var graph_data = null;
			var bar_spacing = 4;
			var bar_width = 11;
			
			if (days_diff <= 1.00) {
				graph_ms = 1000 * 60 * 30;
			}
			else if (days_diff > 1.00 && days_diff <= 2.00) {
				graph_ms = 1000 * 60 * 60;
			}
			else if (days_diff > 2.00 && days_diff <= 4.00) {
				graph_ms = 1000 * 60 * 60 * 2;
			}
			else if (days_diff > 4.00 && days_diff <= 6.00) {
				graph_ms = 1000 * 60 * 60 * 3;
			}
			else if (days_diff > 6.00 && days_diff <= 8.00) {
				graph_ms = 1000 * 60 * 60 * 4;
			}
			else if (days_diff > 8.00 && days_diff <= 12.00) {
				graph_ms = 1000 * 60 * 60 * 6;
			}
			else if (days_diff > 12.00 && days_diff <= 16.00) {
				graph_ms = 1000 * 60 * 60 * 8;
			}
			else if (days_diff > 16.00 && days_diff <= 24.00) {
				graph_ms = 1000 * 60 * 60 * 12;
			}
			else if (days_diff > 24.00) {
				graph_ms = 1000 * 60 * 60 * 24;
			}
			
			graph_data = compute_graph_data(start_time, graph_end_time, graph_ms, data['items']);
			graph_length = graph_data.length;
			var slider_width = (graph_data.length * bar_width) + (graph_data.length * bar_spacing);
			
			historic_slider.css('width', slider_width + 'px');
			
			historic_histogram.sparkline(graph_data, {
				type: 'bar',
				height: '64px',
				barColor: '#2F3740',
				nullColor: '#2F3740',
				barWidth: bar_width,
				barSpacing: bar_spacing,
			});
			
			historic_slider.slider({
				animate: true,
				range: true,
				values: [graph_start, graph_end],
				min: 0,
				max: (bar_width + bar_spacing) * graph_data.length,
				step: (bar_width + bar_spacing),
				slide: function(event, ui) {
					var end_time = graph_end_time.getTime();
					var start = 
						(end_time - (graph_ms * (graph_length - (ui.values[0] / (bar_width + bar_spacing)))));
					var end = 
						(end_time - (graph_ms * (graph_length - (ui.values[1] / (bar_width + bar_spacing)))));
					
					graph_start = ui.values[0];
					graph_end = ui.values[1];
					
					graph_string = friendly_date(new Date(start)) + " - " + friendly_date(new Date(end));
					info.html(graph_string);
					
					time_mode = 'historic';
					$('#time-real-' + id).removeClass('green');
					$('#time-historic-' + id).addClass('green');
				},
				stop: function(event, ui) {
					var end_time = graph_end_time.getTime();
					var start = 
						(end_time - (graph_ms * (graph_length - (ui.values[0] / (bar_width + bar_spacing)))));
					var end = 
						(end_time - (graph_ms * (graph_length - (ui.values[1] / (bar_width + bar_spacing)))));
					
					time_mode = 'historic';
					graph_historic_start = new Date(start);
					graph_historic_end = new Date(end);
					refresh_stream(id);
				}
			});
		}
	});
}

function toggle_query_operator(anchor_id) {
	var event_id = get_id_information(anchor_id, 4);
	var query_id = get_id_information(anchor_id, 3);
	var operator = get_id_information(anchor_id, 2);
	var event_name = $('#event-name-' + event_id).attr('value');
	
	$.ajax({
		url: 'event/' + event_name + '/queries/' + query_id + '/?operator=' + operator,
		complete: function(xhr, textStatus) {
			if (xhr.status == 598)
				api_update_status(false);
		},
		success: function(data) {
			api_update_status(true);
			update_query_list(event_id);
			
			if (operator == 'not') {
				if (data['logical_not']) {
					$('#queries-operator-not-' + query_id + '-' + event_id).addClass('selected');
				}
				else {
					$('#queries-operator-not-' + query_id + '-' + event_id).removeClass('selected');
				}
			}
			else {
				if (data['operator'] == operator) {
					$('#queries-operator-and-' + query_id + '-' + event_id).removeClass('selected');
					$('#queries-operator-or-' + query_id + '-' + event_id).removeClass('selected');
					
					$('#queries-operator-' + operator +'-' + query_id + '-' + event_id).addClass('selected');
				}
			}
		}
	});
	
}

function toggle_query_active(anchor_id) {
	var event_id = get_id_information(anchor_id, 3);
	var query_id = get_id_information(anchor_id, 2);
	var event_name = $('#event-name-' + event_id).attr('value');
	var static_prefix = $('#static-prefix').attr('value');
	
	$.ajax({
		url: 'event/' + event_name + '/queries/' + query_id + '/?active',
		complete: function(xhr, textStatus) {
			if (xhr.status == 598)
				api_update_status(false);
		},
		success: function(data) {
			api_update_status(true);
			
			if (data['success']) {
				var list_item = $('#queries-list-' + query_id + '-' + event_id);
				var list_icon = $('#queries-active-image-' + query_id + '-' + event_id);
				
				if (data['active']) {
					list_item.toggleClass('green red');
					list_icon.attr('src', static_prefix + 'images/icons/play.png');
				}
				else {
					list_item.toggleClass('red green');
					list_icon.attr('src', static_prefix + 'images/icons/stop.png');
				}
				
				$('#queries-active-count-' + event_id).html(data['active_count']);
				update_query_list(event_id);
			}
		}
	});
}

function delete_query(anchor_id) {
	var event_id = get_id_information(anchor_id, 3);
	var query_id = get_id_information(anchor_id, 2);
	var event_name = $('#event-name-' + event_id).attr('value');
	
	$.ajax({
		url: 'event/' + event_name + '/queries/' + query_id + '/?delete',
		complete: function(xhr, textStatus) {
			if (xhr.status == 598)
				api_update_status(false);
		},
		success: function(data) {
			api_update_status(true);
			
			if (data['success']) {
				$('#queries-count-' + event_id).html(data['total_count']);
				$('#queries-active-count-' + event_id).html(data['active_count']);
				
				$('#queries-list-' + query_id + '-' + event_id).remove();
				$('.modal_content').tinyscrollbar_update();
				update_query_list(event_id);
			}
		}
	});
}

function change_query_text(anchor_id) {
	var event_id = get_id_information(anchor_id, 3);
	var query_id = get_id_information(anchor_id, 2);
	var event_name = $('#event-name-' + event_id).attr('value');
	var element = $('#' + anchor_id);
	
	if (/\S/.test(element.val())) {
		$.ajax({
			url: 'event/' + event_name + '/queries/' + query_id + '/?text=' + encodeURIComponent(element.val()),
			complete: function(xhr, textStatus) {
				if (xhr.status == 598)
					api_update_status(false);
			},
			success: function(data) {
				api_update_status(true);
				update_query_list(event_id);
				
				if (data['success']) {
					element.css('color', '#FFF');
					element.animate({'color': "#0A0B42"} , 1500);
				}
			}
		});
	}
	else {
		element.val(element.attr('value'));
		element.css('color', '#B90000');
		element.animate({'color': "#0A0B42"} , 1500);
	}
}

function toggle_query_add(anchor_id) {
	var event_id = get_id_information(anchor_id, 3);
	var element = $('#' + anchor_id);
	
	if (element.val() == "Enter a new query here") {
		element.fadeOut(200, function() {
			element.val("");
			element.css('font-style', 'normal');
			element.toggle(true);
		});
	}
}

function change_query_add(anchor_id) {
	var event_id = get_id_information(anchor_id, 3);
	var event_name = $('#event-name-' + event_id).attr('value');
	var element = $('#' + anchor_id);
	
	if (/\S/.test(element.val())) {
		$.ajax({
			url: 'event/' + event_name + '/queries/add/?query=' + encodeURIComponent(element.val()),
			dataType: 'html',
			complete: function(xhr, textStatus) {
				if (xhr.status == 598)
					api_update_status(false);
			},
			success: function(data) {
				api_update_status(true);
				
				$('#queries-list-' + event_id).append(data);
				
				$('#queries-count-' + event_id).html(parseInt($('#queries-count-' + event_id).html()) + 1);
				$('#queries-active-count-' + event_id).html(parseInt($('#queries-active-count-' + event_id).html()) + 1);
				$('.modal_content').tinyscrollbar_update();
				
				element.css('color', '#FFF');
				element.animate({'color': "#0A0B42"} , 1500);
				
				element.val("Enter a new query here");
				element.css('font-style', 'italic');
				element.toggle(true);
				update_query_list(event_id);
			}
		});
	}
	else {
		element.toggle(false);
		element.css('font-style', 'italic');
		element.val("Enter a new query here");
		element.fadeIn(200);
	}
}

function toggle_source_active(anchor_id) {
	var event_id = get_id_information(anchor_id, 2);
	var source_id = get_id_information(anchor_id, 1);
	var event_name = $('#event-name-' + event_id).attr('value');
	var static_prefix = $('#static-prefix').attr('value');
	
	$.ajax({
		url: 'event/' + event_name + '/sources/' + source_id + '/',
		complete: function(xhr, textStatus) {
			if (xhr.status == 598)
				api_update_status(false);
		},
		success: function(data) {
			api_update_status(true);
			
			var list_item = $('#sources-list-' + source_id + '-' + event_id);
			var list_icon = $('#sources-image-' + source_id + '-' + event_id);
			
			if (data['active']) {
				list_item.toggleClass('green red');
				list_icon.attr('src', static_prefix + 'images/icons/play.png');
			}
			else {
				list_item.toggleClass('red green');
				list_icon.attr('src', static_prefix + 'images/icons/stop.png');
			}
		}
	});
}

/*
 * Computes the values for the historic sliding graph.
 */
function compute_graph_data(start_time, end_time, graph_ms, data) {
	var return_values = [];
	var end_time = end_time.getTime();
	
	for (i = 0; i <= 47; i++) {
		var bar_start = end_time - graph_ms;
		var bar_count = 0;
		
		$.each(data, function(index, val) {
			var data_date = new Date(val['creation_time']).getTime();
			
			if (data_date >= bar_start && data_date <= end_time) {
				
				bar_count++;
				
				data = $.grep(data, function(value) {
					return value != val;
				});
				
			}
		});
		
		return_values.push(bar_count);
		end_time = bar_start;
		
		if (data.length == 0) {
			break;
		}
	}
	
	return return_values.reverse();
}

function toggle_search_box(element_id) {
	var box = $('#' + element_id);
	
	if (box.val() == "Enter a search query") {
		box.animate({'color': "#C9CBDA"} , 200, function() {
			box.val("");
			box.css('color', '#282B3C');
			box.css('font-style', 'normal');
		});
	}
	else if (box.val() == "") {
		box.val("Enter a search query");
		box.css('font-style', 'italic');
	}
}

function search_stream(element_id) {
	var event_id = get_id_information(element_id, 4);
	var mode = get_id_information(element_id, 3);
	var box = $('#live-stream-search-field-' + event_id);
	
	if (mode == "reset") {
		if (box.val() != "Enter a search query") {
			box.animate({'color': "#C9CBDA"} , 200, function() {
				box.val("Enter a search query");
				box.css('color', '#282B3C');
				box.css('font-style', 'italic');
				
				refresh_stream(event_id);
			});
		}
	}
	else {
		if (box.val() == "Enter a search query") {
			alert("Please enter a search query in the search box.");
		}
		else {
			refresh_stream(event_id);
		}
	}
	
}

function toggle_query_list(clicked_id) {
	var anchor = $('#' + clicked_id);
	var event_id = get_id_information(clicked_id, 4);
	var state = get_id_information(clicked_id, 3);
	var container = $('#queries-small-list-' + event_id);
	
	if (state == 'show') {
		container.slideDown(500, function() {
			query_list_active = true;
			
			anchor.html('<strong>Click to hide</strong>');
			anchor.attr('id', 'queries-list-toggle-hide-' + event_id);
			
			$('#queries-small-list-' + event_id).tinyscrollbar({ axis: 'x'});
			update_query_list(event_id);
		});
	}
	else {
		container.slideUp(500, function() {
			query_list_active = false;
			
			anchor.html('<strong>Click to show</strong>');
			anchor.attr('id', 'queries-list-toggle-show-' + event_id);
		});
	}
}

function update_query_list(event_id) {
	if ($('#queries-small-list-' + event_id).css('display') == 'block') {
		var event_name = $('#event-name-' + event_id).attr('value');
		
		$.ajax({
			url: 'event/' + event_name + '/queries/list/',
			dataType: 'html',
			complete: function(xhr, textStatus) {
				if (xhr.status == 598)
					api_update_status(false);
			},
			success: function(data) {
				api_update_status(true);
				
				$('#query-list-ul-' + event_id).html(data);
				$('#queries-small-list-' + event_id).tinyscrollbar_update();
			}
		});
	}
}

function search_sentiment(element_id) {
	var event_id = get_id_information(element_id, 4);
	var sentiment = get_id_information(element_id, 3);
	
	var positive_button = $('#live-stream-search-positive-' + event_id).parent();
	var negative_button = $('#live-stream-search-negative-' + event_id).parent();
	
	if (sentiment == 'positive') {
		positive_button.toggleClass('light');
		negative_button.addClass('light');
	}
	else if (sentiment == 'negative') {
		positive_button.addClass('light');
		negative_button.toggleClass('light');
	}
	
	refresh_stream(event_id);
}

function determine_sentiment(event_id) {
	var positive_button = $('#live-stream-search-positive-' + event_id).parent();
	var negative_button = $('#live-stream-search-negative-' + event_id).parent();
	
	if (!positive_button.is('.light')) {
		return 'positive';
	}
	else if (!negative_button.is('.light')) {
		return 'negative';
	}
	
	return false;
}
