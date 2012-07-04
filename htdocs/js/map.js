if(typeof(String.prototype.trim) === "undefined") {
	String.prototype.trim = function() {
		return String(this).replace(/^\s+|\s+$/g, '');
	};
}

String.prototype.trunc = function(n) {
	return this.substr(0,n-1) + (this.length>n?'&hellip;':'');
};

// Cookie management
function createCookie(name,value,days) {
	if (days) {
		var date = new Date();
		date.setTime(date.getTime()+(days*24*60*60*1000));
		var expires = "; expires="+date.toGMTString();
	}
	else var expires = "";
	document.cookie = name+"="+value+expires+"; path=/";
}
function readCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
		var c = ca[i];
		while (c.charAt(0)==' ') c = c.substring(1,c.length);
		if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	}
	return null;
}
function eraseCookie(name) {
	createCookie(name,"",-1);
}


function gotoFeature(e) {
	map.setView(e._latlng, 15);
	e.openPopup();
}

// set map coordinates from coord-form
function setCoords(e) {
	coords = document.getElementById("coorfield").value;
	coords = coords.split(',');
	lat = coords[0].trim();
	lng = coords[1].trim();
	map.setView(new L.LatLng(lat, lng), 14);
	return false;
}

var uploads;
function fetch_uploads(cached, hideempty) {
	uplist = document.getElementById('uplist');
	uplist.innerHTML = '';
	uplist.classList.add('loading');
	if(cached) {
		display_uploads(hideempty);
	}
	else {
		// AJAX request to get upload list
		new Ajax.Request('/cgi-bin/getupload.py', {
			method: 'get',
			parameters: {mode: 'list'},
			onFailure: function(){ alert('Something went wrong...') },
			onSuccess: function(transport) {
				var json = transport.responseText.evalJSON();
				uploads = json['uploads'];
				display_uploads(hideempty);
			}
		});
	}
}

function display_uploads(hideempty) {
	if(uploads.length > 0) {
		var uhtml = "<table class='uptbl'>";
		j = 0;
		for(var i = 0 ; i < uploads.length ; i++) {
			upload = uploads[i];
			if(! hideempty || upload['netcount']) {
				cycle = (j++ % 2)?'odd':'even';
				uhtml += "<tr class='" + cycle + "'>";
				uhtml += "<td rowspan='2' class='uid'><span class='link' onclick='select_upload(" + upload['id'] + ");'>#" + upload['id'] + "</span></td>";
				uhtml += "<td class='uuser'>" + upload['uploader'] + "</td>";
				uhtml += "<td class='udate'>" + upload['date'] + "</td>";
				uhtml += "</tr><tr class='" + cycle + "'>"
				uhtml += "<td class='ucnt'>" + (upload['netcount']?upload['netcount']:'-') + "</td>";
				uhtml += "<td class='utitle' title='" + upload['comment'] + "'>" + upload['comment'].trunc(14) + "</td>";
				uhtml += "</tr>";
			}
		}
		uhtml += "</table>"
		uplist.classList.remove('loading');
		uplist.innerHTML = uhtml;
	}
}

var netpopup;
function display_network(net, center) {
	netpopup = new L.Popup();
	netpopup.setLatLng(new L.LatLng(net['lat'], net['lon']));
	var content = '';
	content += "<b><span class='"+ (net['adhoc']?'adhoc':'') +"'>"+net['ssid']+"</span></b><br /><br />";
	content += "BSSID: <b>"+net['bssid']+"</b><br />";
	content += "Encryption: <b>"+net['encryption']+"</b><br />";
	content += "Channel: <b>"+net['channel']+" ("+net['frequency']+" MHz)</b><br />";
	content += "Level: <b>"+net['level']+" dB</b><br />";
	content += "Date: <b>"+net['timestamp']+"</b><br />";
	content += "Uploader: <b>"+net['scanned_by']+"</b><br />";
	if(net['hacked'] == 'YES') {
		content += "<br />Hacked: <b>"+(net['hacked_by']?net['hacked_by']:net['hacked'])+"</b>";
	}
	if(net['psk']) {
		content += "<br />PSK: <b>"+net['psk']+"</b>";
	}
	if(net['comment']) {
		content += "<br /><br /><pre>"+net['comment']+"</pre>";
	}
	netpopup.setContent(content);
	netpopup.options.offset.y = -26
	if(center) {
		map.setView(new L.LatLng(net['lat'], net['lon']), map.getZoom());
	}
	map.openPopup(netpopup);
}

var sidetab = 'uplist';
function switch_sidetab(tabname) {
	document.getElementById('netlist').style.display = 'none';
	document.getElementById('uplist').style.display = 'none';
	document.getElementById('cpoint').style.display = 'none';
	document.getElementById('current_upload').style.display = 'none';
	document.getElementById('hideopt').style.display = 'none';
	document.getElementById(tabname).style.display = 'block';
	if(tabname == 'netlist') {
		document.getElementById('cpoint').style.display = 'inline';
		document.getElementById('current_upload').style.display = 'inline';
	}
	else {
		document.getElementById('hideopt').style.display = 'inline-block';
	}
	sidetab = tabname;
}

var chtml = '';
var networks;
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
				uhtml += upload['netcount'] + " new Networks<br />";
				uhtml += "<a href='/files/" + upload['filename'] + "' title='" + upload['filename'] + "'>" + upload['filename'].replace('wardrive', 'w&hellip;e')  + "</a>";
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
							var j = 0;
							var nhtml = "<table class='nettbl'>";
							for(var i = 0 ; i < networks.length ; i++) {
								cycle = (j++ % 2)?'odd':'even';
								var net = networks[i];
								nhtml += "<tr class='" + cycle + "'>";
								nhtml += "<td class='ssid'><span class='link"+ (net['adhoc']?' adhoc':'') +"' title='" + net['ssid'] + (net['adhoc']?' [ad-hoc]':'') + "' onclick='display_network(networks["+i+"], true);'>" + net['ssid'].trunc(20) + "</span></td>";
								nhtml += "<td class='enc " + net['encryption'] + "'>" + net['encryption'] + "</td>";
								nhtml += "</tr>";
							}
							nhtml += "</table>";
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

// old onlayerchange function - left for reference
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
