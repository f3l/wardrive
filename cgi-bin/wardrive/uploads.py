#!/usr/bin/env python
# -*- coding: utf-8 -*-

import native_db, os, mysql.connector.errors

class Uploads:
	def __init__(self, mysql_config):
		self._mysql_db = native_db.Server(**mysql_config['server']).database(mysql_config['database'])
		self._upload_table = self._mysql_db.table(mysql_config['upload_table'])

	def add(self, upload):
		"""Add upload using dict
		Return the id of the added upload.
		"""
		return self._upload_table.insert(upload)

	def delete(self, cond):
		"""Delete uploads
		Return the number of deleted uploads.
		"""
		upcount_delta = int(self._upload_table.find(cond).count())
		self._upload_table.delete(cond)
		return upcount_delta

	def update(self, cond, newvals):
		"""Update upload(s)
		Return the number of updated uploads.
		"""
		upcount_delta = int(self._upload_table.find(cond).count())
		self._upload_table.update(cond, newvals)
		return upcount_delta

	def get(self, cond={}, fields=["*"], index=False):
		"""Get uploads from database
		Return list of upload dicts
		"""
		upfind = self._upload_table.find(cond, fields)
		if index:
			return [ up for up in upfind ]
		else:
			return upfind
