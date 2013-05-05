import os
import sqlite3
import threading
import json
import time

import core
from core.module.sonos.sonos import Sonos
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


	def AddSonos(self):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		devices = Sonos().GetDeviceList()		

		for sonos in devices:
			cursor = connection.cursor()
			cursor.execute('INSERT OR REPLACE INTO sonos (SonosIP, SonosName) VALUES(?,?)', (sonos[1], sonos[0].upper()))
			connection.commit()

		cursor.close()
		
		connection = sqlite3.connect(core.SONOS_DB_FILE, timeout=20)
		cursor = connection.cursor()

		for device in devices:
			
			sql = "CREATE TABLE IF NOT EXISTS '%s' (OrderID INTEGER, DeviceName TEXT, DeviceIP TEXT, Title TEXT, AlbumName TEXT, Artist TEXT, AlbumArt TEXT)"% (device[0].upper())
			cursor.execute(sql)
			connection.commit()
			sql = "INSERT OR REPLACE INTO '%s'(OrderID ,DeviceIP, DeviceName, Title, AlbumName, Artist, AlbumArt) VALUES (0, '', '', '', '', '', '')"% (device[0].upper())
			cursor.execute(sql)
			connection.commit()
		cursor.close()

		#Starting backgroundscan
		SonosBackground= threading.Timer(5,SonosDB().UpdateSonosTable)
		SonosBackground.start()

		return True

	def GetSonosList(self):


		result = []
		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "SELECT SonosIP, SonosName, SonosRoom FROM sonos"

		try:
			cursor.execute(sql)
			result = cursor.fetchall()
			cursor.close()
		    	return result	
		except:
			return result


	def UpdateSonosList(self, sonosName, sonosRoom):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "UPDATE sonos SET SonosRoom='%s' WHERE SonosName='%s'", (sonosRoom, sonosName)

		cursor.execute(sql)
		connection.commit()
		cursor.close()
	    	return 



	def RemoveSonos(self, sonosName):

		connection = sqlite3.connect(core.DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "DELETE FROM sonos WHERE SonosName = '" + sonosName + "'"
		cursor.execute(sql)
		connection.commit()
		cursor.close()

		connection = sqlite3.connect(core.SONOS_DB_FILE, timeout=20)
		cursor = connection.cursor()

		sql = "DROP TABLE IF EXISTS '" + sonosName + "'"

		cursor.execute(sql)
		connection.commit()
		cursor.close()
		log('Remove sonos device with %s Name from DB'% (sonosName), 'info')
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

		sql = "INSERT INTO cams (CamIP, CamName, CamRoom) VALUES('%s','%s', '%s')"% (camIP, camName, roomName)
		
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

	def Add(self, Table, Company='', Serial='', Name='', Type='', roomName='',Value='', ValueType=0, IP='', Username='', Password='', ApiKey='', hidden=1):

		self.i = 0
		self.Type = Type
		self.Serial = dSerial
		self.roomID = int(self.getCountID('devices', 'OrderID' ))
		
		self.value = Value

		self.deviceName = Name.upper()
		self.roomName = roomName.upper()
		
		self.connection = sqlite3.connect(core.DB_FILE, timeout=20)
		self.cursor = self.connection.cursor()

		if table == 'homeautomation':
		
			for self.serial in self.deviceSerial:
				if not self.serial.endswith(':0'):
					self.size = len(self.deviceSerial)
					if self.size > 2:
						self.i = self.i + 1
						self.cursor.execute('INSERT INTO homeautomation(OrderID, DeviceCompany, DeviceTyp, DeviceName, DeviceSerial, IP, RoomName, ValueType, DeviceValue, DeviceVisible) VALUES(?,?,?,?,?,?,?,?,?,?)', (self.roomID ,Company, self.deviceType, self.deviceName + "(" + str(self.i) + ")", self.serial, IP, self.roomName, ValueTypy, '0.0', hidden))
					self.connection.commit()
				else:
					self.cursor.execute('INSERT INTO homeautomation(OrderID, DeviceCompany, DeviceTyp, DeviceName, DeviceSerial, IP, RoomName, ValueType, DeviceValue, DeviceVisible) VALUES(?,?,?,?,?,?,?,?,?,?)', (self.roomID ,Company, self.deviceType, self.deviceName, self.serial, IP, self.roomName, ValueTypy, '0.0', hidden))
					self.connection.commit()
	
		elif table == 'multimedia':

			cursor.execute('INSERT INTO xbmc (IP, Name, Username, Password, ApiKey, Room) VALUES(?,?,?,?,?)', (IP, Name, Username, Password, ApiKey, Room))
			connection.commit()

		elif table == 'web':

			sql = "INSERT INTO web (IP, Name, Username, Password, ApiKey, Room) VALUES('%s','%s', '%s')"% (IP, Name, Username, Password, ApiKey, Room)
			cursor.execute(sql)
			connection.commit()

		self.cursor.close()
		return True

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
		cursor.execute('CREATE TABLE IF NOT EXISTS homeautomation (OrderID INTEGER, DeviceCompany TEXT, DeviceTyp TEXT, DeviceName TEXT, DeviceSerial TEXT, IP TEXT, RoomName TEXT, ValueType TEXT, DeviceValue TEXT, DeviceVisible INTEGER) ')
		cursor.execute('CREATE TABLE IF NOT EXISTS multimedia(OrderID INTEGER, IP TEXT, Name TEXT, Username TEXT, Password TEXT, ApiKey TEXT, Room TEXT) ')
		cursor.execute('CREATE TABLE IF NOT EXISTS web (OrderID INTEGER, IP TEXT, Name TEXT, Username TEXT, Password TEXT, ApiKey TEXT, Room TEXT) ')
		connection.commit()
		cursor.close()
		log("Checking DB", 'info')


	
class SonosDB:


	def UpdateSonosTable(self):

		try:
			devices = Sonos().GetTrackInfo()
		
			connection = sqlite3.connect(core.SONOS_DB_FILE, timeout=20)
			cursor = connection.cursor()

			for key,device in devices.iteritems():

				title = Replacesq(device[3])
				albumname = Replacesq(device[4])
				artist = Replacesq(device[5])
				
		
				sql = "UPDATE '%s' SET DeviceIP='%s', DeviceName='%s', Title='%s', AlbumName='%s', Artist='%s', AlbumArt='%s' WHERE OrderID=0"% (device[0].upper(), device[1], device[0], title , albumname, artist,device[2])
				cursor.execute(sql)
				connection.commit()
	
			cursor.close()
			log('Sonos table was updatet', 'debug')

		except Exception,e:
			log(e, 'error')	


	def GetZoneInfo(self, zoneName=''):

		self.data = {}

		self.devices = DBFunction().GetSonosList()
				
		self.connection = sqlite3.connect(core.SONOS_DB_FILE, timeout=20)
		self.cursor = self.connection.cursor()

		for self.device in self.devices:

			self.sql = "SELECT DeviceName, DeviceIP, AlbumArt, Title, AlbumName, Artist  FROM '%s'"% (self.device[1].upper())
			self.cursor.execute(self.sql)
			self.result = self.cursor.fetchall()
			self.data[self.device[1]] = self.result 

		self.cursor.close()
		return self.data

	

		

	


				

		
