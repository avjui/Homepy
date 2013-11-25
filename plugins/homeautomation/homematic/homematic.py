#
# -*- coding: <utf-8> -*-
#

import threading
import time

#XMLRPC
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer as Server

import cherrypy
from cherrypy.process.plugins import Monitor

from core.PluginManager import Homeautomation
from core.Logger import log
from core.Helper import get_local_ip
from core.DBFunctions import DBFunction

class Homematic(Homeautomation):

	name = 'Homematic'
	type = 'homeautomation'
	config = {
    		   'main_page': '',
		   'config_page': '',
		  }


	def __init__(self):

		self.local_ip = get_local_ip()
		self.local_port = 8991
		#self.server_ip = self.local_ip
		self.server_ip = '192.168.1.150' # for testing
		self.server_port = '2001'
		self.server = self._Connector()
		
		#Set HomeMatic ValuesTypes
		self.validevicetyps = ['SWITCH', 'DIMMER', 'CLIMATECONTROL_REGULATOR', 'HUMIDITY', 'TEMPERATURE', 'KEY', 'KEYMATIC']
		self.validdatatyps = ['STATE', 'LEVEL', 'INSTALL_TEST']


	def start(self):
		

		self.server_thread = threading.Thread(target=self._EventServer)
		self.server_thread.daemon = True
		self.server_thread.start()
		print "Homematic starts"
		self.server.init(self.localip, '12345678')
		log('Homematic was connected with BidCos service', 'info')
		return

	def add(self, serial):
	
		try:
			self.server.addDevice(serial)
			time.sleep(3)
			log('The interface with the Serial: %s was added'%(serial), 'info')
			self.description = self._ListDevices()
			self.data = self.__ParseTyps(serial, self.description)

			return self.data

		except xmlrpclib.Fault as err:
			log (err.faultString, 'error')
			return False


	def remove(self, serial):

		try:
			self.server.removeDevice(serial)
			log('The interface with the Serial: %s was removed'%(serial), 'info')
			return 

		except xmlrpclib.Fault as err:
			log (err.faultString, 'error')
			return

	def action(self, **kwargs):

		try:
			self.func = gettattr(self.server,'_' + kwargs['function'])
			self.func(kwargs)
			return True

		except AttributeError:
			log('Function[%s] is not given'% (kwargs['function']), 'debug')
			return False


	def shutdown(self):

		log('Disconect from Homatic API', 'info')
		self.stop = True
		self.server.init(self.localip, '')


	def _ListDevices(self):

		""" Return information of all devices witch are added
		to the HomeMatic interface. 	

		"""

		try:
			self.interfaces = self.server.listDevices()
			return self.interfaces					

		except xmlrpclib.Fault as err:
			log ('%s', 'error'), err.faultString


	def _setValueToHMDevice(self, devicetype, device, value=''):

		try:

			self.server.setValue(device, devicetype, value)
			log('Set Device with serial :%s to %s : %s"'%(device, devicetype, value), 'debug')

		except xmlrpclib.Fault as err:
			log (err.faultString, 'error')


	def _GetHmDescription(self,serial):

		""" Return information of all devices witch are added
		to the HomeMatic interface. 	

		"""

		try:
			self.interfaces = self.server.getDeviceDescription(serial)
			return self.interfaces					

		except xmlrpclib.Fault as err:
			log ('%s', 'error'), err.faultString


	def _Event(self,*args):

		self.i = iter(args)
		self.eventid = self.i.next()
		self.serial= self.i.next()
		self.type = self.i.next()					
		self.value = self.i.next()
		if self.type in self.validdatatyps:
			DBFunction().UpdateDevice(self.serial, self.type, self.value)
			log('Device with the Serial : %s  switch to %s : %s'% (self.serial, self.type, self.value), 'debug')
		else:
			log('Device with the Serial : %s has unknown type: %s '% (self.serial, self.type), 'debug')
			self.data = ''
			return self.data
		
	
	def _Connector(self):

		try:
			self.serverip = "http://%s:%s"% (self.server_ip, self.server_port)
			self.localip = "%s:%s" %(self.local_ip, self.local_port)

			self.server = xmlrpclib.ServerProxy(self.serverip)

			return self.server

		except xmlrpclib.Fault as err:
			log (err.faultString, 'error')


	def _EventServer(self):
		try:
			self.s = Server((self.local_ip, self.local_port), logRequests=False)
			self.s.register_function(self._Event, 'event')
			self.s.register_function(self.__ListDevices, 'listDevices')
			self.s.register_function(self.__NewDevices, 'newDevices')
	
			self.s.register_introspection_functions()

			self.s.register_multicall_functions()
	
			print "Starting the Server"
			self.stop = False
			while not self.stop:
				self.s.handle_request()
			
		except:
			log('EventServer do not start', 'error')
			return

					
	def __ListDevices(self, array):
		self.device = ''
		return self.device


	def __NewDevices(self, interface_id, description_array):
		self.device = ''
		return self.device


	def __ParseTyps(self, deviceSerial, description):

		self.data = {}
	
		for items in description:
			if items.get('INDEX') != None:
				if items['PARENT'] == deviceSerial and items['INDEX'] == 1:
					self.serial = items['PARENT']
					self.name = items['PARENT_TYPE']
					self.devicetype = items['TYPE']
					

		self.children = self._GetHmDescription(deviceSerial)['CHILDREN']
		for child in self.children:
			if not child.endswith(':0'):
				self.data[child] = self.name, self.devicetype
	
		return self.data