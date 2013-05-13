#
# -*- coding: <utf-8> -*-
#
import urllib2
import os
import thread
import time
import sqlite3

from lib.sonos.soco import SoCo
from lib.sonos.soco import SonosDiscovery
import lib.feedparser as feedparser

import core
from core.Logger import log
from core.PluginManager import Multimedia
from core.Helper import Replacesq
from core.DBFunctions import DBFunction



class Sonos(Multimedia):

	sonos_devices = SonosDiscovery()
	adding = True
	SONOS_DB = os.path.join(core.PROG_DIR, 'sonos.db')

	def start(self):

		self.manufactur = 'SONOS'
		
		for sonos in self._GetDeviceList():
			self.name = sonos[0]
			self.ip = sonos[1]			
			self.existing_devices = DBFunction().GetList('multimedia', company='SONOS')
			for d in self.existing_devices:
				if d[1] == self.ip:
					self.adding = False
					break
				else:
					self.adding = True

			if self.adding:		
				DBFunction().Add('multimedia', self.manufactur, '', self.name, '', '', '', '', self.ip, '', '', '', 0)
				self._CreateSonosTable(self._GetDeviceList())
				log('Found some new sonos device : %s - %s'% (self.name, self.ip), 'info')
				print('Found some sonos device : %s - %s'% (self.name, self.ip))

		self._BackgroundCheck()	
				

	def action(self, zonenip, function, value=''):
		
		self.sonos = SoCo(zonenip)

		self.func = getattr(self.sonos,function)
		if value == '':
			self.func()
		else:
			self.func(value)
		log('Function %s for %s IP'% (function, zonenip), 'debug')

	def get_mediainfo(self):

		self.result = self._GetZoneInfo()
		return self.result

	def _BackgroundCheck(self):

		thread.start_new_thread(self._UpdateSonosTable, ())
		log('SONOS background update thread was started', 'debug') 

	def _GetDeviceList(self):
		
		self.info = {}
		for self.ip in self.sonos_devices.get_speaker_ips():
			self.device = SoCo(self.ip)
			self.zone_name = self.device.get_speaker_info()['zone_name']
			if self.zone_name != None:
				self.info[self.zone_name] = self.ip

		

		log('Function [GetDeviceList: %s ]'% (self.info.items()), 'debug')
		return self.info.items()

	def _GetTrackInfo(self):

		self.art = {}
		sonoslist = self._GetDeviceList()
		#try:
		for sonos in sonoslist:

				sonosdevice = SoCo(sonos[1])
				self.track = sonosdevice.get_current_track_info()
				self.serial = sonosdevice.get_speaker_info()['serial_number']
				self.volume = sonosdevice.volume()


				self.album_art_url = self.track['album_art'].encode('utf-8')
				log('Album cover : %s' % self.album_art_url, 'debug')
				try:
					self.album_artist = self.track['artist'].encode('utf-8')
				except:
					self.album_artist = ""
				try:
					self.title = self.track['title'].encode('utf-8')
				except:
					self.title = ""
				try:
					self.album = self.track['album'].encode('utf-8')
				except:
					self.album = ""
				try:
					self.duration = self.track['duration'].encode('utf-8')
				except:
					self.duration = "0:00:00"
				try:
					self.position = self.track['position'].encode('utf-8')
				except:
					self.position = "0:00:00"



				if self.track['duration'] == '0:00:00' and self.album == '':
				
					try:
						""" First we must parse the streamurl from 1400:status/radiolog
						 to become the id from stream. After that we can parse the logo information
						from opml.radiotime.com """

						self.url = "http://" + str(sonos[1]) + ":1400/status/radiolog"
						self.response = urllib2.urlopen(self.url, timeout=20)
						self.data = self.response.read()
						self.response.close()

						self.r = feedparser.parse(self.data)
						self.stream = self.r.entries[0]['href']		 
						self.id = self.stream.split('&')[0].split('?')[1]
						self.xml= "http://opml.radiotime.com/Describe.ashx?c=nowplaying&%s&partnerId=Sonos&serial=%s"% (self.id, self.serial)

						self.response = urllib2.urlopen(self.xml, timeout=20)
						self.data = self.response.read()
						self.response.close()

						self.album_art_url= feedparser.parse(self.data).feed['summary']
						self.album_art_url = self.album_art_url.split(' ')[0].replace('.png', 'q.png')

					except:
						pass						

				
				# Cache the file
				filename = "/mnt/Media/Downloads/Homematic/data/cache/%s.jpg"% (sonos[0])

				try:
					f = open(filename,'wb')
					f.write(urllib2.urlopen(self.album_art_url, timeout=20).read())
					f.close()
					self.album_art_url = "cache/%s.jpg"% (sonos[0])
				except:
					self.album_art_url = "cache/nocover.png"
			
					
				self.art[sonos[0]] = sonos[0], sonos[1], self.album_art_url, self.title, self.album, self.album_artist, self.duration, self.position, self.volume
				
		#except:
		#	return 
		log('Function [GetTrackInfo : %s ]'% (self.art), 'debug')
		return self.art

	def _CreateSonosTable(self, devices):

		self.connection = sqlite3.connect(self.SONOS_DB, timeout=20)
		self.cursor = self.connection.cursor()

		for device in devices:
			
			sql = "CREATE TABLE IF NOT EXISTS '%s' (OrderID INTEGER, DeviceName TEXT, DeviceIP TEXT, Title TEXT, AlbumName TEXT, Artist TEXT, AlbumArt TEXT, Duration Text, Position TEXT, Volume TEXT)"% (device[0].upper())
			self. cursor.execute(sql)
			self.connection.commit()
			sql = "INSERT OR REPLACE INTO '%s'(OrderID ,DeviceIP, DeviceName, Title, AlbumName, Artist, AlbumArt, Duration, Position, Volume) VALUES (0, '', '', '', '', '', '', '', '', '0')"% (device[0].upper())
			self.cursor.execute(sql)
			self.connection.commit()
		self.cursor.close()


	def _UpdateSonosTable(self):

		try:
			while True:
				self.devices = self._GetTrackInfo()
		
				self.connection = sqlite3.connect(self.SONOS_DB, timeout=20)
				self.cursor = self.connection.cursor()

				for key,device in self.devices.iteritems():
	
					self.title = Replacesq(device[3])
					self.albumname = Replacesq(device[4])
					self.artist = Replacesq(device[5])
				
			
					sql = "UPDATE '%s' SET DeviceIP='%s', DeviceName='%s', Title='%s', AlbumName='%s', Artist='%s', AlbumArt='%s', Duration='%s', Position='%s', Volume='%s' WHERE OrderID=0"% (device[0].upper(), device[1], device[0], self.title , self.albumname, self.artist, device[2], device[6], device[7], device[8])
					self.cursor.execute(sql)
					self.connection.commit()
	
				self.cursor.close()
				log('Sonos table was updatet!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!', 'debug')
				time.sleep(5)

		except Exception,e:
			log(e, 'error')	


	def _GetZoneInfo(self, zoneName=''):

		self.data = {}

		self.devices = DBFunction().GetList('multimedia', company='SONOS')
				
		self.connection = sqlite3.connect(self.SONOS_DB, timeout=20)
		self.cursor = self.connection.cursor()

		for self.device in self.devices:

			self.sql = "SELECT DeviceName, DeviceIP, AlbumArt, Title, AlbumName, Artist, Duration, Position, Volume  FROM '%s'"% (self.device[2].upper())
			self.cursor.execute(self.sql)
			self.result = self.cursor.fetchall()
			#print self.result
	 		for record in self.result:
				self.resultdic = ({'mediatyp' : 'audio',
							'devicename' : record[0],
							'deviceip' : record[1],
							'artist' : record[5], 
			       			'album' : record[4],
							'title' : record[3],
							'cover' : record[2],
							'duration' : record[6],
							'position' : record[7],
							'volume' : record[8],
						})	
			#print self.resultdic
			self.data[self.device[1]] = self.resultdic 

		self.cursor.close()
		return self.data