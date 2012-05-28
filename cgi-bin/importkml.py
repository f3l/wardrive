#!/usr/bin/python

import sys
from wardrive import networks

username = sys.argv[1].split('-')[1]
print "Importing '%s' as '%s'" % (sys.argv[1], username)
print "--> Imported: %(imported)d - Updated: %(updated)d" % networks.importKML(sys.argv[1], username)
