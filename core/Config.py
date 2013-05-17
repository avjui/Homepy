#
# -*- coding: <utf-8> -*-
#

import os
import sys

from lib.configobj import ConfigObj

import core
import core.Logger 


class Config(object):


	################################################################################
	# Check_setting_int                                                            #
	################################################################################
	def check_setting_int(self, config, cfg_name, item_name, def_val):
		try:
			self.my_val = int(config[cfg_name][item_name])
		except:
			self.my_val = def_val
		try:
			config[cfg_name][item_name] = self.my_val
		except:
			config[cfg_name] = {}
			config[cfg_name][item_name] = self.my_val
		#log("%s -> %s" %(item_name, my_val), 'debug')
		return self.my_val


	################################################################################
	# Check_setting_str                                                            #
	################################################################################
	def check_setting_str(self, config, cfg_name, item_name, def_val, log=True):
		try:
			self.my_val = config[cfg_name][item_name]
		except:
			self.my_val = def_val
		try:
			config[cfg_name][item_name] = self.my_val
		except:
			config[cfg_name] = {}
			config[cfg_name][item_name] = self.my_val

		#if log:
		#    log(item_name + " -> " + self.my_val, 'debug')
		#else:
		#    log(item_name + " -> ******", 'debug')
		return self.my_val




	def Check(self):

	
		# Make sure all the config sections exist
		core.CFG.get('General', "General")
		core.CFG.get('Syssetting', "Syssetting")

 
		try:
			core.HTTP_PORT = check_setting_int(core.CFG, 'General', 'http_port', 8989)
		except:
			core.HTTP_PORT = 8989
            
		if core.HTTP_PORT < 21 or core.HTTP_PORT > 65535:
			core.HTTP_PORT = 8989
            
		try:
			core.HTTP_HOST = self.check_setting_str(core.CFG, 'General', 'http_host', '0.0.0.0').encode('utf-8')
		except:
			core.HTTP_HOST = '0.0.0.0'
	
		core.HTTP_USERNAME = self.check_setting_str(core.CFG, 'General', 'http_username', '')
		core.HTTP_PASSWORD = self.check_setting_str(core.CFG, 'General', 'http_password', '')

		core.WEB_INTERFACE = self.check_setting_str(core.CFG, 'Syssetting', 'web_interface', '')
		core.ROOMS = self.check_setting_str(core.CFG, 'Syssetting', 'rooms', '')
		core.DEBUG_LOG = bool(self.check_setting_str(core.CFG, 'Syssetting', 'debuglog', 0))
		core.HTTP_ROOT = self.check_setting_str(core.CFG, 'Syssetting', 'root', '')
	


	def Write(self):

		new_config = ConfigObj()
		new_config.filename = core.CONFIG_FILE

		new_config['General'] = {}
		new_config['General']['http_port'] = core.HTTP_PORT
		new_config['General']['http_host'] = core.HTTP_HOST
		new_config['General']['http_username'] = core.HTTP_USERNAME
		new_config['General']['http_password'] = core.HTTP_PASSWORD

		new_config['Syssetting'] = {}
		new_config['Syssetting']['web_interface'] = core.WEB_INTERFACE
		new_config['Syssetting']['rooms'] = core.ROOMS
		new_config['Syssetting']['debug_log'] = core.DEBUG_LOG
		new_config['Syssetting']['root'] = core.HTTP_ROOT
		new_config.write()

