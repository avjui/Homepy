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
                for dir in dirs:
                    lookdir = os.path.join(root, dir)
                    sys.path.insert(0, lookdir)
                    for mod in [x[:-3] for x in os.listdir(lookdir) if x.endswith('.py')]:
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
                                    log ('Loading failed, skip plugin %s/%s Error: %s' % (os.path.basename(lookdir), mod ,e), 'error')

                del(sys.path[0])
                break


    def get_plugins(self):
        """ the return value is dict of name:class pairs """
        self._load_all()
        return _Plugin.get_plugins()


class _BasePlugin(_Plugin):

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


	def shutdown(self):
		"""
		This function will be call at shutdown.
		It can be used to stop a eventserver 
		or same other backgroundprocesses 
		"""
		return True


class Homeautomation(_BasePlugin):


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



class Multimedia(_BasePlugin):

	def action(self, plugin_name, **kwargs):
		"""
		@param plugin_name                 name of the plugin how was specified in plugin class as name

		"""

		return True


	def get_mediainfo(self):
		""" This function return a dict with media informations
		    This dict must contain few things

		    First you need plugin and specifiate name (f.e. ip)

		    For audio
		       mediatyp : 'audio'
			album :
			artist :
			cover :
			duration :
			position: 
			title :
			volume :

		   For video
			mediatyp : 'video'
			title :
			descritpion :
			cover :
			duration :
			position: 
			volume :				
		"""

		self.info = {'plugin' : 'unknown',
			      'name' : {
					  'mediatyp' : u'audio',
					  'album' : u' ',
					  'artist' : u' ',
				 	  'cover' : u'nocover.png',
					  'devicename' : u' ',
					  'deviceip' : u' ',
					  'duration' : u'0:00:00',
					  'position' : u'0:00:00',
					  'title' : u' ',
					  'volume' : u'0',
					 }
				}	

		return self.info



class Notification(_BasePlugin):

	def send_message(self):
		return True



class Web(_BasePlugin):

	def get_data(self):
		self.webdata = {}
		return self.data

	def send_data(self):
		self.webdata = {}
		return self.data

pluginmgr = PluginMgr()


         