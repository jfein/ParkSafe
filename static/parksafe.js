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
		maxZoom: 25,
		mapTypeId: google.maps.MapTypeId.ROADMAP,
	};
	map = new google.maps.Map($("#map_canvas")[0], mapOptions);
	
	// set up geocoder
	geocoder = new google.maps.Geocoder();
	
	// Set up info window
	infowindow = new google.maps.InfoWindow(
		{ pixelOffset: new google.maps.Size(-100,10) }
	);
	google.maps.event.addListener(infowindow, 'closeclick', function() {
			deactivateMarkers();
	});
}


function deactivateMarkers() {
	// Deactivate signs
	$(sign_markers).each(function(i, marker) {
		marker.setIcon(img_sign);
		marker.setZIndex(10);
	});

	// Deactivate crimes
	$(crime_markers).each(function(i, marker) {
		marker.setIcon(img_crime);
		marker.setZIndex(10);
	});
	
	active_sign = -1;
}


function activateSignMarker(id) {
	if (active_sign != id) {
		// Deactivate old sign markers
		deactivateMarkers();
		
		// Activate this sign marker
		sign_markers[id].setIcon(img_sign_active);
		sign_markers[id].setZIndex(11);
		
		active_sign = id;
	}
}


function activateCrimeMarker(id) {
	if (active_sign != id) {
		// Deactivate old sign markers
		deactivateMarkers();
		
		// Activate this sign marker
		crime_markers[id].setIcon(img_crime_active);
		crime_markers[id].setZIndex(11);
		
		active_sign = id;
	}
}


function addSigns(signs) {
	// Remove old signs
	$(sign_markers).each(function(i, sign_marker) {
		sign_marker.setMap(null);
	});
	sign_markers = [];

	// Aggregate signs at same location
    var compiledSigns = {};
    $(signs).each(function(i, sign) {
        var key = sign.latitude + "," + sign.longitude;
        if (key in compiledSigns) {
			if (compiledSigns[key].description.indexOf(sign.description) == -1)
				compiledSigns[key].description += ("<BR>" + sign.description);
        }
        else {
            compiledSigns[key] = sign;
        }
    });

    $.each(compiledSigns, function(key,sign) {
		// Create a marker for the sign	
		var marker = new google.maps.Marker({
			position: new google.maps.LatLng(sign.latitude , sign.longitude),
			map: map,
			icon: img_sign,
			zIndex: 10,
		});
		sign_markers.push(marker);
		
		var id = sign_markers.length - 1;

		// Add click event to marker
		google.maps.event.addListener(marker, "click", function() {
				activateSignMarker(id);
				querySign(sign.id);
				infowindow.setContent(sign.description + "<br>" + sign.latitude + " " + sign.longitude);
				infowindow.open(map, marker);				
		});
	});
}


function addCrimes(crimes) {
	// Remove old crimes
	$(crime_markers).each(function(i, crime_marker) {
		crime_marker.setMap(null);
	});
	crime_markers = [];

	$(crimes).each(function(i, crime) {
		// Create a marker for the sign	
		var marker = new google.maps.Marker({
			position: new google.maps.LatLng(crime.latitude , crime.longitude),
			map: map,
			icon: img_crime,
			zIndex: 10,
		});
		crime_markers.push(marker);

		// Add click event to marker
		google.maps.event.addListener(marker, "click", function() {
				activateCrimeMarker(i);
				infowindow.setContent(crime.description);
				infowindow.open(map, marker);	
		});	
	});
}


function codeAddress() {
    var address = $("#address").val() + " AND Seattle, Washington";
    geocoder.geocode(
		{ 'address': address}, 
		function(results, status) {
			if (status == google.maps.GeocoderStatus.OK) {
				map.setCenter(results[0].geometry.location);
			} else {
				alert("Geocode was not successful for the following reason: " + status);
			}
    });
}


function querySigns(lat, lon, meters) {
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
			addSigns(signs);
		}
	});
}


function querySign(id) {
	$.ajax({
		url: 'signs/' + id + '.json',
		type: "GET",
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		data: { meters: 50 },
		success: function(sign) {
			var x = 0;
		}
	});
}


function queryCrimes(lat, lon, meters) {
	$.ajax({
		url: 'crimes.json',
		type: "GET",
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		data: { "lat" : lat , "lon" : lon , "meters" : meters },
		success: function(crimes) {
			addCrimes(crimes);
		}
	});
}


function queryMap() {
	center = map.getCenter();
	lat = center.lat();
	lon = center.lng();
	meters = 300;
	
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
 

var map;
var infowindow;
var geocoder;

var cur_pos;

var sign_markers = [];
var crime_markers = [];

var active_sign = -1;


$(document).ready(function() {
	// TODO: get these dynamically
	cur_pos = new google.maps.LatLng(47.619804 , -122.356735)

	// Load map to page
	init();
	
	// Add close button
	$("#close").click(function() {
		deactivateMarkers();
		infowindow.close();
	});
	
	// Add search here button
	$("#search").click(function() {
		queryMap();
	});
	
	// Add search button
	$("#do_search").click(function() {
		codeAddress();
	});
	
	queryMap();
});
