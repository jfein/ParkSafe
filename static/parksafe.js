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
}


function deactivateMarker() {
	if (active_type == "CRIME") {
		active_marker.setIcon(img_crime);
		active_marker.setZIndex(10);
	} else if (active_type == "SIGN") {
		active_marker.setIcon(img_sign);
		active_marker.setZIndex(10);
		$.each(active_marker.nearby_crimes, function(i, id) {
			if (id in crime_markers) {
				crime_markers[id].setIcon(img_crime);
			}
		});
	}
	
	active_marker = null;
	active_type = "";
}


function activateSignMarker(id) {
	marker = sign_markers[id];

	if (active_marker != marker) {
		// Deactivate old sign markers
		deactivateMarker();
		
		// Activate this sign marker
		sign_markers[id].setIcon(img_sign_active);
		sign_markers[id].setZIndex(11);
		
		active_marker = marker;
		active_type = "SIGN";
	}
}


function activateCrimeMarker(id) {
	marker = crime_markers[id];
	
	if (active_marker != marker && (active_marker == null || $.inArray(id, active_marker.nearby_crimes) == -1)) {
		// Deactivate old sign markers
		deactivateMarker();
		
		// Activate this sign marker
		crime_markers[id].setIcon(img_crime_active);
		crime_markers[id].setZIndex(11);
		
		active_marker = marker;
		active_type = "CRIME";
	}
}


function activateCrimeScoreMarker(id) {
	crime_markers[id].setIcon(img_crime_score);
}


function addSign(sign) {
	if (!(sign.id in sign_markers)) {
		// Create a marker for the sign	
		var marker = new google.maps.Marker({
			position: new google.maps.LatLng(sign.latitude , sign.longitude),
			map: map,
			icon: img_sign,
			zIndex: 10,
		});
		sign_markers[sign.id] = marker;

		// Add click event to marker
		google.maps.event.addListener(marker, "click", function() {
				activateSignMarker(sign.id);
				querySign(sign.id);				
		});
	}
}


function addCrime(crime) {
	if (!(crime.id in crime_markers)) {
		// Create a marker for the sign	
		var marker = new google.maps.Marker({
			position: new google.maps.LatLng(crime.latitude , crime.longitude),
			map: map,
			icon: img_crime,
			zIndex: 10,
		});
		crime_markers[crime.id] = marker;

		// Add click event to marker
		google.maps.event.addListener(marker, "click", function() {
				activateCrimeMarker(crime.id);
                var html = "<b>Crime Types:</b> ";
                var keys = Object.keys(crime.crimeCounts);
                $.each(keys, function(i, key) {
                    html += key + " (" + crime.crimeCounts[key] + ")";
                    if (i != keys.length-1)
                        html += ", ";
                });
                html += "<br><b>Total # of Crimes:</b> " + crime.totalCrimes;
                html += "<br><b>From:</b> " + crime.mindate + " <b>To:</b> " + crime.maxdate
				$("#text_canvas").html(html);
		});	
	}
}


function addSigns(signs) {
	// Remove old signs
	$.each(sign_markers, function(key, sign_markers) {
		sign_markers.setMap(null);
	});
	sign_markers = {};

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
		addSign(sign)
	});
}


function addCrimes(crimes) {
    if (!crime_adding) {
        alert("CLEAR!");
        // Remove old crimes
        $.each(crime_markers, function(key, crime_marker) {
            crime_marker.setMap(null);
        });
        crime_markers = {};
        crimes_displayed = {};
    }
    
    var compiledCrimes = {};
	$(crimes).each(function(i, crime) {
        var key = crime.latitude + "," + crime.longitude;
        if ((crime_adding && !(key in crimes_displayed)) || !crime_adding) {
            if (key in compiledCrimes) {
                crimes_displayed[key]++;
                
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
            else {
                crimes_displayed[key] = 1;
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
        }
	});
    
    $.each(compiledCrimes, function(key, crime) {
        addCrime(crime);
    });
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
		data: { meters: max_crime_distance },
		success: function(sign) {
			// Make nearby crimes purple
			active_marker.nearby_crimes = [];
            crime_adding = true;
            addCrimes(sign.crimes);
            crime_adding = false;
			$.each(sign.crimes, function(i, crime) {
				active_marker.nearby_crimes.push(crime.id);
                if (crime.id in crime_markers)
                    activateCrimeScoreMarker(crime.id);
			});
			// Set content of crime
			var content = "<b>" + sign.description + "</b><br>" + 
				"<u>Safety Rating: " + Number((sign.crime_score).toFixed(2)) + "</u><br>" +
				"<table>" +
				"<tr><td># crimes within 1 month:</td><td>" + sign.crime_time_stats.one_month + "</td></tr>" +
				"<tr><td># crimes between 1 and 6 months:</td><td>" + sign.crime_time_stats.six_months + "</td></tr>" +
				"<tr><td># crimes between 6 months and 1 year:</td><td>" + sign.crime_time_stats.one_year + "</td></tr>" +
				"<tr><td># crimes over 1 year ago:</td><td>" + sign.crime_time_stats.greater_one_year + "</td></tr>" +
				"</table>";
			$("#text_canvas").html(content);
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
	var meters = max_searchable_area;
	
	if (map.getBounds()) {
		meters_per_degree = 111185.10693302986
	
		corner = map.getBounds().getNorthEast();
		ne_lat = corner.lat();
		ne_lon = corner.lng();
	
		x = (ne_lat - lat) * meters_per_degree;
		y = (ne_lon - lon) * meters_per_degree;
		
		meters = Math.min(meters, Math.sqrt(x*x + y*y) * 0.85);
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

var img_crime_score = new google.maps.MarkerImage(
	"static/images/crime_score.png",
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
var crimes_displayed = {};

var crime_adding = false;
var active_marker = null;
var active_type = "";


$(document).ready(function() {
	// TODO: get these dynamically
	cur_pos = new google.maps.LatLng(47.619804 , -122.356735)

	// Load map to page
	init();
	
	// Add close button
	$("#close").click(function() {
		deactivateMarker();
		$("#text_canvas").html("")
	});
	
	// Add search here button
	$("#search").click(function() {
		deactivateMarker();
		queryMap();
	});
	
	// Add search button
	$("#do_search").click(function() {
		codeAddress();
	});
	
	queryMap();
});
