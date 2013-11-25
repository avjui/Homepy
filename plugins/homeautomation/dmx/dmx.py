#
# -*- coding: <utf-8> -*-
#

import os
import sys

from core.PluginManager import Homeautomation


class DMX(Homeautomation):

	name = 'DMX'
	type = 'homeautomation'
	config = [{
    		   'name': 'automation',
		   'order': 102,
		  }]

	def get_name(self):
		return self.name

	def get_test(self):
		return "Hallo World"
	