import os, sys
from core.PluginManager import _Plugin

class client(_Plugin):


	def get_name(self):
		return self.name

	def get_test(self):
		return "Hallo World"
	
	def start(self):
		print "dmx starts"
		return