#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from io_details import *

def dump(netlist):
	""" Takes poi list, returns geoJSON-string
	"""
	jlist = {"type": "FeatureCollection", "features": []}
	for network in netlist:
		jlist['features'].append({
			"type": "Feature",
			"geometry": {
				"type": "Point",
				"coordinates": [
					network['lon'],
					network['lat']
				]
			},
			"properties": {
				"name": network['ssid'],
				"popupContent": createDescription(network, viewssid=True)
			}
		})
	return json.dumps(jlist)

def parse(netlist):
	""" NOT IMPLEMENTED
	"""
	raise
