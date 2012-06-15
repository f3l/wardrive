#!/usr/bin/env python

import cgi, os, sys
import cgitb; cgitb.enable()
from wardrive import Wardrive
from wardrive.io_details import *
import json

wardrive = Wardrive('../wardrive.cfg')
networks = wardrive.networks

http_header = "Content-type: application/json\n"

form = cgi.FieldStorage()

lat = float(form.getvalue('lat'))
lon = float(form.getvalue('lon'))
dist = int(form.getvalue('dist', 10))
limit = int(form.getvalue('limit', 1))

netlist = []

for network in networks.getNear(lat, lon, dist, limit):
	netlist.append({
		'lat': network['lat'],
		'lon': network['lon'],
		'bssid': network['bssid'],
		'ssid': network['ssid'],
		'description': createDescription(network, viewssid=True)
	})

print http_header
print json.dumps({'networks': netlist})
