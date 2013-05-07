import os
import sys

from core.PluginManager import Notification

class Pushover(Notification):


	def get_name(self):
		return self.name

	def get_test(self):
		return "Hallo World"
	