#
# -*- coding: <utf-8> -*-
#
import urllib

import core
from core.Logger import log

class Cam()

	def UpdateCamPicture(self, camIP, camName):

		# Cache the file
		filename = os.path.join(core.PROG_DIR, '/data/cache/%s.jpg'% (camName))

		try:
			f = open(filename,'wb')
			f.write(urllib.urlopen(camip).read())
			f.close()
			campic= "cache/%s.jpg"% (sonos[0])
		except:
			campic = "cache/nopic.png"

