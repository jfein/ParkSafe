/*
 * ------------------------------------------------
 * PARKSAFE FUNCTIONS
 * ------------------------------------------------
 */ 

 
function loadMap(lat, lon) {
	// Create map
	var mapOptions = {
		center: new google.maps.LatLng(lat , lon),
		minZoom: 15,
		zoom: 18,
		maxZoom: 25,
		mapTypeId: google.maps.MapTypeId.ROADMAP,
	};
	map = new google.maps.Map($("#map_canvas")[0], mapOptions);
	geocoder = new google.maps.Geocoder();
    
	/*
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
		position: new google.maps.LatLng(lat , lon),
		map: map,
		icon: pinImage,
		shadow: pinShadow,
		zIndex: 0,
	});
	*/
	
	// Query page on first map load
	google.maps.event.addListenerOnce(map, 'idle', function(){
		queryMap();
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
		$('#'+id).addClass('sign_active');
		
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
			if (compiledSigns[key].categoryde.indexOf(sign.categoryde) == -1)
				compiledSigns[key].categoryde += ("<BR>" + sign.categoryde);
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
		google.maps.event.addListener(
			marker, 
			"click", 
			function() {
				activateSignMarker(id);
				infowindow.setContent(sign.categoryde + "<br>" + sign.latitude + " " + sign.longitude);
				infowindow.open(map, marker);				
			}
		);
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
		google.maps.event.addListener(
			marker, 
			"click", 
			function() {
				activateCrimeMarker(i);
				infowindow.setContent(crime.summarized_offense_description);
				infowindow.open(map, marker);	
			}
		);	
	});
}


function codeAddress() {
    var address = document.getElementById("address").value + " AND Seattle, Washington";
    geocoder.geocode( { 'address': address}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            map.setCenter(results[0].geometry.location);
        } else {
            alert("Geocode was not successful for the following reason: " + status);
        }
    });
}


function querySigns(lat, lon, meters) {
	$.ajax({
		url: 'signs.json',
		type: "GET",
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		data: { "lat" : lat , "lon" : lon , "meters" : meters },
		success: function(signs) {
			addSigns(signs);
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
		success: function(signs) {
			addCrimes(signs);
		}
	});
}


function queryMap() {
	meters_per_degree = 111185.10693302986

	center = map.getCenter();
	lat = center.lat();
	lon = center.lng();
	
	corner = map.getBounds().getNorthEast();
	ne_lat = corner.lat();
	ne_lon = corner.lng();
	
	x = (ne_lat - lat) * meters_per_degree;
	y = (ne_lon - lon) * meters_per_degree;
	
	meters = Math.min(300, Math.sqrt(x*x + y*y));
	
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
var geocoder;
var sign_markers = [];
var crime_markers = [];

var infoOptions = {
	pixelOffset: new google.maps.Size(-100,10),
};
var infowindow = new google.maps.InfoWindow(infoOptions);
google.maps.event.addListener(infowindow,'closeclick', function(){
   deactivateMarkers();
});
var active_sign = -1;

	
$(document).ready(function() {
	// TODO: get these dynamically
	var lat = 47.619804;
	var lon = -122.356735;

	// Load map to page
	loadMap(lat, lon);
	
	// Add center button
	$("#center").click(function() {
		map.setCenter(new google.maps.LatLng(lat , lon));
	});
	
	// Add close button
	$("#close").click(function() {
		deactivateMarkers();
		infowindow.close();
	});
	
	// Add search here button
	$("#search").click(function() {
		queryMap();
	});
});
