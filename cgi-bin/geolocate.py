#!/usr/bin/env python

import cgi, os, sys
import cgitb; cgitb.enable()
from wardrive import *
import json

wardrive = Wardrive('../wardrive.cfg')
networks = wardrive.networks

myaps = []

try:
	"""
	example request:
	{
	"request_address": true,
	"version": "1.1.0",
	"wifi_towers": [
			{
				"mac_address":"00:1a:2a:22:01:23",
				"signal_strength":"-37.00",
				"ssid":"centipedenetworks"
			},
			{
				"mac_address":"00:24:fe:a9:92:b9",
				"signal_strength":"-31.00",
				"ssid":"nateidogg"
			}
		]
	}
	"""
	request = json.load(sys.stdin)

	for ap in request['wifi_towers']:
		myaps.append({
			'mac': ap['mac_address'],
			'signal': int(float(ap['signal_strength']))
		})
	try:
		position = findpos.wifipos(networks, myaps)
		print "Content-type: application/json\n"
		print json.dumps(position)
	except IndexError:
		print "Content-type: text/plain\n"
		print "No Network with known position."
except ValueError:
	print "Content-type: text/plain\n"
	print "JSON parsing error."
