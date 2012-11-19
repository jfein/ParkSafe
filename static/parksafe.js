/*
 * ------------------------------------------------
 * PARKSAFE FUNCTIONS
 * ------------------------------------------------
 */ 

 
function loadMap(lat, lon) {
	// Create map
	var mapOptions = {
		center: new google.maps.LatLng(lat , lon),
		minZoom: 18,
		zoom: 19,
		maxZoom: 25,
		mapTypeId: google.maps.MapTypeId.ROADMAP,
	};
	var map = new google.maps.Map($("#map_canvas")[0], mapOptions);
	
	// Make green marker for our position
	var pinColor = "C6EF8C";
	var pinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_xpin_letter&chld=pin_sleft|%E2%80%A2|" + pinColor + "|000000",
		new google.maps.Size(24, 34),
		new google.maps.Point(0,0),
		new google.maps.Point(21, 34));
	var marker = new google.maps.Marker({
		position: new google.maps.LatLng(lat , lon),
		map: map,
		icon: pinImage,
		zIndex: 10000,
	});
	
	return map;
}


function addSigns(signs, map) {
	var sign_divs = [];

	signs.forEach(function(sign) {
		// add marker
		var marker = new google.maps.Marker({
			position: new google.maps.LatLng(sign.latitude , sign.longitude),
			map: map,
			cursor: sign.customtext,
			zIndex: 0
		});
		// add to list
		sign_divs.push("<div class='sign'>" + sign.customtext + "</div>")
	});
	
	$('#sign_canvas').html( sign_divs.join('') );
}


function loadSigns(lat, lon, meters, map) {
	$.ajax({
		url: 'signs.json',
		type: "GET",
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		data: { "lat" : lat , "lon" : lon , "meters" : meters },
		success: function(signs) {
			addSigns(signs, map);
		}
	});
}


/*
 * ------------------------------------------------
 * DOCUMENT MAIN
 * ------------------------------------------------
 */ 
	
	
$(document).ready(function(){
	// TODO: get these dynamically
	var lat = 47.6433;
	var lon = -122.3165;

	// Load map to page
	var map = loadMap(lat, lon);
	
	// Add sign data to the page
	loadSigns(lat, lon, 100, map);
	
	// Add center
	$("#center").click(function() {
		map.setCenter(new google.maps.LatLng(lat , lon));
	});
});
