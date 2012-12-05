/*
 * ------------------------------------------------
 * PARKSAFE FUNCTIONS
 * ------------------------------------------------
 */ 

 
function init() {
	// Create map
	var mapOptions = {
		center: cur_pos,
		minZoom: 15,
		zoom: 18,
		mapTypeId: google.maps.MapTypeId.ROADMAP,
		mapTypeControl: false,
	};
	map = new google.maps.Map($("#map_canvas")[0], mapOptions);
	
	// set up geocoder
	geocoder = new google.maps.Geocoder();
	
	// Make green marker for our position
	var pinColor = "C6EF8C";
	var pinImage = new google.maps.MarkerImage(
		"http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + pinColor,
		new google.maps.Size(20, 34),
		new google.maps.Point(0,0),
		new google.maps.Point(10, 34)
	);
	var pinShadow = new google.maps.MarkerImage(
		"http://chart.apis.google.com/chart?chst=d_map_pin_shadow",
		new google.maps.Size(40, 37),
		new google.maps.Point(0, 0),
		new google.maps.Point(12, 35)
	);
	var marker = new google.maps.Marker({
		position: cur_pos,
		map: map,
		icon: pinImage,
		shadow: pinShadow,
		zIndex: 0,
	});
}


function deactivateMarker() {
	// Active marker is a lone CRIME
	if (active_type == "CRIME") {
		active_marker.setIcon(img_crime);
		active_marker.setZIndex(10);
	} 
	// Active marker is a lone SIGN
	else if (active_type == "SIGN") {
		active_marker.setIcon(img_sign);
		active_marker.setZIndex(10);
		// Also deactivate nearby crimes
		$.each(active_marker.nearby_crimes, function(i, id) {
			crime_markers[id].setIcon(img_crime);
		});
	}
	
	active_marker = null;
	active_type = "";
}


function activateSignMarker(id, crimes) {
	marker = sign_markers[id];

	if (active_marker != marker) {
		// Deactivate old sign markers
		deactivateMarker();
		
		// Activate this sign marker
		marker.setIcon(img_sign_active);
		marker.setZIndex(11);
		
		marker.nearby_crimes = [];
		
		// Make nearby crimes purple
		$.each(crimes, function(i, crime) {
			var crime_marker_id = addCrimeMarker(crime);
			marker.nearby_crimes.push(crime_marker_id);
			activateCrimeScoreMarker(crime_marker_id);
		});
		
		// Set this as active marker
		active_marker = marker;
		active_type = "SIGN";
	}
	else {
		// Deactivate active crime score marker
		activateCrimeScoreMarker(active_marker.active_crime);
		active_marker.active_crime = null;
	}
}


function activateCrimeMarker(id) {
	marker = crime_markers[id];
	
	if (active_marker != marker) {
		// Deactivate old sign markers
		deactivateMarker();
		
		// Activate this sign marker
		crime_markers[id].setIcon(img_crime_active);
		crime_markers[id].setZIndex(11);

		// Set this as active marker		
		active_marker = marker;
		active_type = "CRIME";
	}
}


function activateCrimeScoreMarker(id) {
	crime_markers[id].setIcon(img_crime_score);
}

function activateActiveCrimeScoreMarker(id) {
	if (active_marker.active_crime != null)
		activateCrimeScoreMarker(active_marker.active_crime);
	crime_markers[id].setIcon(img_crime_score_active);
	active_marker.active_crime = id;
}


function addSignMarker(sign_id, lat, lon, text) {
	var marker_id = lat + ":" + lon;
	if (!(marker_id in sign_markers)) {
		// Create a marker for the sign	
		var marker = new google.maps.Marker({
			position: new google.maps.LatLng(lat , lon),
			map: map,
			icon: img_sign,
			zIndex: 10,
		});
		marker.text = text;
		sign_markers[marker_id] = marker;

		// Add click event to marker
		google.maps.event.addListener(marker, "click", function() {
			querySign(sign_id);
		});
	}
	return marker_id;
}


function aggregateSigns(signs) {
    var compiledSigns = {};
    $(signs).each(function(i, sign) {
        var key = sign.latitude + "," + sign.longitude;
		// Seen the key before
        if (key in compiledSigns) {
			if (compiledSigns[key].description.indexOf(sign.description) == -1)
				compiledSigns[key].description += ("<BR>" + sign.description);
        }
        else {
            compiledSigns[key] = sign;
        }
    });
	
	return compiledSigns;
}


function addSigns(signs) {
	// Remove old sign markers
	$.each(sign_markers, function(key, sign_markers) {
		sign_markers.setMap(null);
	});
	sign_markers = {};

	// Aggregate signs at same location
	signs = aggregateSigns(signs);
	
	// Place a marker for each distinct sign location
    $.each(signs, function(key,sign) {
		addSignMarker(sign.id, sign.latitude, sign.longitude, sign.description)
	});
}


