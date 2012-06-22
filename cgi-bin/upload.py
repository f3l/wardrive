#!/usr/bin/env python

import cgi, os, sys
import shutil
from time import time
import cgitb; cgitb.enable()
from wardrive import Wardrive

wardrive = Wardrive('../wardrive.cfg')
networks = wardrive.networks

http_header = "Content-type: text/html\n\n"

try: # Windows needs stdio set for binary mode.
    import msvcrt
    msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
    msvcrt.setmode (1, os.O_BINARY) # stdout = 1
except ImportError:
	pass

form = cgi.FieldStorage()

# Generator to buffer file chunks
def fbuffer(f, chunk_size=10000):
	while True:
		chunk = f.read(chunk_size)
		if not chunk: break
		yield chunk

outp = False
      
if os.environ['REQUEST_METHOD'] == 'POST':
	try:
		# A nested FieldStorage instance holds the file
		fileitem = form['file']

		# Test if the file was uploaded
		if fileitem.filename:
			# strip leading path from file name to avoid directory traversal attacks
			fn, fx = os.path.splitext(os.path.basename(fileitem.filename).replace(' ', '_'))
			if fx not in ['.xml', '.kml']:
				raise
			ft = str(time()).split('.')[0]
			fu = os.environ["REMOTE_USER"]
			filename = "%s-%s-%s.kml" % (ft, fu, fn)
			dp = os.path.join('../htdocs/files/', filename)
			f = open(dp, 'wb', 10000)

			# Read the file in chunks
			for chunk in fbuffer(fileitem.file):
				f.write(chunk)
			f.close()
			if not os.path.getsize(dp):
				os.remove(dp)
				print http_header
				print "<title>F3L W-LAN Database</title>"
				print "<fieldset style='width: 300px;'>"
				print "<legend>F3L W-LAN Database</legend>"
				print "<center>"
				print "ERROR<br /><br />"
				print "Empty File"
				print "<br /><br />"
				print "<a href='/'>Index</a>"
				print "</center>"
				print "</fieldset>"
				outp = True
				raise
			url = '/files/%s' % filename
			# Rebuild Database
			#nc = merge.jsonDump(kml_input=inlist, json_output="../htdocs/all.json")
			impc = wardrive.upload(dp, user=fu)['networks']
			nc = int(networks.get().count())
			open("../htdocs/db/count.txt", "w").write(str(nc))
			#merge.xmlDump(json_input="../htdocs/all.json", xml_output="../htdocs/all.kml")
			#merge.xmlDump(json_input="../htdocs/all.json", xml_output="../htdocs/wep.kml", enc_filter="WEP")
			#merge.xmlDump(json_input="../htdocs/all.json", xml_output="../htdocs/open.kml", enc_filter="OPEN")
			networks.exportKML("../htdocs/db/all.kml")
			networks.exportKML("../htdocs/db/wpa.kml", {'encryption': 'WPA'})
			networks.exportKML("../htdocs/db/ibss.kml", {'encryption': 'IBSS'})
			networks.exportKML("../htdocs/db/wep.kml", {'encryption': 'WEP'})
			networks.exportKML("../htdocs/db/open.kml", {'encryption': 'OPEN'})
			# clear cache
			for enct in ['all', 'wpa', 'wep', 'open']:
				shutil.rmtree(os.path.join(wardrive.config['tiles']['cache_path'], enct), ignore_errors=True)
			# trigger tileserver kml reload
			for enct in ['all', 'wpa', 'wep', 'open']:
				os.utime('../tilelite/mapfiles/%s.xml' % enct, None)
			print http_header
			print "<title>F3L W-LAN Database</title>"
			print "<fieldset style='width: 300px;'>"
			print "<legend>F3L W-LAN Database</legend>"
			print "<center>"
			print "UPLOAD DONE:<br /><br /> <a href='%s'>%s</a>" % (url, filename)
			print "<br /><br />"
			print "%d Networks imported.<br />" % impc['imported']
			print "%d Networks updated." % impc['updated']
			print "<br /><br />"
			print "<a href='/'>Index</a>"
			print "</center>"
			print "</fieldset>"
			outp = True
		else:
			print http_header
			print "<title>F3L W-LAN Database</title>"
			print "<fieldset style='width: 300px;'>"
			print "<legend>F3L W-LAN Database</legend>"
			print "<center>"
			print "ERROR"
			print "<br /><br />"
			print "<a href='/'>Index</a>"
			print "</center>"
			print "</fieldset>"
			outp = True
	except:
		raise
		if not outp:
			print "Location: http://%s/\n\n" % os.environ['SERVER_NAME']
else:
	print "Location: http://%s/\n\n" % os.environ['SERVER_NAME']
