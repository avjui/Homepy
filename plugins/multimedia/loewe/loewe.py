#
# -*- coding: <utf-8> -*-
#

import os
import sys

from core.PluginManager import Multimedia

class Loewe(Multimedia):

	name = 'Loewe'
	type = 'multimedia'
	config = {
  		    'main_page': 'loewe.html',
		    'config_page': 'config_loewe.html',
		  }

	def get_name(self):
		return self.name

	def get_test(self):
		return "Hallo World"
	