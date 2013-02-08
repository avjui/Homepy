#
# -*- coding: <utf-8> -*-
#
import urllib

from lib.sonos.soco import SoCo
from lib.sonos.soco import SonosDiscovery

from core.Logger import log

sonos_devices = SonosDiscovery()

class Sonos:

	def GetDeviceList(self):
		
		info = {}
		for ip in sonos_devices.get_speaker_ips():
			device = SoCo(ip)
			zone_name = device.get_speaker_info()['zone_name']
			if zone_name != None:
				info[zone_name] = ip

		

		log('Function [GetDeviceList: ' + str(info.items()) + ']', 'debug')
		return info.items()

	def GetTrackInfo(self):

		art = {}
		sonoslist = self.GetDeviceList()
		#try:
		for sonos in sonoslist:
				sonosdevice = SoCo(sonos[1])
				track = sonosdevice.get_current_track_info()
				album_art_url = track['album_art']
				try:
					album_artist = track['artist']
				except:
					album_artist = ""
				try:
					title = track['title']
				except:
					title = ""
				try:
					album = track['album']
				except:
					album = ""
					

				
				# Cache the file
				filename = "/mnt/Media/Downloads/Homematic/data/cache/%s.jpg"% (sonos[0])

				try:
					f = open(filename,'wb')
					f.write(urllib.urlopen(album_art_url).read())
					f.close()
					album_art_url = "cache/%s.jpg"% (sonos[0])
				except:
					album_art_url = "cache/nocover.png"

				art[sonos[0]] = sonos[0], sonos[1], album_art_url, title, album, album_artist 
				
		#except:
		#	return 
		log('Function [GetTrackInfo :' + str(art) + ']', 'debug')
		return art


	def SonosFunctions(self, zonenip, function):
		
		sonos = SoCo(zonenip)

		func = getattr(sonos,function)
		func()
		log('Function %s for %s IP', 'debug'), (function, zonenip) 

		