function addCrimeMarker(crime) {
	var marker_id = crime.latitude + ":" + crime.longitude;
	if (!(marker_id in crime_markers)) {
			// Create a marker for the sign	
		var marker = new google.maps.Marker({
			position: new google.maps.LatLng(crime.latitude , crime.longitude),
			map: map,
			icon: img_crime,
			zIndex: 10,
		});
		crime_markers[marker_id] = marker;

		// Add click event to marker
		google.maps.event.addListener(marker, "click", function() {
				activateCrime(crime);
		});
	}
	return marker_id;
}


function aggregateCrimes(crimes) {
    var compiledCrimes = {};
    $(crimes).each(function(i, crime) {
        var key = crime.latitude + "," + crime.longitude;
		// Seen the key before
        if (key in compiledCrimes) {
			// Combine the descriptions
			if (!(crime.description.toLowerCase() in compiledCrimes[key].crimeCounts))
				compiledCrimes[key].crimeCounts[crime.description.toLowerCase()] = 1;
			else
				compiledCrimes[key].crimeCounts[crime.description.toLowerCase()]++;
			
			compiledCrimes[key].totalCrimes++;
			
			// Update the dates
			if (crime.date < compiledCrimes[key].mindate)
				compiledCrimes[key].mindate = crime.date;
			else if (crime.date > compiledCrimes[key].maxdate)
				compiledCrimes[key].maxdate = crime.date;
        }
		// New crime at that location
        else {
			var curCrime = {};
			curCrime.crimeCounts = {};
			curCrime.crimeCounts[crime.description.toLowerCase()] = 1;
			curCrime.totalCrimes = 1;
			curCrime.mindate = crime.date;
			curCrime.maxdate = crime.date;
			curCrime.latitude = crime.latitude;
			curCrime.longitude = crime.longitude;
			curCrime.id = crime.id;
			compiledCrimes[key] = curCrime;
        }
    });
	
	return compiledCrimes;
}


function addCrimes(crimes) {
	// Remove old crimes
	$.each(crime_markers, function(key, crime_marker) {
		crime_marker.setMap(null);
	});
	crime_markers = {};
	
	
	// Aggregate crimes to crimes in same location
	crimes = aggregateCrimes(crimes)

	// Add each crime marker to the map
    $.each(crimes, function(key, crime) {
        addCrimeMarker(crime);
    });
}


function activateCrime(crime) {
	var marker_id = crime.latitude + ":" + crime.longitude;
	
	// Make crime marker bright red
	if (!(active_type == "SIGN" && $.inArray(marker_id, active_marker.nearby_crimes) != -1))
		activateCrimeMarker(marker_id);
	// Make crime marker bright purple
	else
		activateActiveCrimeScoreMarker(marker_id);

	// Set content of the text canvas
	var mindate = $.datepicker.formatDate('m/d/yy', $.datepicker.parseDate("yy-mm-dd", crime.mindate));
	var maxdate = $.datepicker.formatDate('m/d/yy', $.datepicker.parseDate("yy-mm-dd", crime.maxdate));

	var html = "";
	html += "<b>" + crime.totalCrimes + " total crimes from " + mindate + " till " + maxdate + ":</b><br>";
	html += "<table>";
	var keys = Object.keys(crime.crimeCounts);
	$.each(keys, function(i, key) {
		html += "<tr><td># of " + key + " crimes:</td><td>" + crime.crimeCounts[key] + "</td></tr>";
	});
	html += "</table>";
	open_bottom_canvas(html);
}


function activateSign(sign) {
	var marker_id = sign.latitude + ":" + sign.longitude;
	
	// Make sign and crime markers active
	crimes = aggregateCrimes(sign.crimes);
	activateSignMarker(marker_id, crimes);
	
	// Set content of text canvas
	var content = "<b>" + active_marker.text + "</b><br>" + 
		"<u>Safety Rating: " + Number((sign.crime_score).toFixed(2)) + "</u><br>" +
		"<table>" +
		"<tr><td># crimes within 1 month:</td><td>" + sign.crime_time_stats.one_month + "</td></tr>" +
		"<tr><td># crimes between 1 and 6 months:</td><td>" + sign.crime_time_stats.six_months + "</td></tr>" +
		"<tr><td># crimes between 6 months and 1 year:</td><td>" + sign.crime_time_stats.one_year + "</td></tr>" +
		"<tr><td># crimes over 1 year ago:</td><td>" + sign.crime_time_stats.greater_one_year + "</td></tr>" +
		"</table>";
	open_bottom_canvas(content);
}


function codeAddress() {
    var address = $("#address").val() + " AND Seattle, Washington";
    geocoder.geocode(
		{ 'address': address}, 
		function(results, status) {
			if (status == google.maps.GeocoderStatus.OK) {
				map.setCenter(results[0].geometry.location);
				queryMap();
			} else {
				alert("Geocode was not successful for the following reason: " + status);
			}
    });
}


function querySigns(lat, lon, meters) {
	$('#overlay').fadeIn();
	queries_in_flight += 1;

	var data = { "lat" : lat , "lon" : lon , "meters" : meters };
	if ($("#filter_time").is(":checked")) {
		data['filter_time'] = "True";
	}

	$.ajax({
		url: 'signs.json',
		type: "GET",
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		data: data,
		success: function(signs) {
			queries_in_flight -= 1;
			if (queries_in_flight == 0) {
				$('#overlay').stop();
				$("#overlay").css({opacity:0.7});
				$('#overlay').hide();
			}
			addSigns(signs);
		}
	});
}


