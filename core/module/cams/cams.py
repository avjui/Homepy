#
# -*- coding: <utf-8> -*-
#
import os
import urllib

import core
#from core.Logger import log

class Cam():

	def UpdateCamPicture(self, camIP, camName):

		# Cache the file
		filename = os.path.join(core.PROG_DIR, '/data/cache/%s.jpg'% (camName))

		try:
			f = open(filename,'wb')
			f.write(urllib.urlopen(camIP).read())
			f.close()
			self.campic= "cache/%s.jpg"% (camName)
		except:
			self.campic = "cache/nopic.png"

			
