import re
import socket

from core.Logger import log

def Replacesq(string):
	
	try:
		cleanstr = string.replace("'", "''")

	except AttributeError:
		cleanstr = string

	return cleanstr


def get_local_ip():

	# From http://stackoverflow.com/a/7335145

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            s.connect(('8.8.8.8', 9))
            ip = s.getsockname()[0]
        except socket.error as e:
            log('Can not get local ip : %s'% e, 'info')

        return ip


def ParseTyps(deviceSerial, description):

	data = {}
	serial = ''

	for items in description:
		for key, values in items.iteritems(): 
			if key == 'INDEX' and values == 1:
				for key, values in items.items():
					if key == 'PARENT':
						serial = values
					if key == 'PARENT_TYPE':
						name = values
					if key == 'TYPE':	
						type = values

					if serial == deviceSerial:
						data[deviceSerial] = name, type			

	return data