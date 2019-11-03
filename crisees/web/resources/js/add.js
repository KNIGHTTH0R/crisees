var add_map;
var add_marker;
var add_polygon;

function initialise_add_map() {
	var latitude = 55.93074;
	var longitude = -3.93311;
	var start = new L.LatLng(latitude, longitude);
	var static_prefix = $('#static-prefix').attr('value');
	
	$('#map-add-box-longitude').html(Math.round(longitude * 100000) / 100000);
	$('#map-add-box-latitude').html(Math.round(latitude * 100000) / 100000);
	
	add_map = new L.Map('add-map');
	
	var cloudmadeUrl = 'http://{s}.tile.cloudmade.com/8f8d09efa7cf4722a00a22454de7094f/997/256/{z}/{x}/{y}.png',
	cloudmadeAttrib = 'Map data &copy; 2011 OpenStreetMap contributors. Sexed up for Crisees',
	cloudmade = new L.TileLayer(cloudmadeUrl, {maxZoom: 18, attribution: cloudmadeAttrib});
	
	add_map.setView(start, 7).addLayer(cloudmade);
	define_add_map_polygon();
	
	var map_green_icon = L.Icon.extend({
		iconUrl    : static_prefix + 'images/leaflet/green.png',
		shadowUrl  : static_prefix + 'images/leaflet/shadow.png',
		iconSize   : new L.Point(32, 32),
		shadowSize : new L.Point(59, 32),
		iconAnchor : new L.Point(15, 32),
		popupAnchor: new L.Point(0, -34),
	});
	
	var inst = new map_green_icon();
	
	add_marker = new L.Marker(start, {icon: inst});
	add_map.addLayer(add_marker);
	
	add_map.on('click', onAddMapClick);
}

function add_create() {
	var name = $('#map-add-box-name').val();
	var longitude = parseFloat($('#map-add-box-longitude').html());
	var latitude = parseFloat($('#map-add-box-latitude').html());
	var distance = parseInt($('#map-add-box-distance').val());
	
	if (name == 'Enter a name' || name == '') {
		alert("Please enter an event name.");
		return false;
	}
	
	if (isNaN(distance)) {
		alert("Please specify a whole number for the distance.");
		return false;
	}
	
	$('#add_modalback').fadeIn(300, function() {
		
		$('#add_modalmessage').fadeIn(200, function() {
			
			$.ajax({
				url: 'event/add/?name=' + name + '&longitude=' + longitude + '&latitude=' + latitude + '&distance=' + distance,
				complete: function(xhr, textStatus) {
					if (xhr.status == 598)
						api_update_status(false);
						
						$('#add_modalmessage').fadeOut(200, function() {
							$('#add_modalback').fadeOut(200);
						});
				},
				statusCode: {
					400: function() {
						var row = $('#map-add-row-name');
						row.css('background', '#ED7070');
					}
				},
				success: function(data) {
					api_update_status(true);
					
					$('#add_modalmessage').fadeOut(200, function() {
						$('#add_modalback').fadeOut(200);
					});
					
					if (data['active']) {
						element = '<li><a id="tab-' + data['event_id'] + '" class="green" href="event/' + data['tab_url'] + '/">' + data['name'] + '</a></li>';
					}
					else {
						element = '<li><a id="tab-' + data['event_id'] + '" class="red" href="event/' + data['tab_url'] + '/">' + data['name'] + '</a></li>';
					}
					
					$('#tab_list > li').each(function() {
						var anchor = $(this).find('a');
						
						if (anchor.is('.permanent')) {
							$(element).insertBefore($(this));
							window.location.hash = 'event/' + data['tab_url'] + '/';
							return false;
						}
						else {
							if (data['name'] < anchor.html()) {
								$(element).insertBefore($(this));
								window.location.hash = 'event/' + data['tab_url'] + '/';
								return false;
							}
						}
					});
					
				}
			});
			
		});
		
	});
	
	return true;
}

function add_map_name() {
	var element = $('#map-add-box-name');
	
	if (element.val() == 'Enter a name') {
		element.fadeOut(200, function() {
			element.val('');
			element.css('font-style', 'normal');
			element.show();
		});
	}
	else if (element.val() == '') {
		element.hide();
		element.val('Enter a name');
		element.css('font-style', 'italic');
		
		element.fadeIn(200);
	}
}

