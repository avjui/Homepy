#
# -*- coding: <utf-8> -*-
#
import urllib2

from lib.sonos.soco import SoCo
from lib.sonos.soco import SonosDiscovery
import lib.feedparser as feedparser

from core.Logger import log
from core.PluginManager import _Plugin



class Sonos(_Plugin):

	name = 'Test'
	type = 'multimedia'
	sonos_devices = SonosDiscovery()

	def GetDeviceList(self):
		
		self.info = {}
		for self.ip in sonos_devices.get_speaker_ips():
			self.device = SoCo(self.ip)
			self.zone_name = self.device.get_speaker_info()['zone_name']
			if self.zone_name != None:
				self.info[self.zone_name] = self.ip

		

		log('Function [GetDeviceList: %s ]'% (self.info.items()), 'debug')
		return self.info.items()

	def GetTrackInfo(self):

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


	def SonosFunctions(self, zonenip, function, value=''):
		
		sonos = SoCo(zonenip)

		func = getattr(sonos,function)
		if value == '':
			func()
		else:
			func(value)
		log('Function %s for %s IP'% (function, zonenip), 'debug')

		