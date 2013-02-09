import os
import cherrypy
import threading
import json

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

import core
import core.DBFunctions as DBFunctions
from core.DBFunctions import SonosDB
from core.Config import Config
# modules
from core.module.sonos import Sonos
from core.module.homematic.homematic import HmXmlClasses
from core.module.homematic.homematicserver import EventServer


def serve_template(templatename, **kwargs):

	interface_dir = os.path.join(str(core.PROG_DIR), 'data/interfaces/')
	template_dir = os.path.join(str(interface_dir), 'default')
	
	_hplookup = TemplateLookup(directories=[template_dir])
	
	try:
		template = _hplookup.get_template(templatename)
		return template.render(**kwargs)
	except:
		return exceptions.html_error_template().render()
	
class WebInterface():


	@cherrypy.expose
	def index(self):
		raise cherrypy.HTTPRedirect("home")
	

	@cherrypy.expose
	def home(self):
		db = DBFunctions.DBFunction
		roomlist = DBFunctions.DBFunction().GetRoomsList()
		return serve_template(templatename="index.html", title="Home", roomlist=roomlist)


	@cherrypy.expose
	def config_homematic(self):
		db = DBFunctions.DBFunction
		interfacelist = DBFunctions.DBFunction().GetInterfaceList()
		devicelist = DBFunctions.DBFunction().GetDeviceList()	
		roomlist = DBFunctions.DBFunction().GetRoomsList()
		return serve_template(templatename="config_homematic.html", title="Homematic Config", interfacelist=interfacelist, devicelist=devicelist, roomlist=roomlist)


	@cherrypy.expose
	def config_sonos(self):
		db = DBFunctions.DBFunction
		devicelist = db().GetSonosList()
		roomlist = DBFunctions.DBFunction().GetRoomsList()
		#DBFunctions.DBFunction().GetZoneInfo('Jerry')
		return serve_template(templatename="config_sonos.html", title="Sonos Config", devicelist=devicelist, roomlist=roomlist)


	@cherrypy.expose
	def config_xbmc(self):
		db = DBFunctions.DBFunction
		xbmcs = DBFunctions.DBFunction().GetXbmcList()
		roomlist = DBFunctions.DBFunction().GetRoomsList()
		return serve_template(templatename="config_xbmc.html", title="XBMC Config", xbmcs=xbmcs, roomlist=roomlist)


	@cherrypy.expose
	def config_rooms(self):
		db = DBFunctions.DBFunction
		roomlist = DBFunctions.DBFunction().GetRoomsList()
		scenelist = DBFunctions.DBFunction().GetSceneElements(None)
		devicelist = DBFunctions.DBFunction().GetDeviceList()
		return serve_template(templatename="config_rooms.html", title="Rooms Config", roomlist=roomlist, scenelist=scenelist, devicelist=devicelist)


	@cherrypy.expose
	def config_general(self):
		db = DBFunctions.DBFunction
		roomlist = DBFunctions.DBFunction().GetRoomsList()
		return serve_template(templatename="config_general.html", title="General Config", roomlist=roomlist)


	@cherrypy.expose
	def rooms(self):
		db = DBFunctions.DBFunction
		roomlist = DBFunctions.DBFunction().GetRoomsList()
		return serve_template(templatename="rooms.html", title="Rooms", roomlist=roomlist)


	@cherrypy.expose
	def sonos(self):
		db = DBFunctions.DBFunction
		roomlist = DBFunctions.DBFunction().GetRoomsList()
		trackinfolist =  SonosDB().GetZoneInfo()
		if trackinfolist != None:
			return serve_template(templatename="sonos.html", title="Sonos", trackinfolist=trackinfolist, roomlist=roomlist)
		else:
			raise cherrypy.HTTPRedirect("config_sonos")


	@cherrypy.expose
	def addInterface(self, interface_serial, interface_ip, interface_name):
		db = DBFunctions.DBFunction
		self.data = self
		DBFunctions.DBFunction().AddInterface(None, interface_serial, interface_ip, interface_name)
		raise cherrypy.HTTPRedirect("config_homematic")


	@cherrypy.expose
	def removeInterface(self, interface_serial):
		db = DBFunctions.DBFunction
		DBFunctions.DBFunction().RemoveInterface(interface_serial)
		raise cherrypy.HTTPRedirect("config_homematic")


	@cherrypy.expose
	def addDevice(self, device_serial, device_name, device_type, device_room):
		db = DBFunctions.DBFunction
		if HmXmlClasses().addHMDevice(device_serial):
			device_children = HmXmlClasses().getHMChildren(device_serial)
			DBFunctions.DBFunction().AddDevice(device_children, device_name, device_type, device_room)		
		raise cherrypy.HTTPRedirect("config_homematic")


	@cherrypy.expose
	def removeDevice(self, device_serial):
		db = DBFunctions.DBFunction

		#HmXmlClasses().deleteHMDevice(device_serial)
		DBFunctions.DBFunction().RemoveDevice(device_serial)

		raise cherrypy.HTTPRedirect("config_homematic")


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
	def functionSonos(self, zonen_ip='', function='', zone_name=''):
		self.data = []
		db = DBFunctions.DBFunction		
		if function == 'getcover':
			trackinfolist = SonosDB().GetZoneInfo()
			for key,devices in trackinfolist.iteritems():
				for device in devices:

					if device[0] == zone_name:

						zonenip = device[1]
						art = device[2]
						title = device[3]
						album = device[4]		
						artist = device[5]
						self.data = art, title, album, artist, zonenip
						return json.dumps(self.data)

		else:
			Sonos().SonosFunctions(zonen_ip, function)
			return 


	@cherrypy.expose
	def updateSonos(self, device_room):	
		print device_room
		raise cherrypy.HTTPRedirect("config_sonos")


	@cherrypy.expose
	def removeSonos(self, device_name):	
		db = DBFunctions.DBFunction
		db().RemoveSonos(device_name)
		raise cherrypy.HTTPRedirect("config_sonos")


	@cherrypy.expose
	def searchForSonos(self):
		DBFunctions.DBFunction().AddSonos()		
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
	def functionHomatic(self, device_serial, value='', type='' ):

		if value == '':
			HmXmlClasses().setValueToHMSwitch(device_serial)
			return
		else:	
			HmXmlClasses().setValueToHMDimmer(device_serial, value)
			return 


	@cherrypy.expose
	def event(self,*args):
	
		print args
		

		