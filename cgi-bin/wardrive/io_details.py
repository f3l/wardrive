#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, datetime

mac_addr = re.compile(r"([a-fA-F0-9]{2}[:|\-]?){6}")
wlan_level = re.compile(r"\-[0-9]{2}")
timestamp = re.compile(r"[0-9]{9}[0-9]+")
enc_wep = re.compile(r"WEP", re.I)
enc_wpa = re.compile(r"WPA", re.I)
enc_wps = re.compile(r"WPS", re.I)
enc_ibss = re.compile(r"IBSS", re.I)
wlan_chan = {"2412": 1,"2417": 2, "2422": 3, "2427": 4, "2432": 5, "2437": 6, "2442": 7, "2447": 8, "2452": 9, "2457": 10, "2462": 11, "2467": 12, "2472": 13, "2484": 14}
wlan_freq = {1: "2412", 2: "2417", 3: "2422", 4: "2427", 5: "2432", 6: "2437", 7: "2442", 8: "2447", 9: "2452", 10: "2457", 11: "2462", 12: "2467", 13: "2472", 14: "2484"}
iconimgs = {'red': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
					'yellow': 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
					'green': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'}
encryptstyles = {'WPA': 'red', 'WPS': 'red', 'IBSS': 'red', 'WEP': 'yellow', 'OPEN': 'green'}

def createDescription(network, viewssid=False):
	return "%(ssid)sBSSID: <b>%(bssid)s</b><br />Encryption: <b>%(encryption)s</b><br />Channel: <b>%(channel)s (%(frequency)s MHz)</b><br />Level: <b>%(level)s dB</b><br />Date: <b>%(date)s</b>%(scanned_by)s%(hacked)s%(internet)s%(private)s%(comment)s" % {
			'ssid': "<b>%s</b><br /><br />" % network['ssid'] if viewssid else "",
			'bssid': network['bssid'],
			'encryption': network['encryption'],
			'channel': str(network['channel']),
			'frequency': wlan_freq[network['channel']],
			'level': network['level'],
			'date': network['timestamp'].strftime('%a %d %b %Y %H:%M:%S'),
			'scanned_by': "<br />Scanned: <b>%s</b>" % network['scanned_by'] if network.has_key('scanned_by') else "",
			'hacked': "<br />Hacked: <b>%s (%s)</b>" % (network['hacked_by'], network['hacked']) if network.get('hacked_by', False) and network.get('hacked', 'NO') != 'NO' else "",
			'internet': "<br />Internet: <b>%s</b>" % network['internet_access'] if network.get('internet_access', 'UNKNOWN') != 'UNKNOWN' else "",
			'private': "<br />Private: <b>%s</b>" % network['private'] if network.get('private', 'UNKNOWN') != 'UNKNOWN' else "",
			'comment': "<br /><br /><pre>%s</pre>" % network['comment'] if network.get('comment', False) else ""}

def createDescriptionLite(network, viewssid=False):
	return "%(bssid)s<br />Enc: <b>%(encryption)s</b><br />CH: <b>%(channel)s</b><br />Lv: <b>%(level)s dB</b><br />Date: <b>%(date)s</b>" % {
			'ssid': "<b>%s</b><br /><br />" % network['ssid'] if viewssid else "",
			'bssid': network['bssid'],
			'encryption': network['encryption'],
			'channel': str(network['channel']),
			'level': network['level'],
			'date': network['timestamp'].strftime('%a %d %b %Y %H:%M:%S')}
