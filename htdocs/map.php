<!DOCTYPE html>
<html>
<head>
	<title>Wardrive Map</title>
	<link rel="stylesheet" href="leaflet/leaflet.css" />
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
	<script src="leaflet/leaflet.js"></script>
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

		/*
		var openJSON = <?php //echo file_get_contents('open.json'); ?>;
		var wepJSON = <?php //echo file_get_contents('wep.json'); ?>;
		var wpaJSON = <?php //echo file_get_contents('wpa.json'); ?>;
		*/


		// Set map tile-service urls
		var mapnik = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "OSM: Mapnik"}),
				cloudmade= new L.TileLayer('http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/{styleId}/256/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "OSM: CloudMade"}, {styleId: 997}),
				cloudmade_night = new L.TileLayer('http://{s}.tile.cloudmade.com/BC9A493B41014CAABB98F0471D759707/{styleId}/256/{z}/{x}/{y}.png', {maxZoom: 18, attribution: "OSM: CloudMade Night"}, {styleId: 999}),
				google_map = new L.TileLayer('http://mt{s}.google.com/vt/hl=en&x={x}&y={y}&z={z}', {maxZoom: 18, attribution: "Google Maps", subdomains: '0123'}),
				google_sat = new L.TileLayer('http://khm{s}.google.com/kh/v=95&x={x}&y={y}&z={z}', {maxZoom: 18, attribution: "Google Sat", subdomains: '0123'});

		// Construct network list from events
		function onFeatureParse(e, layerName) {
			e.layer.bindPopup(e.properties.popupContent);
			e.layer.options.title = e.properties.name;
			document.getElementById(layerName).innerHTML += "<a href='javascript:gotoFeature(" + layerName + "._layers[" + i + "])'>" + i + " " + e.properties.name + "</a><br />";
			i++;
		}

		function onOpenFeatureParse(e) {
			onFeatureParse(e, "openLayer");
		}

		function onWepFeatureParse(e) {
			onFeatureParse(e, "wepLayer");
		}

		function onWpaFeatureParse(e) {
			onFeatureParse(e, "wpaLayer");
		}

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

		var emptyFeatureCollection = {
			"type": "FeatureCollection",
			"features": []
		};

		var openIcon = L.Icon.extend({
			iconUrl: 'leaflet/images/marker.png',
			shadowUrl: 'leaflet/images/marker-shadow.png'
		});

		var wepIcon = L.Icon.extend({
			iconUrl: 'leaflet/images/marker.png',
			shadowUrl: 'leaflet/images/marker-shadow.png'
		});

		var wpaIcon = L.Icon.extend({
			iconUrl: 'leaflet/images/marker.png',
			shadowUrl: 'leaflet/images/marker-shadow.png'
		});
	
		// Use empty json first, as we need to set event-handlers before import
		var openLayer = new L.GeoJSON(emptyFeatureCollection, {pointToLayer: function (latlng){return new L.Marker(latlng, {icon: new openIcon()});}});
		var wepLayer = new L.GeoJSON(emptyFeatureCollection, {pointToLayer: function (latlng){return new L.Marker(latlng, {icon: new wepIcon()});}});
		var wpaLayer = new L.GeoJSON(emptyFeatureCollection, {pointToLayer: function (latlng){return new L.Marker(latlng, {icon: new wpaIcon()});}});

		openLayer.on("featureparse", onOpenFeatureParse);
		wepLayer.on("featureparse", onWepFeatureParse);
		wpaLayer.on("featureparse", onWpaFeatureParse);

		var i = 1;
		//openLayer.addGeoJSON(openJSON);
		//wepLayer.addGeoJSON(wepJSON);
		//wpaLayer.addGeoJSON(wpaJSON);

		// Create map in the 'map' div
		var map = new L.Map('map', {center: new L.LatLng(49.81672, 11.68396), zoom: 9, layers: [mapnik, openLayer]});

		var baseMaps = {
			"Mapnik": mapnik,
			"CloudMade": cloudmade,
			"CloudMade Night": cloudmade_night,
			"Google Maps": google_map,
			"Google Sat": google_sat
		};

		var overlayMaps = {
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

