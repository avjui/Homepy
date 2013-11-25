import os
import cherrypy
import threading
import json
import inspect

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

import core
from core.Helper import ParseTyps
import core.DBFunctions as DBFunctions
from core.Config import Config
from core.Logger import log
from core.PluginManager import *

# modules
#from core.module.homematic.homematic import HmXmlClasses
#from core.module.homematic.homematicserver import EventServer


def serve_template(templatename, **kwargs):
	
	plugins = pluginmgr.get_plugins()
	interface_dir = os.path.join(str(core.PROG_DIR), 'data/interfaces/')
	template_dir = os.path.join(str(interface_dir), 'default')

	template_list = [template_dir]
	#Plugins custom htmls
	for key in plugins:
		plugin = pluginmgr.get_plugins()[key] 		
		path = inspect.getmodule(plugin).__file__
		template = os.path.join(os.path.dirname(path), "interface")
		template_list.append(template)
              
	_hplookup = TemplateLookup(directories=template_list)
	
	try:
		template = _hplookup.get_template(templatename)
		return template.render(**kwargs)
	except:
		return exceptions.html_error_template().render()
	
class WebInterface():


	def __init__(self):
		self.db = DBFunctions.DBFunction
		self.plugins = pluginmgr.get_plugins()
		self.plugins_homeautomation = self.db().GetList('plugins', type='homeautomation')
		self.plugins_multimedia = self.db().GetList('plugins', type='multimedia')
		self.plugins_notification = self.db().GetList('plugins', type='notification')
		self.plugins_web = self.db().GetList('plugins', type='web')

	
	@cherrypy.expose
	def index(self):
		raise cherrypy.HTTPRedirect("home")
	

	@cherrypy.expose
	def home(self):
		db = DBFunctions.DBFunction
		roomlist = DBFunctions.DBFunction().GetRoomsList()
		return serve_template(templatename="index.html", title="Home", roomlist=roomlist)


	@cherrypy.expose
	def config_homeautomation(self):
		devicelist = self.db().GetList('homeautomation')
		roomlist = self.db().GetRoomsList()
		pluginlist = self.db().GetList('plugins', type='homeautomation')
		return serve_template(templatename="config_homeautomation.html", title="Homeautomation Config", devicelist=devicelist, roomlist=roomlist, pluginlist=pluginlist)


	@cherrypy.expose
	def config_multimedia(self):
		
		devicelist = self.db().GetList('multimedia')
		roomlist = self.db().GetRoomsList()
		pluginlist = self._getPluginConfig(self.plugins_multimedia)

		return serve_template(templatename="config_multimedia.html", title="Multimedia Config", devicelist=devicelist, roomlist=roomlist, pluginlist=pluginlist)


	@cherrypy.expose
	def config_web(self):
		devicelist = self.db().GetList('web')
		roomlist = self.db().GetRoomsList()
		pluginlist = self.db().GetList('plugins', type='web')
		return serve_template(templatename="config_web.html", title="Web Config", devicelist=devicelist, roomlist=roomlist, pluginlist=pluginlist)


	@cherrypy.expose
	def config_notification(self):
		devicelist = self.db().GetList('notification')
		roomlist = self.db().GetRoomsList()
		pluginlist = self.db().GetList('plugins', type='homeautomation')
		return serve_template(templatename="config_notification.html", title="Notification Config", devicelist=devicelist, roomlist=roomlist, pluginlist=pluginlist)


	@cherrypy.expose
	def config_rooms(self):
		db = DBFunctions.DBFunction
		roomlist = DBFunctions.DBFunction().GetRoomsList()
		scenelist = DBFunctions.DBFunction().GetSceneElements(None)
		
		return serve_template(templatename="config_rooms.html", title="Rooms Config", roomlist=roomlist, scenelist=scenelist, homeautomationlist=self.plugins_homeautomation, weblist=self.plugins_web, multimedialist=self.plugins_multimedia)


	@cherrypy.expose
	def config_general(self):
		db = DBFunctions.DBFunction
		roomlist = DBFunctions.DBFunction().GetRoomsList()
		return serve_template(templatename="config_general.html", title="General Config", roomlist=roomlist)


	@cherrypy.expose
	def rooms(self):
		db = DBFunctions.DBFunction
		roomlist = DBFunctions.DBFunction().GetRoomsList()
		#self.devicelist = self.db().GetList('homeautomation', devicetype='device')

		#print self.devicelist
		return serve_template(templatename="rooms.html", title="Rooms", roomlist=roomlist)


	@cherrypy.expose
	def multimedia(self):
		self.multimedialist = []
		self.htmllist = {}
		self.roomlist = self.db().GetRoomsList()
		print self.plugins_multimedia
		for plugin in self.plugins_multimedia:
			self.plugincls = pluginmgr.get_plugins()[plugin[1]]
			self.metadata = self.plugincls().get_mediainfo()
			self.multimedialist.append(self.metadata)
			self.htmllist[self.metadata['plugin']] = self.plugincls().config['main_page']

		if self.multimedialist != None:
			return serve_template(templatename="multimedia.html", title="Multimediadevices", htmllist=self.htmllist, trackinfolists=self.multimedialist, roomlist=self.roomlist)
		else:
			raise cherrypy.HTTPRedirect("config_sonos")

	@cherrypy.expose
	def web(self):
		db = DBFunctions.DBFunction
		self.roomlist = DBFunctions.DBFunction().GetRoomsList()
		self.weblist = self.db().GetList('web')

		print self.weblist
		return serve_template(templatename="base_web.html", title="Web", roomlist=self.roomlist, weblists=self.weblist)

	@cherrypy.expose
	def add(self, **kwargs):
		if kwargs['Table'] == 'homeautomation' and kwargs['Type'] == 'device':
			self.plugincls = pluginmgr.get_plugins()[kwargs['Company']]
			self.data = self.plugincls().add(kwargs['Serial'])
			if self.data:
				log('Device found with %s Serial'% kwargs['Serial'], 'debug')
				for key, value in self.data.items():			
					kwargs['Serial'] = key
					kwargs['ValueType'] = value[1]
					db = DBFunctions.DBFunction
					DBFunctions.DBFunction().Add(**kwargs)
			else:
				log('!!! Device was not Found with %s Serial!!!'% kwargs['Serial'], 'debug')
		else:
			DBFunctions.DBFunction().Add(**kwargs)
		
		raise cherrypy.HTTPRedirect("config_homeautomation")


	@cherrypy.expose
	def remove(self, Table, Serial, Company):
		db = DBFunctions.DBFunction
		DBFunctions.DBFunction().Remove(Table, Serial)
		raise cherrypy.HTTPRedirect("config_homeautomation")



	@cherrypy.expose
	def addXbmc(self, xbmc_ip, xbmc_name, xbmc_username, xbmc_password, xbmc_room):
		db = DBFunctions.DBFunction
		DBFunctions.DBFunction().AddXbmc(xbmc_ip, xbmc_name, xbmc_username, xbmc_password, xbmc_room)		
		raise cherrypy.HTTPRedirect("config_xbmc")


	@cherrypy.expose
	def removeXbmc(self, xbmc_ip):
		db = DBFunctions.DBFunction
		DBFunctions.DBFunction().RemoveXbmc(xbmc_ip)
		raise cherrypy.HTTPRedirect("config_xbmc")


	@cherrypy.expose
	def addRoom(self, room_name):
		db = DBFunctions.DBFunction
		DBFunctions.DBFunction().AddRoom(None, room_name)		
		raise cherrypy.HTTPRedirect("config_rooms")


	@cherrypy.expose
	def removeRoom(self, room_name):
		db = DBFunctions.DBFunction
		DBFunctions.DBFunction().RemoveRoom(room_name)		
		raise cherrypy.HTTPRedirect("config_rooms")


	@cherrypy.expose
	def addScene(self, scene_name):
		db = DBFunctions.DBFunction
		DBFunctions.DBFunction().AddScene(None, scene_name)		
		raise cherrypy.HTTPRedirect("config_rooms")


	@cherrypy.expose
	def removeSceneElement(self, scene_name, scene_room, scene_device):
		db = DBFunctions.DBFunction
		DBFunctions.DBFunction().RemoveSceneElements(scene_name, scene_room, scene_device)		
		raise cherrypy.HTTPRedirect("config_rooms")

		
	@cherrypy.expose
	def addElementToScene(self, scene_name, scene_room, scene_device):
		db = DBFunctions.DBFunction
		DBFunctions.DBFunction().UpdateSceneElements(scene_name, scene_room, scene_device)		
		raise cherrypy.HTTPRedirect("config_rooms")


	@cherrypy.expose
	def removeScene(self, scene_name):
		db = DBFunctions.DBFunction
		DBFunctions.DBFunction().RemoveScene(scene_name)		
		raise cherrypy.HTTPRedirect("config_rooms")


	@cherrypy.expose
	def action(self, plugin_name, **kwargs):	
		for key in self.plugins:
			plugin = pluginmgr.get_plugins()[key]
			if plugin().name == plugin_name:
				self.data = plugin().action(**kwargs)
		if type(self.data) == bool:
			return
		else:
			return json.dumps(self.data) 


	@cherrypy.expose
	def updateSonos(self, device_room):	
		print device_room
		raise cherrypy.HTTPRedirect("config_sonos")


	@cherrypy.expose
	def removeSonos(self, device_name):	
		db = DBFunctions.DBFunction
		raise cherrypy.HTTPRedirect("config_sonos")


	@cherrypy.expose
	def searchForSonos(self):		
		raise cherrypy.HTTPRedirect("config_sonos")


	@cherrypy.expose
	def saveGeneralConfig(self, http_host, http_port, http_username, http_password, webinterface, debugEnabled=''):
		core.HTTP_PORT = http_port
		core.HTTP_HOST = http_host
		core.HTTP_USERNAME = http_username
		core.HTTP_PASSWORD = http_password

		core.WEB_INTERFACE = webinterface
		core.DEBUG_LOG = debugEnabled		
		Config().Write()
		raise cherrypy.HTTPRedirect("config_general")	


	@cherrypy.expose
	def functionHomatic(self, device_serial, device_type , value=''):
		#HmXmlClasses().setValueToHMDevice(device_type, device_serial, value)
		return

		
	@cherrypy.expose
	def addCam(self, cam_ip, cam_name, room_name):
		db = DBFunctions.DBFunction
		DBFunctions.DBFunction().Add('web',IP=cam_ip, Name=cam_name, roomName=room_name)		
		raise cherrypy.HTTPRedirect("config_web")


	@cherrypy.expose
	def removeCam(self, cam_ip):	
		db = DBFunctions.DBFunction
		db().Remove('web', IP=cam_ip)
		raise cherrypy.HTTPRedirect("config_web")

	def _getPluginConfig(self, pluginlist):
		self.htmlslist = []
		self.roomlist = self.db().GetRoomsList()
		for plugin in pluginlist:
			self.plugincls = pluginmgr.get_plugins()[plugin[1]]
			self.html = self.plugincls().config
			self.html['name'] = self.plugincls().name
			self.htmlslist.append(self.html)
		print self.htmlslist
		return self.htmlslist
		
		