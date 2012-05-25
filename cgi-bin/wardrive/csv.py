#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from io_details import *

def dump(netlist):
	""" Takes poi list, returns (wardriving-forum.de export) csv
	"""
	csv = ""
	for network in netlist:
		csv += ";".join([
			network['ssid'],
			network['bssid'],
			network['encryption'],
			str(network['lat']),
			str(network['lon']),
		])+";\n"
	return csv.encode("utf-8")

def parse(netlist):
	""" NOT IMPLEMENTED
	"""
	raise
