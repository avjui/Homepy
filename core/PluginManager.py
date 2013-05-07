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

            sys.path.insert(0, pdir)
            for mod in [x[:-3] for x in os.listdir(pdir) if x.endswith('.py')]:
                if mod and mod != '__init__':
                    if mod in sys.modules:
                        log('Module %s already exists, skip' % mod, 'info')
                    else:
                        try:
                            pymod = __import__(mod)
                            self.plugin_dirs[pdir] = True
                            log("Plugin Found [Name] %s	[Path] %s"% (mod, pymod.__file__), 'info')
                            DBFunction().AddPlugin(mod.upper(), pymod.__file__.split('/')[1])
                        except ImportError, e:
                            log ('Loading failed, skip plugin %s/%s' % (os.path.basename(pdir), mod), 'error')

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

	def add(self):
		"""  	This function will be call to add a devices		
		
			@param deviceCompany	       name of manufactor
			@param devicename           name of device
			@param devicetype           type of device ex. SWITCH
			@param deviceseriel         serialnummber of device
			@param deviceIP             ip of device
			@param deviceroom           name of the room where the device stay
			@param DeviceValue          value of device
			@param Visible              0 -> false or 1 -> true 
		"""
		return True


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
			timestamp : 
			volume :

		   For video
			title :
			descritpion :
			cover :
			timestamp :
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


pluginmgr = PluginMgr()


         