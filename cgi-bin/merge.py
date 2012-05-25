#!/usr/bin/env python

import xml.sax, xml.dom.minidom, re, argparse, errno, json

# remember to use xml.etree for xml-creation next time...

mac_addr = re.compile(r"([a-fA-F0-9]{2}[:|\-]?){6}")
enc_wep = re.compile(r"WEP", re.I)
enc_wpa = re.compile(r"WPA", re.I)
enc_wps = re.compile(r"WPS", re.I)
enc_ibss = re.compile(r"IBSS", re.I)
 
class NetworkHandler(xml.sax.handler.ContentHandler):
	def __init__(self, mapping = {}):
		self.inName = 0
		self.inDesc = 0
		self.inCoor = 0
		# dict = object -> reference
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
			self.name = self.buffer.replace("\n", "").strip()
			self.inName = 0
		elif name == "description":
			try:
				self.description = self.buffer.replace("\n", "").strip()
				mac = mac_addr.search(self.description)
				self.bssid = self.description[mac.start():mac.end()].lower()
				if enc_wpa.search(self.description):
					self.encryption = "WPA"
				elif enc_wep.search(self.description):
					self.encryption = "WEP"
				elif enc_wps.search(self.description):
					self.encryption = "WPS"
				elif enc_ibss.search(self.description):
					self.encryption = "IBSS"
				else:
					self.encryption = "OPEN"
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
			self.mapping[self.bssid] = {"name": self.name, "description": self.description, "lon": self.lon, "lat": self.lat, "height": self.height, "encryption": self.encryption}

def make_kml(netlist, args):
	doc = xml.dom.minidom.Document()

	# KML Tag
	kml = doc.createElement("kml")
	kml.setAttribute("xmlns", "http://www.opengis.net/kml/2.2")
	doc.appendChild(kml)

	# Document Tag
	kmldoc = doc.createElement("Document")
	kml.appendChild(kmldoc)

	# Styles
	iconimgs = {'red': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
						'yellow': 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
						'green': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'}
	encryptstyles = {'WPA': 'red', 'WPS': 'red', 'IBSS': 'red', 'WEP': 'yellow', 'OPEN': 'green'}
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
	for bssid in netlist.keys():
		if args.filter and args.filter != netlist[bssid]['encryption']:
			continue
		placemark = doc.createElement("Placemark")
		folder.appendChild(placemark)

		name = doc.createElement("name")
		placemark.appendChild(name)

		if args.output != "-":
			netlist[bssid]['name'] = netlist[bssid]['name'].encode("utf-8")
			netlist[bssid]['description'] = netlist[bssid]['description'].encode("utf-8")
		namecontent = doc.createTextNode(netlist[bssid]['name'])
		name.appendChild(namecontent)

		description = doc.createElement("description")
		placemark.appendChild(description)

		descriptioncontent = doc.createTextNode(netlist[bssid]['description'])
		description.appendChild(descriptioncontent)

		styleurl = doc.createElement("styleUrl")
		placemark.appendChild(styleurl)

		styleurlcontent = doc.createTextNode("#%s" % encryptstyles[netlist[bssid]['encryption']])
		styleurl.appendChild(styleurlcontent)

		point = doc.createElement("Point")
		placemark.appendChild(point)

		coordinates = doc.createElement("coordinates")
		point.appendChild(coordinates)

		coordinatescontent = doc.createTextNode("%(lon)s,%(lat)s,%(height)s" % netlist[bssid])
		coordinates.appendChild(coordinatescontent)

	if args.output == "-":
		print doc.toprettyxml(indent="    ", encoding="UTF-8")
	else:
		fp = open(args.output, 'w')
		doc.writexml(fp, encoding="UTF-8", indent="", addindent="	", newl="\n")
		fp.close()

def main():
	parser = argparse.ArgumentParser(description='This tool helps you to merge multiple kml files. If - is used as OUTPUT, kml will be printed to standard output.')
	parser.add_argument('input', metavar='KML', nargs="+", help='Files to be merged')
	parser.add_argument('-f', dest='filter', metavar='ENCRYPTION', help='Filter by encryption (OPEN/WEP/WPA/WPS/IBSS)')
	parser.add_argument('-o', dest='output', default='-', metavar='OUTPUT', help='File to save merged kml')
	args = parser.parse_args()

	netlist = {}
	handler = NetworkHandler(netlist)
	parser = xml.sax.make_parser()
	parser.setContentHandler(handler)

	for kmlfile in args.input:
		parser.parse(kmlfile)

	make_kml(netlist, args)

def jsonDump(kml_input, json_output="-"):
	netlist = {}
	handler = NetworkHandler(netlist)
	parser = xml.sax.make_parser()
	parser.setContentHandler(handler)

	for kmlfile in kml_input:
		parser.parse(kmlfile)

	if json_output != "-":
		json.dump(netlist, open(json_output, "w"))
	else:
		print json.dumps(netlist)
	return len(netlist)

def xmlDump(json_input, xml_output="-", enc_filter=""):
	class Args:
		def __init__(self, output, enc_filter):
			self.output = output
			self.filter = enc_filter
	args = Args(output=xml_output, enc_filter=enc_filter)
	netlist = json.load(open(json_input, "r"))
	make_kml(netlist, args)
	return len(netlist)
	
if __name__ == "__main__":
	try:
		main()
	except IOError, e:
		if e.errno != errno.EPIPE:
			raise
