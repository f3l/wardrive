#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ['Wardrive', 'findpos']

import os
from . import findpos
from datetime import datetime

class Wardrive:
	def __init__(self, configfile='wardrive.cfg'):
		from configobj import ConfigObj
		self.config = ConfigObj(configfile)
		from . import networks
		self.networks = networks.Networks(self.config['mysql'])
		from . import uploads
		self.uploads = uploads.Uploads(self.config['mysql'])

	def upload(self, filename, user='anonymous', timestamp=datetime.now(), comment=None):
		upload = {
			'filename': os.path.basename(filename),
			'uploader': user,
			'timestamp': timestamp
		}
		if isinstance(comment, str):
			upload['comment'] = comment
		upload_id = self.uploads.add(upload)
		return {
			'networks': self.networks.importKML(filename, user, upload_id),
			'upload_id': upload_id
		}
