#
# -*- coding: <utf-8> -*-
#

import os
import sys

from core.PluginManager import Notification

class Pushover(Notification):

	name = 'Pushover'

	def get_name(self):
		return self.name

	def get_test(self):
		return "Hallo World"
	