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

	example result:
	{
		"location": {
			"latitude":49.45052,
			"longitude":11.08048,
			"address":{
				"country":"Germany",
				"country_code":"DE",
				"region":"Bavaria",
				"county":"Middle Franconia",
				"city":"Nuremberg",
				"street":"Lorenzer Platz",
				"street_number":"13",
				"postal_code":"90402"
			},
			"accuracy":18000.0
		},
		"access_token":"2:D2vkFN8VlR24wTIS:1RtMbpIlp3OqwR1o"
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
		result = {
			'location': {
				'latitude': position['lat'],
				'longitude': position['lon'],
				'accuracy': float(150 - position['netcount'] * 30)
			}
		}
		if request.get('request_address', False):
			#FIXME: perform geolocation, somehow
			pass
		print "Content-type: application/json\n"
		print json.dumps(result)
	except IndexError:
		print "Content-type: text/plain\n"
		print "No Network with known position."
except ValueError:
	print "Content-type: text/plain\n"
	print "JSON parsing error."
