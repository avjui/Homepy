import xmlrpclib
from time import sleep
import re

from core.Logger import log

class HmXmlClasses():

	def ConectToServer(self, **kwargs):

		"""  Connect to Api from Homematice interface

		There you can add different arguments. For example:
		 - verbose=True
		 - multical=True

		"""

		try:
			server = xmlrpclib.ServerProxy("http://192.168.1.150:2001")
			return server

		except xmlrpclib.Fault as err:
			log (err.faultString, 'error'), 


	def GetHMInterfaces(self, **kwargs):

		""" Return the adress of interfaces

		You can also specification witch Interface this function should return

		"""

		interfaces = self.ConectToServer().listDevices('IEQ0004676')
	
		description = ''
		address = ''
		subaddress = ''
		#values = interfaces
		values = re.split("]}, {" ,str(interfaces))
		#print values
		for value in values:
			if 'TYP' in value:
				description = value
			if 'ADDRESS' in value and 'IEQ' in value:
				subaddress = subaddress + value		
			


	def addHMDevice(self, serial):
	
		try:
			interface = self.ConectToServer().addDevice(serial)
			log('The interface with the Serial: %s was added', 'info'), (serial)
			return True

		except xmlrpclib.Fault as err:
			log ('%s', 'error'), err.faultString


	def deleteHMDevice(self, serial):

		try:
			interface = self.ConectToServer().deleteDevice(serial)
			log('The interface with the Serial: %s was deleted', 'info'), (serial)
			sleep(3)

		except xmlrpclib.Fault as err:
			log ('%s', 'error'), err.faultStringg
	


	def getHMDeviceDescription(self, serial):

		try:
			self.result = self.ConectToServer().getDeviceDescription(serial)
			log('The interface with the Serial: %s was deleted', 'info'), (serial)
			return self.result

		except xmlrpclib.Fault as err:
			log ('%s', 'error'), err.faultStringg


	def getHMChildren(self, serial):

		try:
			self.description = self.getHMDeviceDescription(serial)
			for key, values in self.description.items():
				if key == 'CHILDREN':
					#log(Function  [getHMChildren : + str(values) + ']', 'debug')
					return values
		except:
			log ('Do not return CHILDREN', 'error')
	

	def getParamsetFromHMDevice(self, device):

		try:
			Paramset = self.ConectToServer().getParamset(device, 'VALUES')
			return Paramset

		except xmlrpclib.Fault as err:
			log ('%s', 'error'), err.faultString



	def setValueToHMSwitch(self, device):

		try:
			value = self.getParamsetFromHMDevice(device)
			state = self.toggleSwitch(value)
			interfaces = self.ConectToServer().setValue(device, 'STATE', state)
			log('Set Switch to STATE %s"', 'debug'), (state)

		except xmlrpclib.Fault as err:
			log ('%s', 'error'), err.faultString



	def setValueToHMDimmer(self, device, level):

		try:
			interfaces = self.ConectToServer().setValue(device, 'LEVEL', level)
			log('Set Device: %s to STATE %s' , 'debug'), (device, level)


		except xmlrpclib.Fault as err:
			log ('%s', 'error'), err.faultString
	


	def getValueFromHMDimmer(self, device):

		try:
			result = self.ConectToServer().gettValue(device, 'LEVEL')
			log('Value for Device: %s is %s' , 'debug'), (device, result)


		except xmlrpclib.Fault as err:
			log ('%s', 'error'), err.faultString

	

	def toggleSwitch(self, Paramset):
	
		for key, value in Paramset.items():
			if(key == 'STATE'):
				if(value):
					return False
				else:
					return True


