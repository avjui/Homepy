import socket
from SimpleXMLRPCServer import SimpleXMLRPCServer as Server
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

# core 
from core.DBFunctions import DBFunction
from core.Logger import log


class EventServer():

	s = Server(('192.168.1.250', 8990), logRequests=False)
	
	

	def Event(self,*args):

		i = iter(args)
		eventid = i.next()
		serial= i.next()
		type = i.next()					
		value = i.next()

		if type == 'LEVEL':
			DBFunction().UpdateDevice(serial, type, value)
			log('Dimmer with the Serial : %s  switch to %s : %s'% (serial, type, value), 'debug')
		elif type == 'STATE':
			DBFunction().UpdateDevice(serial, type, value)
			log('Switch with the Serial : %s  switch to %s : %s'% (serial, type, value), 'debug')
		else:
			data = ''
			return data
					
					
	def listDevices(self, array):
		device = ''
		return device

	def newDevices(self, interface_id, description_array):
		device = ''
		return device
		
	
	def start(self):

		self.s.register_function(self.Event, 'event')
		self.s.register_function(self.listDevices, 'listDevices')
		self.s.register_function(self.newDevices, 'newDevices')
	
		self.s.register_introspection_functions()

		self.s.register_multicall_functions()

		#Starting the Server
		self.s.serve_forever()
