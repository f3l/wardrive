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
			font-family: sans-serif;
		}
		#headerbar
		{
			height: 39px;
			padding: 5px;
			border-bottom: 1px solid #ccc;
		}
		#sidebar
		{
			float:left;
			width: 200px;
			padding: 7px 15px;
			/*font-size: 12px;*/
			font-size: 0.7em;
			overflow-y: auto;
			overflow-x: hidden;
			top: 50px;
			bottom: 0;
			position: absolute;
		}
		#map
		{
			min-height: 20px;
			margin: 0;
			border-left: 1px solid #ccc;
			position: absolute;
			top: 50px;
			bottom: 0;
			left: 230px;
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
		#sidetree {
			margin-bottom: 10px;
		}
		#cpoint, .current_upload {
			display: none;
		}
		#current_upload {
			font-weight: bold;
		}
		.link {
			cursor: pointer;
			text-decoration: underline;
			color: blue;
		}
		.loading {
			background: url('/images/loading.gif') no-repeat center;
			width: 100%;
			height: 95%;
		}
		.uptbl {
			padding-bottom: 5px;
			border-collapse: collapse;
			border: 1px solid #CCCCCC;
		}
		.uptbl td {
			padding: 1px 0;
			border: 1px dotted #CCCCCC;
			text-align: center;
		}
		.uptbl .uid {
			width: 40px;
		}
		.uptbl .ucnt {
			width: 30px;
		}
		.uptbl .udate {
			width: 100px;
		}
		.uptbl .utitle {
			width: 130px;
		}
		table tr.even {
			background-color: #f0f0f0;
		}
		table tr.odd {
			background-color: #fafafa;
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
		<div id="sidebar">
			<div id="sidetree">
				<span id="reset_uploads" class="link" onclick="switch_sidetab('uplist'); fetch_uploads();">Uploads</span>
				<span id="cpoint">&gt;</span>
				<span id="current_upload"></span>
			</div>
			<div id="uplist">
				<div id="openLayer" style="background-color: green;"></div>
				<div id="wepLayer" style="background-color: yellow; display: none;"></div>
				<div id="wpaLayer" style="background-color: red; display: none;"></div>
			</div>
			<div id="netlist">
				<div id="openLayer" style="background-color: green;"></div>
				<div id="wepLayer" style="background-color: yellow; display: none;"></div>
				<div id="wpaLayer" style="background-color: red; display: none;"></div>
			</div>
		</div>
		<div id="map"></div>
	</div>
	<script type="text/javascript">
		if(typeof(String.prototype.trim) === "undefined") {
			String.prototype.trim = function() {
				return String(this).replace(/^\s+|\s+$/g, '');
			};
		}

		String.prototype.trunc = function(n) {
			return this.substr(0,n-1) + (this.length>n?'&hellip;':'');
		};


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

		var uploads;
		function fetch_uploads() {
			uplist = document.getElementById('uplist');
			uplist.innerHTML = '';
			uplist.classList.add('loading');
			// AJAX request to get upload list
			new Ajax.Request('/cgi-bin/getupload.py', {
				method: 'get',
				parameters: {mode: 'list'},
				onFailure: function(){ alert('Something went wrong...') },
				onSuccess: function(transport) {
					var json = transport.responseText.evalJSON();
					uploads = json['uploads'];
					if(uploads.length > 0) {
						var uhtml = "<table class='uptbl'>";
						for(var i = 0 ; i < uploads.length ; i++) {
							upload = uploads[i];
							cycle = (i % 2)?'odd':'even';
							uhtml += "<tr class='" + cycle + "'>";
							uhtml += "<td rowspan='2' class='uid'><span class='link' onclick='select_upload(" + upload['id'] + ");'>#" + upload['id'] + "</span></td>";
							uhtml += "<td class='uuser'>" + upload['uploader'] + "</td>";
							uhtml += "<td class='udate'>" + upload['date'] + "</td>";
							uhtml += "</tr><tr class='" + cycle + "'>"
							uhtml += "<td class='ucnt'>" + upload['netcount'] + "</td>";
							uhtml += "<td class='utitle' title='" + upload['comment'] + "'>" + upload['comment'].trunc(14) + "</td>";
							uhtml += "</tr>";
						}
						uhtml += "</table>"
						uplist.classList.remove('loading');
						uplist.innerHTML = uhtml;
					}
				}
			});
		}

		var sidetab = 'uplist';
		function switch_sidetab(tabname) {
			document.getElementById('netlist').style.display = 'none';
			document.getElementById('uplist').style.display = 'none';
			document.getElementById('cpoint').style.display = 'none';
			document.getElementById('current_upload').style.display = 'none';
			document.getElementById(tabname).style.display = 'block';
			if(tabname == 'netlist') {
				document.getElementById('cpoint').style.display = 'inline';
				document.getElementById('current_upload').style.display = 'inline';
			}
			sidetab = tabname;
		}

		var chtml = '';
		function select_upload(supload) {
			switch_sidetab('netlist');
			netlist = document.getElementById('netlist');
			document.getElementById('current_upload').innerHTML = "#" + supload;
			netlist.innerHTML = '';
			chtml = '';
			netlist.classList.add('loading');

			// Get upload info
			new Ajax.Request('/cgi-bin/getupload.py', {
				method: 'get',
				parameters: {mode: 'id', id: supload},
				onFailure: function(){ alert('Something went wrong...') },
				onSuccess: function(transport) {
					var json = transport.responseText.evalJSON();
					uploads = json['uploads'];
					if(uploads.length > 0) {
						var uhtml = '';
						upload = uploads[0];
						uhtml += "<div class='upload_info'>";
						uhtml += upload['date'] + " by " + upload['uploader'] + "<br />";
						uhtml += upload['netcount'] + " new Networks";
						if(upload['comment'].length > 0) {
							uhtml += "<br /><br />";
							uhtml += upload['comment'];
						}
						uhtml += "<hr />"
						uhtml += "</div>";
						chtml += uhtml;

						// Get netlist
						new Ajax.Request('/cgi-bin/getnet.py', {
							method: 'get',
							parameters: {mode: 'upload', upload: supload},
							onFailure: function(){ alert('Something went wrong...') },
							onSuccess: function(transport) {
								var json = transport.responseText.evalJSON();
								networks = json['networks'];
								if(networks.length > 0) {
									var nhtml = '';
									for(var i = 0 ; i < networks.length ; i++) {
										var net = networks[i];
										nhtml += net['ssid'] + "<br />";
									}
									chtml += nhtml;
								}
								netlist.innerHTML = chtml;
								chtml = '';
								netlist.classList.remove('loading');
							}
						});
					}
				}
			});

		}

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

