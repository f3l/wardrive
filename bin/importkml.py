#!/usr/bin/python

import sys
import os
from wardrive import Wardrive
from datetime import datetime

wardrive = Wardrive('../wardrive.cfg')

username = sys.argv[1].split('-')[1]
timestamp = datetime.fromtimestamp(int(os.path.basename(sys.argv[1]).split('-')[0]  ))

print "Importing '%s' as '%s' at %s ..." % (sys.argv[1], username, timestamp),
print "--> Imported: %(imported)d - Updated: %(updated)d" % wardrive.upload(sys.argv[1], username, timestamp)['networks']
