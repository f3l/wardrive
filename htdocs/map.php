<!DOCTYPE html>
<html>
<head>
	<title>Wardrive Map</title>
	<link rel="stylesheet" href="/leaflet/leaflet.css" />
	<!--[if lte IE 8]><link rel="stylesheet" href="leaflet/leaflet.ie.css" /><![endif]-->
	<link rel="stylesheet" href="/css/style.css" />
	<script src="/leaflet/leaflet.js"></script>
	<script src="/js/prototype.js"></script>
	<script src="/js/map.js"></script>
</head>
<body>
	<div id="container" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0;">
		<div id="headerbar">
			<div id="titlebox">Wardrive Map</div>
			<div id="coordbox">
				<form method="get" id="coorform" onsubmit="return setCoords();">
					<input type="text" name="coorfield" id="coorfield" size="20" style="border: none; text-align: right;" /><input type="submit" style="display: none;" />
				</form>
			</div>
		</div>
		<div id="sidebar">
			<div id="sidetree">
				<span id="reset_uploads" class="link" onclick="switch_sidetab('uplist'); fetch_uploads(false, document.getElementById('hideempty').checked);">Uploads</span>
				<span id="cpoint">&gt;</span>
				<span id="current_upload"></span>
			</div>
			<div id="sidetools">
				<span id="hideopt"><label><input type="checkbox" name="hideempty" id="hideempty" onclick="display_uploads(this.checked);" />Hide empty Uploads</label></span>
			</div>
			<div id="uplist">
			</div>
			<div id="netlist">
			</div>
		</div>
		<div id="map"></div>
	</div>
	<script type="text/javascript">
		// Set map tile-service urls
		var mapnik = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "OSM: Mapnik", maximumAge: 1000*3600*24*40});
		var cloudmade = new L.TileLayer('http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/{styleId}/256/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "OSM: CloudMade", maximumAge: 1000*3600*24*40}, {styleId: 997});
		var cloudmade_night = new L.TileLayer('http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/{styleId}/256/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "OSM: CloudMade Night", maximumAge: 1000*3600*24*40}, {styleId: 999});
		var google_map = new L.TileLayer('http://mt{s}.google.com/vt/hl=en&x={x}&y={y}&z={z}', {maxZoom: 18, attribution: "Google Maps", subdomains: '0123', maximumAge: 1000*3600*24*60});
		var google_sat = new L.TileLayer('http://khm{s}.google.com/kh/v=95&x={x}&y={y}&z={z}', {maxZoom: 18, attribution: "Google Sat", subdomains: '0123', maximumAge: 1000*3600*24*60});
		var allLayer_t = new L.TileLayer('/tiles/all/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "", maximumAge: 1000*3600*24*10});
		var openLayer_t = new L.TileLayer('/tiles/open/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "", maximumAge: 1000*3600*24*10});
		var wepLayer_t = new L.TileLayer('/tiles/wep/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "", maximumAge: 1000*3600*24*10});
		var wpaLayer_t = new L.TileLayer('/tiles/wpa/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "", maximumAge: 1000*3600*24*10});

		// Create map in the 'map' div
		var map = new L.Map('map', {center: new L.LatLng(49.81672, 11.68396), zoom: 9, layers: [mapnik, allLayer_t]});

		var baseMaps = {
			"Mapnik": mapnik,
			"CloudMade": cloudmade,
			"CloudMade Night": cloudmade_night,
			"Google Maps": google_map,
			"Google Sat": google_sat
		};

		var overlayMaps = {
			"ALL": allLayer_t,
			"OPEN": openLayer_t,
			"WEP": wepLayer_t,
			"WPA": wpaLayer_t
		};

		layersControl = new L.Control.Layers(baseMaps, overlayMaps);
		map.addControl(layersControl);

		var shiftKeyPressed = false;
		map.on('mousemove', function(e) {
			// Don't update coordinates when shift is pressed
			if(!shiftKeyPressed) {
				document.getElementById("coorfield").value = e.latlng.lat.toFixed(5) + ', ' + e.latlng.lng.toFixed(5);
			}
		});

		map.on('click', function(e) {
			// AJAX request to get nearest network from database

			// Convert pixels to meters to calc search distance
			var tile_size = 256;
			var zoom_level = map.getZoom();
			var meters_per_pixel = (2 * Math.PI * 6378137) / (tile_size * Math.pow(2, zoom_level))
			var dist = 20 * meters_per_pixel;
			// convert distance from meter to km
			dist /= 1000;

			// Perform Request
			new Ajax.Request('/cgi-bin/getnet.py', {
				method: 'get',
				parameters: {mode: 'near', lat: e.latlng.lat.toFixed(5), lon: e.latlng.lng.toFixed(5), dist: dist, limit: 1},
				onFailure: function(){ alert('Something went wrong...') },
				onSuccess: function(transport) {
					var json = transport.responseText.evalJSON();
					if(json['networks'].length > 0) {
						display_network(json['networks'][0]);
					}
				}
			});
		});


		// Add ids and event handlers to layer checkboxes
		window.onload = function() {
			cbids = ['openbox', 'wepbox', 'wpabox'];
			var j = 0;
			for(var elem in document.getElementsByTagName('input')) {
				elem = document.getElementsByTagName('input')[elem];
				if(elem.type == 'checkbox' && !elem.name && !elem.id) {
					elem.id = cbids[j];
					elem.onchange = onLayerChange;
					j++;
				}
			}

			// Fill upload-bar
			fetch_uploads();
		}

		// Save shift status into var
		window.onkeydown = function(e) {
			// 16 = shift
			if(e.keyCode == 16) { 
				shiftKeyPressed = true;
			}
		}

		window.onkeyup = function(e) {
			// 16 = shift
			if(e.keyCode == 16) { 
				shiftKeyPressed = false;
			}
		}
	</script>
</body>
</html>

