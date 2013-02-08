import socket
from SimpleXMLRPCServer import SimpleXMLRPCServer as Server
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import xmlrpclib


class Initial():

	# Get local ip
	#hostname = socket.gethostname()
	#address = socket.gethostbyname("%s.local" % hostname)

	s = Server(('192.168.1.250', 8990))
	
	

	def Event(self,*args):
	
		print args


	def listDevices(self):
		device = ''
		return device

	def newDevices(self, array):
		device = ''
		return device
		
	s.register_function(Event, 'event')
	s.register_function(listDevices, 'listDevices')
	s.register_function(newDevices, 'newDevices')

	s.register_introspection_functions()

	s.register_multicall_functions()

	#Starting the Server
	s.serve_forever()

	
		

