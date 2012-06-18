#!/usr/bin/python

import sys
from wardrive import Wardrive

wardrive = Wardrive('../wardrive.cfg')
networks = wardrive.networks

networks.exportKML("../htdocs/db/all.kml")
networks.exportKML("../htdocs/db/wpa.kml", {'encryption': 'WPA'})
networks.exportKML("../htdocs/db/ibss.kml", {'encryption': 'IBSS'})
networks.exportKML("../htdocs/db/wep.kml", {'encryption': 'WEP'})
networks.exportKML("../htdocs/db/open.kml", {'encryption': 'OPEN'})
