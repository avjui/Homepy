import socket
from SimpleXMLRPCServer import SimpleXMLRPCServer as Server
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler


class EventServer():

	s = Server(('192.168.1.250', 8990), logRequests=False)
	
	

	def Event(self,*args):

		i = iter(args)
		serial = i.next()
		value = i.next()
		state = i.next()					

		if value == 'LEVEL':
			print "Dimmer with the Serial : %s  switch to %s : %s"% (serial, value, state)
		elif value == 'STATE':
			print "Switch with the Serial : %s  switch to %s : %s"% (serial, value, state)
		else:
			return
					
					
	def listDevices(self):
		device = ''
		return device

	def newDevices(self, array):
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
		

	
		

