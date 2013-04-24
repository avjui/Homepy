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
			log (err.faultString, 'error') 


	def Init(self):
		
		try:
			interface = self.ConectToServer().init('192.168.1.250:8990', '12345678')
			return True

		except xmlrpclib.Fault as err:
			log (err.faultString, 'error')



	def GetHmDescription(self):

		""" Return information of all devices witch are added
		to the HomeMatic interface. 	

		"""

		try:
			interfaces = self.ConectToServer().listDevices()
			return interfaces					

		except xmlrpclib.Fault as err:
			log ('%s', 'error'), err.faultString

			

	def addHMDevice(self, serial):
	
		try:
			interface = self.ConectToServer().addDevice(serial)
			log('The interface with the Serial: %s was added'%(serial), 'info')
			return True

		except xmlrpclib.Fault as err:
			log ('%s', 'error'), err.faultString


	def deleteHMDevice(self, serial):

		try:
			interface = self.ConectToServer().deleteDevice(serial)
			log('The interface with the Serial: %s was deleted'%(serial), 'info')
			sleep(3)

		except xmlrpclib.Fault as err:
			log (err.faultString, 'error')	


	def getHMDeviceDescription(self, serial):

		try:
			self.result = self.ConectToServer().getDeviceDescription(serial)
			log('The interface with the Serial: %s was deleted'% (serial), 'info')
			return self.result

		except xmlrpclib.Fault as err:
			log (err.faultStringg, 'error')


	def getHMChildren(self, serial):

		try:
			self.description = self.getHMDeviceDescription(serial)
			for key, values in self.description.items():
				if key == 'CHILDREN':
					log('Function  [getHMChildren : ' + str(values) + ']', 'debug')
					return values
		except:
			log ('Function  [getHMChildren : ]Do not return CHILDREN', 'error')
	

	def getParamsetFromHMDevice(self, devices):

		try:
			self.Paramsets = []

			for device in devices:
				self.Paramset = self.ConectToServer().getParamset(device, 'VALUES')
				self.Paramsets.append(self.Paramset)

			return self.Paramsets

		except xmlrpclib.Fault as err:
			log (err.faultString, 'error')



	def setValueToHMDevice(self, devicetype, device, value=''):

		try:
			if value == '':
				value = self.getParamsetFromHMDevice(device)
				value = self.toggleSwitch(value)

			interfaces = self.ConectToServer().setValue(device, devicetype, value)
			log('Set Device with serial :%s to %s : %s"'%(device, devicetype, value), 'debug')

		except xmlrpclib.Fault as err:
			log (err.faultString, 'error')



	def getValueFromHMDimmer(self, device):

		try:
			result = self.ConectToServer().gettValue(device, 'LEVEL')
			log('Value for Device: %s is %s'% (device, result), 'debug')

		except xmlrpclib.Fault as err:
			log (err.faultString, 'error'), err.faultString

	

	def toggleSwitch(self, Paramset):
	
		for key, value in Paramset.items():
			if(key == 'STATE'):
				if(value):
					return False
				else:
					return True

	def Multicall(self, methoddic):

		""" 
		This function send a multicall request to server.
		The methoddic specificate must be a dictionary. The key is the methodecall
		and the value must be a list for the arguments for the call.
		"""


		self.multicall = xmlrpclib.MultiCall(self.ConectToServer)
		
		for methode, values in methoddic:

			self.call = getattr(self.multicall, methode)
			self.call(values)
			log('[ HomeMatic Multicall ] The  %s multicall function send %s arguments'% (methode, values), 'debug')

		self.multicall()
		return

		