function querySign(id) {
	$('#overlay').fadeIn();
	queries_in_flight += 1;

	$.ajax({
		url: 'signs/' + id + '.json',
		type: "GET",
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		data: { meters: max_crime_distance },
		success: function(sign) {
			queries_in_flight -= 1;
			if (queries_in_flight == 0) {
				$('#overlay').stop();
				$("#overlay").css({opacity:0.7});
				$('#overlay').hide();
			}
			activateSign(sign);
		}
	});
}


function queryCrimes(lat, lon, meters) {
	$('#overlay').fadeIn();
	queries_in_flight += 1;
	
	$.ajax({
		url: 'crimes.json',
		type: "GET",
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		data: { "lat" : lat , "lon" : lon , "meters" : meters },
		success: function(crimes) {
			queries_in_flight -= 1;
			if (queries_in_flight == 0) {
				$('#overlay').stop();
				$("#overlay").css({opacity:0.7});
				$('#overlay').hide();
			}
			addCrimes(crimes);
		}
	});
}


function queryMap() {
	center = map.getCenter();
	lat = center.lat();
	lon = center.lng();
	var meters = max_searchable_area;
	
	if (map.getBounds()) {
		meters_per_degree = 111185.10693302986
	
		corner = map.getBounds().getNorthEast();
		ne_lat = corner.lat();
		ne_lon = corner.lng();
	
		x = (ne_lat - lat) * meters_per_degree;
		y = (ne_lon - lon) * meters_per_degree;
		
		meters = Math.min(meters, Math.sqrt(x*x + y*y));
	}
	querySigns(lat, lon, meters)
	queryCrimes(lat, lon, meters)
}


function close_bottom_canvas() {
	$("#close").hide();
	deactivateMarker();
	$("#text_canvas").html("")
	$("#bottom_canvas").height(10);
	$("#map_canvas").css({bottom: 11});
}

function open_bottom_canvas(html) {
	$("#text_canvas").html(html);
	$("#close").show();
	$("#map_canvas").css({bottom: 121});
	$("#bottom_canvas").height(120);
}


/*
 * ------------------------------------------------
 * DOCUMENT MAIN
 * ------------------------------------------------
 */ 
 
var img_sign = new google.maps.MarkerImage(
	"static/images/sign.png",
	new google.maps.Size(223, 223),
	new google.maps.Point(0,0),
	new google.maps.Point(8, 16),
	new google.maps.Size(16,16)
);

var img_sign_active = new google.maps.MarkerImage(
	"static/images/sign_active.png",
	new google.maps.Size(223, 223),
	new google.maps.Point(0,0),
	new google.maps.Point(8, 16),
	new google.maps.Size(16,16)
);

var img_crime = new google.maps.MarkerImage(
	"static/images/crime.png",
	new google.maps.Size(223, 223),
	new google.maps.Point(0,0),
	new google.maps.Point(8, 16),
	new google.maps.Size(16,16)
);

var img_crime_active = new google.maps.MarkerImage(
	"static/images/crime_active.png",
	new google.maps.Size(223, 223),
	new google.maps.Point(0,0),
	new google.maps.Point(8, 16),
	new google.maps.Size(16,16)
);

var img_crime_score = new google.maps.MarkerImage(
	"static/images/crime_score.png",
	new google.maps.Size(223, 223),
	new google.maps.Point(0,0),
	new google.maps.Point(8, 16),
	new google.maps.Size(16,16)
);

var img_crime_score_active = new google.maps.MarkerImage(
	"static/images/crime_score_active.png",
	new google.maps.Size(223, 223),
	new google.maps.Point(0,0),
	new google.maps.Point(8, 16),
	new google.maps.Size(16,16)
);

var max_searchable_area = 300;
var max_crime_distance = 250;

var map;
var geocoder;

var cur_pos;

var sign_markers = {};
var crime_markers = {};

var active_marker = null;
var active_type = "";

var queries_in_flight = 0;


$(document).ready(function() {
	// TODO: get these dynamically
	cur_pos = new google.maps.LatLng(47.619804 , -122.356735)

	// Load map to page
	init();
	
	// Add close button
	$("#close").click(function() {
		close_bottom_canvas();
	});
	
	// Add refresh button
	$("#refresh").click(function() {
		close_bottom_canvas();
		queryMap();
	});
	
	// Add search button
	$("#do_search").click(function() {
		close_bottom_canvas();
		codeAddress();
	});
	
	// Add text box hit "enter" to do search
	$("#address").keyup(function(event){
		if(event.keyCode == 13){
			$("#do_search").click();
		}
	});
	
	// Add center button
	$("#center").click(function() {
		map.setCenter(cur_pos);
		queryMap();
	});
	
	close_bottom_canvas();
	queryMap();
});
