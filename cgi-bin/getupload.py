#!/usr/bin/env python

import cgi, os, sys
import cgitb; cgitb.enable()
from wardrive import Wardrive
from wardrive.io_details import *
import json

wardrive = Wardrive('../wardrive.cfg')
uploads = wardrive.uploads

http_header = "Content-type: application/json\n"

form = cgi.FieldStorage()

mode = form.getvalue('mode', None)
# comment(like) id list

if not mode:
	print "Content-type: text/plain\n"
	print "Invalid mode"
	sys.exit()

uplist = []

if mode == 'list':
	# fixme: use limit, paging...

	uplist_raw = uploads.get().sort({'id': 1}, reverse=True)

	for upload in uplist_raw:
		uplist.append({
			'id': upload['id'],
			'date': timestring(upload['timestamp'], 2),
			'uploader': upload['uploader'],
			'filename': upload['filename'],
			'netcount': upload['netcount'],
			'comment': upload['comment']
		})
elif mode == 'id':
	qid = int(form.getvalue('id'))

	uplist_raw = uploads.get({'id': qid})

	for upload in uplist_raw:
		uplist.append({
			'id': upload['id'],
			'date': timestring(upload['timestamp'], 2),
			'uploader': upload['uploader'],
			'filename': upload['filename'],
			'netcount': upload['netcount'],
			'comment': upload['comment']
		})

print http_header
print json.dumps({'uploads': uplist})
