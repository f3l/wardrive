<!DOCTYPE html>
<html>
<head>
	<title>Wardrive Map</title>
	<link rel="stylesheet" href="/leaflet/leaflet.css" />
	<!--[if lte IE 8]><link rel="stylesheet" href="leaflet/leaflet.ie.css" /><![endif]-->
	<style type="text/css">
		<!--
		* html body 
		{
			height: 100%;
		}
		body
		{
			margin: 0;
			padding: 0;
			min-height: 100%;
		}
		#headerbar
		{
			height: 39px;
			padding: 5px;
			border-bottom: 1px solid #ccc;
		}
		#netlist
		{
			float:left;
			width: 170px;
			padding: 15px;
		}
		#map
		{
			min-height: 20px;
			margin: 0;
			border-left: 1px solid #ccc;
			position: absolute;
			top: 50px;
			bottom: 0;
			left: 200px;
			right: 0;
		}
		#titlebox {
			float: left;
			position: absolute;
			left: 0;
			padding: 10px;
		}
		#coordbox {
			position: absolute;
			right: 0;
			padding: 10px;
		}
		-->
	</style>
	<script src="/leaflet/leaflet.js"></script>
	<script src="/prototype.js"></script>
</head>
<body>
	<div id="container" style="position: absolute; top: 0; left: 0; right: 0; bottom: 0;">
		<div id="headerbar">
			<div id="titlebox">Wardrive Map</div>
			<div id="coordbox">
				<form method="get" action="" id="coorform" onsubmit="return setCoords();">
					<input type="text" name="coorfield" id="coorfield" size="20" style="border: none; text-align: right;" /><input type="submit" style="display: none;" />
				</form>
			</div>
		</div>
		<div id="netlist">
			<div id="openLayer" style="background-color: green;"></div>
			<div id="wepLayer" style="background-color: yellow; display: none;"></div>
			<div id="wpaLayer" style="background-color: red; display: none;"></div>
		</div>
		<div id="map"></div>
	</div>
	<script type="text/javascript">
		if(typeof(String.prototype.trim) === "undefined") {
			String.prototype.trim = function() {
				return String(this).replace(/^\s+|\s+$/g, '');
			};
		}

		// Set map tile-service urls
		var mapnik = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "OSM: Mapnik", maximumAge: 1000*3600*24*40}),
				cloudmade= new L.TileLayer('http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/{styleId}/256/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "OSM: CloudMade", maximumAge: 1000*3600*24*40}, {styleId: 997}),
				cloudmade_night = new L.TileLayer('http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/{styleId}/256/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "OSM: CloudMade Night", maximumAge: 1000*3600*24*40}, {styleId: 999}),
				google_map = new L.TileLayer('http://mt{s}.google.com/vt/hl=en&x={x}&y={y}&z={z}', {maxZoom: 18, attribution: "Google Maps", subdomains: '0123', maximumAge: 1000*3600*24*60}),
				google_sat = new L.TileLayer('http://khm{s}.google.com/kh/v=95&x={x}&y={y}&z={z}', {maxZoom: 18, attribution: "Google Sat", subdomains: '0123', maximumAge: 1000*3600*24*60}),
				allLayer_t = new L.TileLayer('/tiles/all/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "", maximumAge: 1000*3600*24*10}),
				openLayer_t = new L.TileLayer('/tiles/open/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "", maximumAge: 1000*3600*24*10}),
				wepLayer_t = new L.TileLayer('/tiles/wep/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "", maximumAge: 1000*3600*24*10}),
				wpaLayer_t = new L.TileLayer('/tiles/wpa/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "", maximumAge: 1000*3600*24*10});

		function onLayerChange() {
			if(document.getElementById('openbox').checked) {
				document.getElementById('openLayer').style.display = "block";
			}
			else {
				document.getElementById('openLayer').style.display = "none";
			}

			if(document.getElementById('wepbox').checked) {
				document.getElementById('wepLayer').style.display = "block";
			}
			else {
				document.getElementById('wepLayer').style.display = "none";
			}

			if(document.getElementById('wpabox').checked) {
				document.getElementById('wpaLayer').style.display = "block";
			}
			else {
				document.getElementById('wpaLayer').style.display = "none";
			}
		}

		function gotoFeature(e) {
			map.setView(e._latlng, 15);
			e.openPopup();
		}

		function setCoords(e) {
			coords = document.getElementById("coorfield").value;
			coords = coords.split(',');
			lat = coords[0].trim();
			lng = coords[1].trim();
			map.setView(new L.LatLng(lat, lng), 15);
			return false;
		}

		// Create map in the 'map' div
		var map = new L.Map('map', {center: new L.LatLng(49.81672, 11.68396), zoom: 9, layers: [mapnik]});

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

		var netpopup;
		map.on('click', function(e) {
			// AJAX request to get nearest network from database
			new Ajax.Request('/cgi-bin/near.py', {
				method: 'get',
				parameters: {lat: e.latlng.lat.toFixed(5), lon: e.latlng.lng.toFixed(5), dist: 1, limit: 1},
				onFailure: function(){ alert('Something went wrong...') },
				onSuccess: function(transport) {
					var json = transport.responseText.evalJSON();
					if(json['networks'].length > 0) {
						var net = json['networks'][0];
						netpopup = new L.Popup();
						netpopup.setLatLng(new L.LatLng(net['lat'], net['lon']));
						netpopup.setContent(net['description']);
						netpopup.options.offset.y = -26
						map.openPopup(netpopup);
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
				if(elem.type == 'checkbox') {
					elem.id = cbids[j];
					elem.onchange = onLayerChange;
					j++;
				}
			}
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

