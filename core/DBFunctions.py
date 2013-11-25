
import os
import sqlite3
import threading
import json
import time

import core
from core.Logger import log
from core.Helper import Replacesq

db_lock = threading.Lock()

class DBFunction:


	def getCountID(self, tableName, indicatorName):

		self.tableName = tableName
		self.indicatorName = indicatorName
		self.connection = sqlite3.connect(core.DB_FILE, timeout=20)
		self.cursor = self.connection.cursor()

		if self.indicatorName == None:
			self.sql = "SELECT count(ID) FROM table"
		else:
			self.sql = "SELECT count('" + self.indicatorName + "') FROM '" + self.tableName + "'"
		
		self.cursor.execute(self.sql)
		self.connection.commit()
		self.result = self.cursor.fetchall()    
		self.recordCount = self.result[0][0]
		self.cursor.close()
		return self.recordCount

	
	def AddInterface(self, interfaceID, interfaceSerial, interfaceIP, interfaceName):

		#if interfaceID == None:
		#	self.interfaceID = self.getCountID('interfaces', None)

		interfaceSerial = interfaceSerial.upper()
		interfaceIP = interfaceIP.upper()
		interfaceName = interfaceName.upper()
		
		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()
		sql = "INSERT INTO interfaces(InterfaceSerial, InterfaceIP, InterfaceName) VALUES('" + interfaceSerial + "','" + interfaceIP + "','" + interfaceName + "')"
		cursor.execute(sql)
		connection.commit()
		cursor.close()
		return True

	def RemoveInterface(self, interfaceSerial):

		self.interfaceSerial = interfaceSerial
		self.connection = sqlite3.connect(core.DB_FILE, timeout=20)
		self.cursor = self.connection.cursor()

		self.sql = "DELETE FROM interfaces WHERE InterfaceSerial = '" + self.interfaceSerial + "'"
		self.cursor.execute(self.sql)
		print self.connection.commit()
		self.cursor.close()
		return 


	def GetInterfaceList(self):

		self.data = ""
		self.connection = sqlite3.connect(core.DB_FILE, timeout=20)
		self.cursor = self.connection.cursor()

		self.sql = "SELECT InterfaceSerial, InterfaceName FROM interfaces"

		self.cursor.execute(self.sql)
		self.result = self.cursor.fetchall()
		self.cursor.close()
		print self.result
		return self.result


	def AddDevice(self, deviceSerial, deviceName, deviceType, roomName, companyName='', hidden=1):

		self.i = 0
		self.deviceType = deviceType
		self.deviceSerial = deviceSerial
		self.roomID = int(self.getCountID('devices', 'OrderID' ))
		
		self.value = 0

		self.deviceName = deviceName.upper()
		self.roomName = roomName.upper()
		
		self.connection = sqlite3.connect(core.DB_FILE, timeout=20)
		self.cursor = self.connection.cursor()
		for self.serial in self.deviceSerial:
			if not self.serial.endswith(':0'):
				self.size = len(self.deviceSerial)
				if self.size > 2:
					self.i = self.i + 1
					self.cursor.execute('INSERT INTO devices(OrderID, DeviceTyp, DeviceName, DeviceSerial, RoomName, DeviceValue, DeviceVisible) VALUES(?,?,?,?,?,?,?)', (self.roomID, self.deviceType, self.deviceName + "(" + str(self.i) + ")", self.serial, self.roomName, '0.0', hidden))
					self.connection.commit()
				else:
					self.cursor.execute('INSERT INTO devices(OrderID, DeviceTyp, DeviceName, DeviceSerial, RoomName, DeviceValue, DeviceVisible) VALUES(?,?,?,?,?,?,?)', (self.roomID, self.deviceType, self.deviceName, self.serial, self.roomName, '0.0', hidden))
					self.connection.commit()

		self.cursor.close()
		return True



	def GetDeviceList(self, roomName=''):


		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()
	
		if roomName == '':
			sql = "SELECT DeviceTyp , DeviceName , DeviceSerial , RoomName, DeviceValue FROM devices ORDER BY OrderID"
			log(sql, 'debug')
		else:
			sql = "SELECT DeviceTyp , DeviceName , DeviceSerial , RoomName, DeviceValue FROM devices WHERE RoomName='%s'"% (roomName)
			log(sql, 'debug')
		
		cursor.execute(sql)
		self.result = cursor.fetchall()
		cursor.close()
	    	return self.result


	def UpdateDevice(self, deviceSerial, ValueType, deviceValue):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "UPDATE devices SET ValueType='%s', DeviceValue='%s' WHERE DeviceSerial='%s'"% (ValueType, deviceValue, deviceSerial)
		print sql
		cursor.execute(sql)
		connection.commit()
		cursor.close()
	    	return 



	def RemoveDevice(self, deviceSerial):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "DELETE FROM devices WHERE DeviceSerial = '" + deviceSerial + "'"
		cursor.execute(sql)
		connection.commit()
		cursor.close()
		return 

		
	def AddXbmc(self, XbmcIP, XbmcName, XbmcUsername, XbmcPassword, XbmcRoom):

		roomID = int(self.getCountID('devices', 'OrderID' ))

		XbmcIP = XbmcIP.upper()
		XbmcName = XbmcName.upper()
		XbmcUsername = XbmcUsername.upper()
		XbmcPassword = XbmcPassword.upper()
		XbmcRoom = XbmcRoom.upper()

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()
		cursor.execute('INSERT INTO xbmc (XbmcIP, XbmcName, XbmcUsername, XbmcPassword, XbmcRoom) VALUES(?,?,?,?,?)', (XbmcIP, XbmcName, XbmcUsername, XbmcPassword, XbmcRoom))
		connection.commit()
		cursor.close()
		return True

	def GetXbmcList(self):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "SELECT XbmcIP, XbmcName, XbmcRoom FROM xbmc"

		cursor.execute(sql)
		result = cursor.fetchall()
		cursor.close()
	    	return result		


	def RemoveXbmc(self, xbmcIP):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "DELETE FROM xbmc WHERE XbmcIP = '" + xbmcIP + "'"
		cursor.execute(sql)
		connection.commit()
		cursor.close()
		return 


	def AddRoom(self, orderID, roomName):


		if orderID == None:
			orderID = int(self.getCountID('rooms', 'OrderID' ))

		roomName = roomName.upper()

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "INSERT INTO rooms (OrderID, RoomName) VALUES(%s,'%s')"% (orderID, roomName)
		
		cursor.execute(sql)
		connection.commit()
		cursor.close()
		return 

	def GetRoomsList(self):
		
		result = []

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()
		try:
			sql = "SELECT OrderID, RoomName FROM rooms ORDER BY OrderID"
	
			cursor.execute(sql)
			result = cursor.fetchall()
			cursor.close()

		except Exception,e:
			log(e, 'error')

	    	return result	


	def RemoveRoom(self, roomName):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "DELETE FROM rooms WHERE RoomName = '" + roomName + "'"
		cursor.execute(sql)
		connection.commit()
		cursor.close()
		return 


	def AddScene(self, orderID, sceneName):


		if orderID == None:
			orderID = int(self.getCountID('scenes', 'OrderID' ))

		sceneName = sceneName.upper()

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "INSERT INTO scenes (OrderID, SceneName) VALUES(%s,'%s')"% (orderID, sceneName.upper())
		
		cursor.execute(sql)
		connection.commit()

		sql = "CREATE TABLE IF NOT EXISTS '%s' (OrderID INTEGER, SceneName TEXT, RoomName TEXT, DeviceName TEXT, SwitchValue INTEGER, DimmerValue FLOAT)"% (sceneName.upper()) 

		cursor.execute(sql)
		connection.commit()

		sql = "INSERT INTO '%s' (SceneName) VALUES ('%s')"% (sceneName.upper(), sceneName.upper()) 

		cursor.execute(sql)
		connection.commit()


		cursor.close()
		return 


	def GetScenes(self):

		self.result = ''

		try:
			connection = sqlite3.connect(core.DB_FILE, timeout=20)
			cursor = connection.cursor()

			sql = "SELECT OrderID, SceneName FROM scenes"

			cursor.execute(sql)
			self.result = cursor.fetchall()
			cursor.close()
	    		return self.result
		except:
			return self.result


	def GetSceneElements(self, scene_name):



		self.data = {}
		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		if scene_name == None:
			for scene in self.GetScenes():		
				sql = "SELECT SceneName, RoomName, DeviceName FROM '%s'" % (scene[1])
				
				cursor.execute(sql)
				result = cursor.fetchall()
				self.data[scene[1]]= result
				
		else:
			sql = "SELECT " + scene_name + ", RoomName, DeviceName, SwitchValue, DimmerValue FROM scenes ORDER BY OrderID"
			cursor.execute(sql)
			self.data[scene_name] = cursor.fetchall()

		cursor.close()
		print self.data
	    	return self.data


	def RemoveSceneElements(self, sceneName, sceneRoom, sceneDevice):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sceneName = sceneName.upper()
		sceneRoom = sceneRoom.upper()
		sceneDevice = sceneDevice.upper()

		if sceneRoom == 'NONE':
			sql = "DELETE FROM '%s' WHERE DeviceName='%s'"% (sceneName, sceneDevice)
		else:
			sql = "DELETE FROM '%s' WHERE RoomName='%s'"% (sceneName, sceneRoom)

		cursor.execute(sql)
		connection.commit()
		cursor.close()
	    	return 


	def UpdateSceneElements(self, sceneName, sceneRoom, sceneDevice):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sceneName = sceneName.upper()
		sceneRoom = sceneRoom.upper()
		sceneDevice = sceneDevice.upper()
		
		if sceneRoom == '--- PLEASE CHOOSE A ROOM ---':
			sql = "INSERT INTO '%s' (SceneName, DeviceName) VALUES('%s','%s')"% (sceneName, sceneName, sceneDevice)
		else:
			sql = "INSERT INTO '%s' (SceneName, RoomName) VALUES('%s','%s')"% (sceneName, sceneName, sceneRoom )

		cursor.execute(sql)
		connection.commit()
		cursor.close()
	    	return 


	def RemoveScene(self, sceneName):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "DELETE FROM '" + sceneName + "'"
		cursor.execute(sql)
		connection.commit()

		sql = "DELETE FROM scenes WHERE SceneName = '" + sceneName + "'"
		cursor.execute(sql)
		connection.commit()
		cursor.close()
		return 	

	def AddCam(self, camIP, camName, roomName):

		camIP = camIP
		camName = camName.upper()
		roomName = roomName.upper()

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "INSERT INTO web (CamIP, CamName, CamRoom) VALUES('%s','%s', '%s')"% (camIP, camName, roomName)
		
		cursor.execute(sql)
		connection.commit()
		cursor.close()
		return 


	def GetCamList(self):
		
		result = []

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()
		try:
			sql = "SELECT CamIP, CamName, CamRoom FROM cams ORDER BY OrderID"
	
			cursor.execute(sql)
			result = cursor.fetchall()
			cursor.close()

		except Exception,e:
			log(e, 'error')

	    	return result	


	def RemoveCam(self, camIP):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "DELETE FROM cams WHERE CamIP = '" + camIP + "'"
		cursor.execute(sql)
		connection.commit()
		cursor.close()
		return 	


	def AddPlugin(self, Name, Type, Active=1):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "INSERT INTO plugins (Type, Name, Active) VALUES('%s','%s', '%i')"% (Type, Name, Active)
		
		cursor.execute(sql)
		connection.commit()
		cursor.close()
		return 

	def Add(self, Table, Company='', Serial='', Name='', Type='device', roomName='',Value='', ValueType='UNKNOWN', IP='', Username='', Password='', ApiKey='', hidden=0):

		self.i = 0
		self.type = Type
		self.serial = Serial
		self.roomID = int(self.getCountID('devices', 'OrderID' ))
		
		self.value = Value

		self.deviceName = Name.upper()
		self.roomName = roomName.upper()
		
		self.connection = sqlite3.connect(core.DB_FILE, timeout=20)
		self.cursor = self.connection.cursor()

		if Table == 'homeautomation':
		
			self.cursor.execute('INSERT INTO homeautomation(OrderID, DeviceCompany, DeviceTyp, Name, DeviceSerial, IP, Room, ValueType, DeviceValue, DeviceVisible) VALUES(?,?,?,?,?,?,?,?,?,?)', (self.roomID ,Company, self.type, self.deviceName, self.serial, IP, self.roomName, ValueType, '0.0', hidden))
			self.connection.commit()
	
		elif Table == 'multimedia':

			self.cursor.execute('INSERT INTO multimedia (OrderID, DeviceCompany, IP, Name, Username, Password, ApiKey, Room) VALUES(?,?,?,?,?,?,?,?)', (self.roomID, Company, IP, self.deviceName, Username, Password, ApiKey, self.roomName))
			self.connection.commit()

		elif Table == 'notification':

			self.cursor.execute('INSERT INTO notification (OrderID, DeviceCompany, IP, Name, Username, Password, ApiKey) VALUES(?,?,?,?,?,?,?)', (self.roomID, Company, IP, self.deviceName, Username, Password, ApiKey))
			self.connection.commit()

		elif Table == 'web':

			self.sql = "INSERT INTO web (IP, Name, Username, Password, ApiKey, Room) VALUES('%s','%s','%s','%s','%s','%s')"% (IP, self.deviceName, Username, Password, ApiKey, self.roomName)
			self.cursor.execute(self.sql)
			self.connection.commit()

		elif Table == 'room':

			sql = "INSERT INTO rooms (OrderID, RoomName) VALUES(%s,'%s')"% (orderID, self.roomName)
			self.cursor.execute(self.sql)
			self.connection.commit()
		

		self.cursor.close()
		return True


	def Remove(self, Table, Serial= '', IP='', roomName=''):

		self.connection = sqlite3.connect(core.DB_FILE, timeout=20)
		self.cursor = self.connection.cursor()

		if Table == 'homeautomation':
			sql = "DELETE FROM %s WHERE DeviceSerial ='%s'"% (Table, Serial)

		elif Table == 'rooms':
			sql = "DELETE FROM %s WHERE RoomName ='%s'"% (Table, roomName)

		else:
			sql = "DELETE FROM %s WHERE IP ='%s'"% (Table, IP)

		print sql
		self.cursor.execute(sql)
		self.connection.commit()
		self.cursor.close()
		return 


	def GetList(self, Table, roomName='', company='', devicetype='', ip='', type=''):

		self.result = {}
		self.connection = sqlite3.connect(core.DB_FILE, timeout=20)
		self.cursor = self.connection.cursor()
	
		if Table == 'homeautomation':
			if devicetype == 'interface':
				sql = "SELECT  DeviceCompany, DeviceTyp, Name , DeviceSerial , IP, ValueType, DeviceValue, DeviceVisible, Room FROM homeautomation WHERE DeviceTyp='interface'"			
			elif roomName == '' and company == '':
				sql = "SELECT DeviceCompany, DeviceTyp, Name , DeviceSerial , Room, ValueType, DeviceValue, DeviceVisible, IP FROM homeautomation ORDER BY OrderID"
			elif company !='':
				sql = "SELECT DeviceTyp , Name , DeviceSerial, Room, ValueType, DeviceValue, DeviceVisible FROM homeautomation WHERE DeviceCompany='%s'"% (company)
			else:
				sql = "SELECT DeviceCompany, DeviceTyp , Name , DeviceSerial , ValueType, DeviceValue, DeviceVisible FROM homeautomation WHERE Room='%s'"% (roomName)
		
		elif Table == 'multimedia':
			if roomName == '' and company == '':
				sql = "SELECT  DeviceCompany, IP, Name, Username, Password, ApiKey, Room FROM multimedia ORDER BY OrderID"
			elif company !='':
				sql = "SELECT DeviceCompany, IP, Name, Username, Password, ApiKey, Room FROM multimedia WHERE DeviceCompany='%s'"% (company)
			elif ip !='':
				sql = "SELECT DeviceCompany, IP, Name, Username, Password, ApiKey, FRoom ROM multimedia WHERE IP='%s'"% (ip)
			else:
				sql = "SELECT DeviceCompany, IP, Name, Username, Password, ApiKey FROM multimedia WHERE Room='%s'"% (roomName)

		elif Table == 'notification':
			sql = "SELECT DeviceCompany, IP, Name, Username, Password, ApiKey FROM notification ORDER BY OrderID"

		elif Table == 'web':
			if roomName == '' and company == '':
				sql = "SELECT DeviceCompany, Name, IP, Username, Password, ApiKey, Room FROM web ORDER BY OrderID"
			elif company !='':
				sql = "SELECT Name, IP, Username, Password, ApiKey, Room FROM web WHERE DeviceCompany='%s'"% (company)
			else:
				sql = "SELECT DeviceCompany, Name, IP, Username, Password, ApiKey FROM web WHERE Room='%s'"% (roomName)		
		
		elif Table == 'plugins':
			if type != '':
				sql = "SELECT Type, Name, Active FROM plugins WHERE Type='%s'"% (type)
			else:
				sql = "SELECT Type, Name, Active FROM plugins ORDER BY OrderID"
				
		log(sql, 'debug')	
		self.cursor.execute(sql)
		self.result = self.cursor.fetchall()
		self.cursor.close()
		return self.result

	def Update(self, Table, **kwargs):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "UPDATE %s SET %s"% (Table, kwargs)
		print sql
		cursor.execute(sql)
		connection.commit()
		cursor.close()
	    	return 


	def CeckDatabase(self):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		cursor.execute('CREATE TABLE IF NOT EXISTS interfaces (InterfaceID INTEGER, InterfaceSerial TEXT, InterfaceIP TEXT, InterfaceName TEXT ) ')
		cursor.execute('CREATE TABLE IF NOT EXISTS devices (OrderID INTEGER, DeviceCompany TEXT, DeviceTyp TEXT, DeviceName TEXT, DeviceSerial TEXT, RoomName TEXT, ValueType TEXT, DeviceValue TEXT, DeviceVisible INTEGER) ')
		cursor.execute('CREATE TABLE IF NOT EXISTS rooms (OrderID INTEGER, RoomName TEXT) ')
		cursor.execute('CREATE TABLE IF NOT EXISTS scenes (OrderID INTEGER, SceneName TEXT) ')
		cursor.execute('CREATE TABLE IF NOT EXISTS xbmc (OrderID INTEGER, XbmcIP TEXT, XbmcName TEXT, XbmcUsername TEXT, XbmcPassword TEXT, XbmcRoom TEXT) ')
		cursor.execute('CREATE TABLE IF NOT EXISTS sonos (OrderID INTEGER, SonosIP TEXT, SonosName TEXT, SonosRoom TEXT) ')
		cursor.execute('CREATE TABLE IF NOT EXISTS cams (OrderID INTEGER, CamIP TEXT, CamName TEXT, CamRoom TEXT) ')
		cursor.execute('CREATE TABLE IF NOT EXISTS plugins (OrderID INTEGER, Type TEXT, Name TEXT, Active INTEGER) ')
		cursor.execute('CREATE TABLE IF NOT EXISTS homeautomation (OrderID INTEGER, DeviceCompany TEXT, DeviceTyp TEXT, Name TEXT, DeviceSerial TEXT, IP TEXT, Room TEXT, ValueType TEXT, DeviceValue TEXT, DeviceVisible INTEGER) ')
		cursor.execute('CREATE TABLE IF NOT EXISTS multimedia (OrderID INTEGER, DeviceCompany TEXT, IP TEXT, Name TEXT, Username TEXT, Password TEXT, ApiKey TEXT, Room TEXT) ')
		cursor.execute('CREATE TABLE IF NOT EXISTS notification (OrderID INTEGER, DeviceCompany TEXT, IP TEXT, Name TEXT, Username TEXT, Password TEXT, ApiKey TEXT) ')
		cursor.execute('CREATE TABLE IF NOT EXISTS web (OrderID INTEGER, DeviceCompany TEXT, IP TEXT, Name TEXT, Username TEXT, Password TEXT, ApiKey TEXT, Room TEXT) ')
		connection.commit()
		cursor.close()
		log("Checking DB", 'info')


