import os
import sys
import socket
import threading

#XMLRPC
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer as Server
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

from core.PluginManager import _Plugin
from core.Logger import log
from core.Helper import get_local_ip
from core.DBFunctions import DBFunction

class Homematic(_Plugin):

	name = 'Homematic'
	type = 'homeautomation'


	def __init__(self):

		self.local_ip = get_local_ip()
		self.local_port = '8990'
		#self.server_ip = self.local_ip
		self.server_ip = '192.168.1.150' # for testing
		self.server_port = '2001'

		#Set HomeMatic ValuesTypes
		self.validevicetyps = ['SWITCH', 'DIMMER', 'CLIMATECONTROL_REGULATOR', 'HUMIDITY', 'TEMPERATURE', 'KEY', 'KEYMATIC']
		self.validdatatyps = ['STATE', 'LEVEL', 'INSTALL_TEST']

	def start(self, **kwargs):
		

		self._Event_Server_start()
		
		try:
			for k,v in kwargs.iteritems():
				if k == 'server_ip':
					self.server_ip = v
				elif k == 'server_port':
					self.server_port = v	
				elif k == 'local_port':
					self.local_port = v
				else: 
					continue
			
			self.serverip = "http://%s:%s"% (self.server_ip, self.server_port)
			self.localip = "%s:%s" %(self.local_ip, self.local_port)

			self.server = xmlrpclib.ServerProxy(self.serverip)
			#self.interface = self.server().init(self.localip , '12345678')
			log('Homematic was connected with BidCos service', 'info')
			return

		except xmlrpclib.Fault as err:
			log (err.faultString, 'error')

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
					
					
	def _listDevices(self, array):
		self.device = ''
		return self.device

	def _newDevices(self, interface_id, description_array):
		self.device = ''
		return self.device
		
	
	def _EventServer(self):
		try:
			self.s.register_function(self._Event, 'event')
			self.s.register_function(self._listDevices, 'listDevices')
			self.s.register_function(self._newDevices, 'newDevices')
	
			self.s.register_introspection_functions()

			self.s.register_multicall_functions()
	
			#Starting the Server
			log('Starting EventServer' , 'info')
			self.s.serve_forever()
			
		except:
			log('EventServer do not start', 'error')
			return

	def _Event_Server_start(self):
		#self.serverthread = threading.Thread(target=_EventServer())
		#self.serverthread.start()
		print "Homematic starts"
		log('Homematic XMLRPC server started', 'info')