#!/usr/bin/env python
# -*- coding: utf-8 -*-

import native_db, os, mysql.connector.errors
from . import kml, geojson, csv

class Networks:
	def __init__(self, mysql_config):
		self._mysql_db = native_db.Server(**mysql_config['server']).database(mysql_config['database'])
		self._network_table = self._mysql_db.table(mysql_config['network_table'])

	def add(self, network):
		"""Add network using dict
		"""
		self._network_table.insert(network)

	def delete(self, cond):
		"""Delete networks
		Return the number of deleted networks.
		"""
		netcount_delta = int(self._network_table.find(cond).count())
		self._network_table.delete(cond)
		return netcount_delta

	def update(self, cond, newvals):
		"""Update network(s)
		Return the number of updated networks.
		"""
		netcount_delta = int(self._network_table.find(cond).count())
		self._network_table.update(cond, newvals)
		return netcount_delta

	def get(self, cond={}, fields=["*"], index=False):
		"""Get networks from database
		Return list of network dicts
		"""
		netfind = self._network_table.find(cond, fields)
		if index:
			return [ net for net in netfind ]
		else:
			return netfind

	def getNear(self, lat, lon, dist=10, limit=1, index=False):
		"""Get networks from database
		Return list of network dicts
		"""
		netfind = self._mysql_db.call('geodist', (lat, lon, dist, limit))
		if index:
			return [ net for net in netfind ]
		else:
			return netfind

	def importNetlist(self, netlist):
		"""Add networks using list of dicts
		Return the number of added networks.
		"""
		netcount_old = int(self._network_table.find({}).count())
		netcount_delta = 0
		for network in netlist:
			try:
				self.add(network)
			except mysql.connector.errors.IntegrityError as e:
				# Skip duplicate entries
				try:
					# Update position if better signal
					old_conflict_item = self.get(cond={'bssid': network['bssid']}, fields=['level'], index=True).pop()
					if int(network['level']) > old_conflict_item['level']:
						netcount_delta += self.update(cond={'bssid': network['bssid']}, newvals=network)
				except:
					pass
				if e.errno == 1062:
					pass
				else:
					raise
		netcount_new = int(self._network_table.find({}).count())
		return {'imported': (netcount_new - netcount_old), 'updated': netcount_delta}

	def importKML(self, kmlfile, user='anonymous', upload_id=None):
		"""Import KML file into the Database.
		Return the number of added networks.
		"""
		netlist = []
		for network in kml.parse(open(kmlfile, 'r').read()):
			network['scanned_by'] = user
			if isinstance(upload_id, int):
				network['upload_id'] = upload_id
			netlist.append(network)
		return self.importNetlist(netlist)

	def exportKML(self, kmlfile, cond={}):
		"""Export KML file from the Database.
		Return the number of exported networks.
		"""
		netlist = self.get(cond, index=True)
		open(kmlfile, 'w').write(kml.dump(netlist))
		return len(netlist)

	def exportJSON(self, jsonfile, cond={}, prefix=""):
		"""Export JSON file from the Database.
		Return the number of exported networks.
		"""
		netlist = self.get(cond, index=True)
		open(jsonfile, 'w').write(prefix+geojson.dump(netlist))
		return len(netlist)

	def exportCSV(self, csvfile, cond={}):
		"""Export CSV file from the Database.
		Return the number of exported networks.
		"""
		netlist = self.get(cond, index=True)
		open(csvfile, 'w').write(csv.dump(netlist))
		return len(netlist)
