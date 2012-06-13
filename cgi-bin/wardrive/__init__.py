#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ["Wardrive"]

class Wardrive:
	def __init__(self, configfile='wardrive.cfg'):
		from configobj import ConfigObj
		self.config = ConfigObj(configfile)
		from . import networks
		self.networks = networks.Networks(self.config['mysql'])
