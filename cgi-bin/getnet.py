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

mode = form.getvalue('mode', None)
# search (bssid) near upload

if not mode:
	print "Content-type: text/plain\n"
	print "Invalid mode"
	sys.exit()

netlist = []

if mode == 'near':
	lat = float(form.getvalue('lat'))
	lon = float(form.getvalue('lon'))
	dist = float(form.getvalue('dist', 10))
	limit = int(form.getvalue('limit', 1))

	netlist_raw = networks.getNear(lat, lon, dist, limit)

	for network in netlist_raw:
		network['timestamp'] = timestring(network['timestamp'])
		network['frequency'] = wlan_freq[network['channel']]
		netlist.append(network)
elif mode == 'upload':
	upload = int(form.getvalue('upload'))

	netlist_raw = networks.get({'upload_id': upload})

	for network in netlist_raw:
		network['timestamp'] = timestring(network['timestamp'])
		network['frequency'] = wlan_freq[network['channel']]
		netlist.append(network)

print http_header
print json.dumps({'networks': netlist})
