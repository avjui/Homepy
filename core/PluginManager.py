#
# -*- coding: <utf-8> -*-
#

import os
import sys

from core.DBFunctions import DBFunction
from core.Logger import log


'''
Code base on code from http://yannik520.github.io/python_plugin_framework.html
'''

class _Plugin(object):
     
     class __metaclass__(type):
        def __init__(cls,name, bases, attrs):
            if not hasattr(cls, 'plugins'):
                cls.plugins = {}
            else:
                if attrs['__module__'] != 'core.PluginManager':
                     modul = attrs['__module__'].upper()
                     # will be added later
                     #try:
                         # will be added later
                     #    self.config = attrs['config']	
                     #except:
                     #    log("No config found for %s plugin "% (modul), 'info')
                     cls.plugins[modul] = cls


        def get_plugins(cls):
            return cls.plugins


class PluginMgr(object):

    plugin_dirs = { }
    adding = True

    # make the manager class as singleton
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PluginMgr, cls).__new__(cls, *args, **kwargs)

        return cls._instance
    def __init__(self):

        self.plugin_dirs.update({
                                 'plugins/homeautomation/' : False,
                                 'plugins/multimedia/' : False,
                                 'plugins/notification' : False,
                                 'plugins/web/' : False,
                                 })

    def _load_all(self):
        for (pdir, loaded) in self.plugin_dirs.iteritems():
            if loaded: continue

            for root,dirs,mod in os.walk(pdir):
                sys.path.insert(0, root)            
                for mod in [x[:-3] for x in os.listdir(root) if x.endswith('.py')]:
                    if mod and mod != '__init__':
                        if mod in sys.modules:
                            log('Module %s already exists, skip' % mod, 'info')
                        else:
                            try:
                                pymod = __import__(mod)
                                splitted = mod.split('.')
                                self.plugin_dirs[pdir] = True
                                log("Plugin Found [Name] %s	[Path] %s"% (mod, pymod.__file__), 'info')
                                self.plugins = DBFunction().GetList('plugins')
                                for p in self.plugins:
                                     if p[1] == mod.upper():
                                        self.adding = False
                                        break
                                     else:
                                       self.adding = True

                                if self.adding:
                                     DBFunction().AddPlugin(mod.upper(), pymod.__file__.split('/')[1])
                            except ImportError, e:
                                log ('Loading failed, skip plugin %s/%s' % (os.path.basename(root), mod), 'error')

                del(sys.path[0])


    def get_plugins(self):
        """ the return value is dict of name:class pairs """
        self._load_all()
        return _Plugin.get_plugins()


class Homeautomation(_Plugin):

 	def start(self):
		"""	
		This function will be call at start.
		With this function you can call startups for example start
		a eventserver or same other backgroundprocesses 
		"""
		return


	def add(self, serial):
		"""  	This function will be call to add a devices		
		
			@param serial               serialnummber of device
			
			There shoud be return a dict with following key's

			deviceseriel         serialnummber of device or list of devices
			devicename           can by the industrial name of the device
			devicetype           type of device ex. SWITCH

		"""

		self.data = [{ 
				'deviceserial' : '',
				'config' : [
				{
					'devicename' : ' ',
					'devicetype' : ' ',
					}]
				}]
		return self.data


	def remove(self):
		"""
		This function will remove the device
	
		@param deviceseriel                serialnummber of device
		"""	
		return True


	def switch(self):
		"""	
		This function will be toggle the device

		@param deviceserial                serialnumber of device
		"""
		return True


	def dimm(self):
		"""	
		This function will set device to a special value
		
		@param deviceserial                serialnumber of device
		@param value                       value
		@param t                           time to dimm
		"""
		return True


	def status(self):
		""" 
		Will return the status of all devices in a dict
		If there is give serialnumbers in a list it will return only the the status of this devices
	
		@param	devicelist                  list with serialnumbers of devices
		"""
		self.devices = {}
		return self.device

	def shutdown(self):
		"""
		This function will be call at shutdown.
		It can be used to stop a eventserver 
		or same other backgroundprocesses 
		"""
		return True


class Multimedia(_Plugin):

 	def start(self):
		"""
		This function will be call at start.
		With this function you can call startups for example start
		a eventserver or same other backgroundprocesses 
		"""
		return

	def action(self, ip, a):
		"""
		@param ip                          ip of device
		@param a                           valid action are (play, stop, pause, forrword, rewind, volume)
		@param value                       e.x. for volume 
		"""

		return True

	def add(self):
		return True

	def remove(self):
		return True

	def get_mediainfo(self):
		""" This function return a dict with media informations
		    This dict must contain few things

		    First mediatyp : 'audio' or 'video'

		    For audio
			interpret :
		       album :
			title :
			cover :
			duration :
			position: 
			volume :

		   For video
			title :
			descritpion :
			cover :
			duration :
			position: 
			volume :				
		"""

		self.info({
			     'mediatyp' : 'audio',
			     'interpret' : ' ',
			     'album' : ' ',
			     'title' : ' ',
			     'cover' : 'nocover.png',
			     'timestamp' : ('00.00.00', '00.00.00'),
			     'volume' : 0,
			})	

		return self.info

	def shutdown(self):
		"""
		This function will be call at shutdown.
		It can be used to stop a eventserver 
		or same other backgroundprocesses 
		"""
		return True

class Notification(_Plugin):

 	def start(self):
		"""
		This function will be call at start.
		With this function you can call startups for example start
		a eventserver or same other backgroundprocesses 
		"""
		return

	def send_message(self):
		return True


	def shutdown(self):
		"""
		This function will be call at shutdown.
		It can be used to stop a eventserver 
		or same other backgroundprocesses 
		"""
		return True

class Web(_Plugin):

 	def start(self):
		"""
		This function will be call at start.
		With this function you can call startups for example start
		a eventserver or same other backgroundprocesses 
		"""
		return

	def get_data(self):
		self.webdata = {}
		return self.data

	def shutdown(self):
		"""
		This function will be call at shutdown.
		It can be used to stop a eventserver 
		or same other backgroundprocesses 
		"""
		return True

pluginmgr = PluginMgr()


         