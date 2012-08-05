#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.sax, xml.dom.minidom, datetime
from wardrive.io_details import *

# remember to use xpath for xml-creation next time...

class NetworkHandler(xml.sax.handler.ContentHandler):
	def __init__(self, mapping = []):
		self.inName = 0
		self.inDesc = 0
		self.inCoor = 0
		# list = object -> reference
		self.mapping = mapping

	def startElement(self, name, attributes):
		self.buffer = ""
		if name == "name":
			self.inName = 1
		elif name == "description":
			self.inDesc = 1
		elif name == "coordinates":
			self.inCoor = 1
		elif name == "Placemark":
			self.invalidNetwork = False

	def characters(self, data):
		if self.inName or self.inDesc or self.inCoor:
			self.buffer += data

	def endElement(self, name):
		if name == "name":
			self.ssid = self.buffer.replace("\n", "").strip()
			self.inName = 0
		elif name == "description":
			try:
				self.description = self.buffer.replace("\n", "").strip()
				mac = mac_addr.search(self.description)

				self.bssid = self.description[mac.start():mac.end()].lower()

				level = wlan_level.search(self.description)
				self.level = self.description[level.start():level.end()]

				ts = timestamp.search(self.description)
				self.timestamp = int(self.description[ts.start():ts.end()])
				# Fix unix/micro timestamp joined without decimal point
				# This fix will not work after Sun, 26 Dec 4821 16:00 GMT
				if self.timestamp > 90000000000:
					self.timestamp /= 1000
				self.timestamp = datetime.datetime.fromtimestamp(self.timestamp)

				if enc_wpa.search(self.description):
					self.encryption = "WPA"
				elif enc_wep.search(self.description):
					self.encryption = "WEP"
				elif enc_wps.search(self.description):
					self.encryption = "WPS"
				else:
					self.encryption = "OPEN"

				self.adhoc = True if mode_ibss.search(self.description) else False

				self.channel = 0
				for freq in wlan_chan.keys():
					if freq in self.description:
						self.channel = wlan_chan[freq]
						break
			except:
				self.invalidNetwork = True
			finally:
				self.inDesc = 0
		elif name == "coordinates":
			try:
				self.lon, self.lat, self.height = self.buffer.replace("\n", "").strip().split(',')
			except:
				self.invalidNetwork = True
			finally:
				self.inCoor = 0
		elif name == "Placemark" and not self.invalidNetwork:
			self.mapping.append({"bssid": self.bssid, "ssid": self.ssid, "lon": self.lon, "lat": self.lat, "height": self.height, "encryption": self.encryption, "adhoc": self.adhoc, "channel": self.channel, "level": self.level, "timestamp": self.timestamp})


def parse(kml_input):
	""" Parses a kml-string, returns poi list
	"""
	netlist = []
	handler = NetworkHandler(netlist)
	xml.sax.parseString(kml_input, handler)
	return netlist

def dump(netlist):
	""" Takes poi list, returns kml-string
	"""
	doc = xml.dom.minidom.Document()

	# KML Tag
	kml = doc.createElement("kml")
	kml.setAttribute("xmlns", "http://www.opengis.net/kml/2.2")
	doc.appendChild(kml)

	# Document Tag
	kmldoc = doc.createElement("Document")
	kml.appendChild(kmldoc)

	# Styles
	for iconcolor in iconimgs.keys():
		style = doc.createElement("Style")
		style.setAttribute("id", iconcolor)
		kmldoc.appendChild(style)

		iconstyle = doc.createElement("IconStyle")
		style.appendChild(iconstyle)

		icon = doc.createElement("Icon")
		iconstyle.appendChild(icon)

		href = doc.createElement("href")
		icon.appendChild(href)

		hrefcontent = doc.createTextNode(iconimgs[iconcolor])
		href.appendChild(hrefcontent)

	# Folder
	folder = doc.createElement("Folder")
	kmldoc.appendChild(folder)

	foldername = doc.createElement("name")
	folder.appendChild(foldername)

	foldernamecontent = doc.createTextNode("Network List")
	foldername.appendChild(foldernamecontent)

	# Placemarks
	for network in netlist:
		placemark = doc.createElement("Placemark")
		folder.appendChild(placemark)

		name = doc.createElement("name")
		placemark.appendChild(name)

		#FIXME: network['name'] = network['name'].encode("utf-8")
		namecontent = doc.createTextNode(network['ssid'])
		name.appendChild(namecontent)

		description = doc.createElement("description")
		placemark.appendChild(description)

		descriptioncontent = doc.createTextNode(createDescriptionLite(network))
		description.appendChild(descriptioncontent)

		styleurl = doc.createElement("styleUrl")
		placemark.appendChild(styleurl)

		styleurlcontent = doc.createTextNode("#%s" % encryptstyles[network['encryption']])
		styleurl.appendChild(styleurlcontent)

		point = doc.createElement("Point")
		placemark.appendChild(point)

		coordinates = doc.createElement("coordinates")
		point.appendChild(coordinates)

		coordinatescontent = doc.createTextNode("%(lon)s,%(lat)s,%(height)s" % network)
		coordinates.appendChild(coordinatescontent)

	return doc.toxml(encoding="UTF-8")