function parse_add_distance() {
	var distance = parseInt($('#map-add-box-distance').val());
	
	alert(distance);
}

function define_add_map_polygon() {
	var longitude = parseFloat($('#map-add-box-longitude').html());
	var latitude = parseFloat($('#map-add-box-latitude').html());
	var distance = parseInt($('#map-add-box-distance').val());
	
	if (isNaN(distance)) {
		if (add_polygon) {
			add_map.removeLayer(add_polygon);
		}
		
		return false;
	}
	
	if (add_polygon) {
		add_map.removeLayer(add_polygon);
	}
	
	/* TL, TR, BR, BL */
	var points = [destination_coord(latitude, longitude, distance, 315),
				  destination_coord(latitude, longitude, distance, 45),
				  destination_coord(latitude, longitude, distance, 135),
				  destination_coord(latitude, longitude, distance, 225)];
	
	add_polygon = new L.Polygon(points);
	add_map.addLayer(add_polygon);
}

function onAddMapClick(e) {
	var static_prefix = $('#static-prefix').attr('value');
	add_map.panTo(e.latlng);
	
	if (add_marker) {
		add_map.removeLayer(add_marker);
	}
	
	if (add_map.getZoom() <= 7) {
		add_map.setZoom(12);
	}
	
	var map_green_icon = L.Icon.extend({
		iconUrl    : static_prefix + 'images/leaflet/green.png',
		shadowUrl  : static_prefix + 'images/leaflet/shadow.png',
		iconSize   : new L.Point(32, 32),
		shadowSize : new L.Point(59, 32),
		iconAnchor : new L.Point(15, 32),
		popupAnchor: new L.Point(0, -34),
	});
	
	var inst = new map_green_icon();
	
	add_marker = new L.Marker(e.latlng, {icon: inst});
	add_map.addLayer(add_marker);
	
	$('#map-add-box-longitude').html(Math.round(e.latlng.lng * 100000) / 100000);
	$('#map-add-box-latitude').html(Math.round(e.latlng.lat * 100000) / 100000);
	
	define_add_map_polygon();
}

function deg_to_rad(value) {
	return value * (Math.PI / 180);
}

function rad_to_deg(value) {
	return value * (180 / Math.PI);
}

function fmod(x, y) {
	var tmp, tmp2, p = 0, pY = 0, l = 0.0, l2 = 0.0;
	
	tmp = x.toExponential().match(/^.\.?(.*)e(.+)$/);
	p = parseInt(tmp[2], 10) - (tmp[1] + '').length;
	tmp = y.toExponential().match(/^.\.?(.*)e(.+)$/);
	pY = parseInt(tmp[2], 10) - (tmp[1] + '').length;
	
	if (pY > p) {
		p = pY;
	}
	
	tmp2 = (x % y);
	
	if (p < -100 || p > 20) {
		l = Math.round(Math.log(tmp2) / Math.log(10));
		l2 = Math.pow(10, l);
		
		return (tmp2 / l2).toFixed(l - p) * l2;
	}
	else {
		return parseFloat(tmp2.toFixed(-p));
	}
}

function destination_coord(latitude, longitude, distance, bearing) {
	latitude = deg_to_rad(latitude);
	longitude = deg_to_rad(longitude);
	distance = distance / 6371.01;
	bearing = deg_to_rad(bearing)
	
	destination_latitude = 
		Math.asin(Math.sin(latitude)
				* Math.cos(distance)
				+ Math.cos(latitude)
				* Math.sin(distance)
				* Math.cos(bearing));
	
	destination_longitude =
		longitude + Math.atan2(
				  Math.sin(bearing)
				* Math.sin(distance)
				* Math.cos(latitude),
				  Math.cos(distance)
				- Math.sin(latitude)
				* Math.sin(destination_latitude));
	
	destination_longitude =
		fmod((destination_longitude + 3 * Math.PI),
			 (2 * Math.PI)) - Math.PI;
	
	return new L.LatLng(rad_to_deg(destination_latitude),
						rad_to_deg(destination_longitude));
}
