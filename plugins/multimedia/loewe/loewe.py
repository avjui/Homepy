#
# -*- coding: <utf-8> -*-
#

import os
import sys

from core.PluginManager import Homeautomation

class client(Homeautomation):

	name = 'Loewe'
	type = 'homeautomation'
	config = [{
  		    'name': 'automation',
		    'order': 103,
		  }]

	def get_name(self):
		return self.name

	def get_test(self):
		return "Hallo World"
	