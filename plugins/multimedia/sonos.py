#
# -*- coding: <utf-8> -*-
#
import urllib2

from lib.sonos.soco import SoCo
from lib.sonos.soco import SonosDiscovery
import lib.feedparser as feedparser

from core.Logger import log
from core.PluginManager import Multimedia
from core.Helper import Replacesq
from core.DBFunctions import DBFunction



class Sonos(Multimedia):

	sonos_devices = SonosDiscovery()
	adding = True
	
	def start(self):

		self.sonos_devices = Sonos()._GetDeviceList()
		self.manufactur = 'SONOS'
		
		for sonos in self.sonos_devices:
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
				log('Found some new sonos device : %s - %s'% (self.name, self.ip), 'info')
				print('Found some sonos device : %s - %s'% (self.name, self.ip))

	def action(self, zonenip, function, value=''):
		
		self.sonos = SoCo(zonenip)

		self.func = getattr(self.sonos,function)
		if value == '':
			self.func()
		else:
			self.func(value)
		log('Function %s for %s IP'% (function, zonenip), 'debug')


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
		sonoslist = self.GetDeviceList()
		#try:
		for sonos in sonoslist:

				sonosdevice = SoCo(sonos[1])
				self.track = sonosdevice.get_current_track_info()
				self.serial = sonosdevice.get_speaker_info()['serial_number']



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
			
					
				self.art[sonos[0]] = sonos[0], sonos[1], self.album_art_url, self.title, self.album, self.album_artist 
				
		#except:
		#	return 
		log('Function [GetTrackInfo : %s ]'% (self.art), 'debug')
		return self.art

	def _UpdateSonosTable(self):

		try:
			self.devices = Sonos().GetTrackInfo()
		
			self.connection = sqlite3.connect(core.SONOS_DB_FILE, timeout=20)
			self.cursor = self.connection.cursor()

			for key,device in self.devices.iteritems():

				self.title = Replacesq(device[3])
				self.albumname = Replacesq(device[4])
				self.artist = Replacesq(device[5])
				
		
				sql = "UPDATE '%s' SET DeviceIP='%s', DeviceName='%s', Title='%s', AlbumName='%s', Artist='%s', AlbumArt='%s' WHERE OrderID=0"% (device[0].upper(), device[1], device[0], self.title , self.albumname, self.artist, device[2])
				self.cursor.execute(sql)
				self.connection.commit()
	
			self.cursor.close()
			log('Sonos table was updatet', 'debug')

		except Exception,e:
			log(e, 'error')	


	def _GetZoneInfo(self, zoneName=''):

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