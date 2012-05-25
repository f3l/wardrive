#!/usr/bin/env python

import cgi, os, sys
import cgitb; cgitb.enable()
from wardrive import networks

http_header = "Content-type: text/html\n\n"

asdil12 = int(networks.get({'scanned_by': 'asdil12'}).count())
asdil1991 = int(networks.get({'scanned_by': 'asdil1991'}).count())
the_king4 = int(networks.get({'scanned_by': 'the_king4'}).count())
streber11 = int(networks.get({'scanned_by': 'streber11'}).count())
fillius = int(networks.get({'scanned_by': 'fillius'}).count())
 
print http_header
print "<title>F3L W-LAN Database</title>"
print "<fieldset style='width: 300px;'>"
print "<legend>F3L W-LAN Database</legend>"
print "<center>"
print """
	<table style="font-family: monospace;">
		<tr><td>asdil12</td><td>%d</td></tr>
		<tr><td>asdil1991</td><td>%d</td></tr>
		<tr><td>fillius</td><td>%d</td></tr>
		<tr><td>streber11</td><td>%d</td></tr>
		<tr><td>the_king4</td><td>%d</td></tr>
	</table>
""" % (asdil12,asdil1991,fillius,streber11,the_king4)
print "<a href='/'>Index</a>"
print "</center>"
print "</fieldset>"
