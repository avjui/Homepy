import socket
from SimpleXMLRPCServer import SimpleXMLRPCServer as Server
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

# core 
from core.DBFunctions import DBFunction
from core.Logger import log
from core.Helper import get_local_ip


class EventServer():


	ip = get_local_ip()
	s = Server((ip, 8990), logRequests=False)

	#Set HomeMatic ValuesTypes
	validevicetyps = ['SWITCH', 'DIMMER', 'CLIMATECONTROL_REGULATOR', 'HUMIDITY', 'TEMPERATURE', 'KEY', 'KEYMATIC']
	validdatatyps = ['STATE', 'LEVEL']

	def Event(self,*args):

		i = iter(args)
		eventid = i.next()
		serial= i.next()
		type = i.next()					
		value = i.next()
		#print args
		if type in self.validdatatyps:
			DBFunction().UpdateDevice(serial, type, value)
			log('Device with the Serial : %s  switch to %s : %s'% (serial, type, value), 'debug')
		else:
			data = ''
			return data
					
					
	def listDevices(self, array):
		device = ''
		#print array
		return device

	def newDevices(self, interface_id, description_array):
		device = ''
		return device
		
	
	def start(self):
		try:
			self.s.register_function(self.Event, 'event')
			self.s.register_function(self.listDevices, 'listDevices')
			self.s.register_function(self.newDevices, 'newDevices')
	
			self.s.register_introspection_functions()

			self.s.register_multicall_functions()
	
			#Starting the Server
			log('Starting EventServer' , 'info')
			self.s.serve_forever()
			
		except:
			log('EventServer do not start', 'error')
			return