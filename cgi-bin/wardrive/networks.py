#!/usr/bin/env python
# -*- coding: utf-8 -*-

import native_db, os, mysql.connector.errors
import kml, geojson, csv
from configobj import ConfigObj

_configfile = 'wardrive.cfg'
_config = ConfigObj(_configfile)

_mysql_db = native_db.Server(**_config['mysql']['server']).database(_config['mysql']['database'])
_network_table = _mysql_db.table(_config['mysql']['network_table'])

def add(network):
	"""Add network using dict
	"""
	_network_table.insert(network)

def delete(cond):
	"""Delete networks
	Return the number of deleted networks.
	"""
	netcount_delta = int(_network_table.find(cond).count())
	_network_table.delete(cond)
	return netcount_delta

def update(cond, newvals):
	"""Update network(s)
	Return the number of updated networks.
	"""
	netcount_delta = int(_network_table.find(cond).count())
	_network_table.update(conds, newvals)
	return netcount_delta

def get(cond={}, fields=["*"], index=False):
	"""Get networks from database
	Return list of network dicts
	"""
	netfind = _network_table.find(cond, fields)
	if index:
		return [ net for net in netfind ]
	else:
		return netfind

def importNetlist(netlist):
	"""Add networks using list of dicts
	Return the number of added networks.
	"""
	netcount_old = int(_network_table.find({}).count())
	for network in netlist:
		try:
			add(network)
		except mysql.connector.errors.IntegrityError as e:
			# Skip duplicate entries
			if e.errno == 1062:
				pass
			else:
				raise
	netcount_new = int(_network_table.find({}).count())
	return netcount_new - netcount_old

def importKML(kmlfile, user='anonymous'):
	"""Import KML file into the Database.
	Return the number of added networks.
	"""
	netlist = []
	for network in kml.parse(open(kmlfile, 'r').read()):
		network['scanned_by'] = user
		netlist.append(network)
	return importNetlist(netlist)

def exportKML(kmlfile, cond={}):
	"""Export KML file from the Database.
	Return the number of exported networks.
	"""
	netlist = get(cond, index=True)
	open(kmlfile, 'w').write(kml.dump(netlist))
	return len(netlist)

def exportJSON(jsonfile, cond={}, prefix=""):
	"""Export JSON file from the Database.
	Return the number of exported networks.
	"""
	netlist = get(cond, index=True)
	open(jsonfile, 'w').write(prefix+geojson.dump(netlist))
	return len(netlist)

def exportCSV(csvfile, cond={}):
	"""Export CSV file from the Database.
	Return the number of exported networks.
	"""
	netlist = get(cond, index=True)
	open(csvfile, 'w').write(csv.dump(netlist))
	return len(netlist)
