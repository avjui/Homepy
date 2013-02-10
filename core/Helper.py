import re
import socket


def Replacesq(string):
	
	try:
		cleanstr = string.replace("'", "''")

	except:
		cleanstr = string

	return string


def get_local_ip():

	# From http://stackoverflow.com/a/7335145

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            s.connect(('8.8.8.8', 9))
            ip = s.getsockname()[0]
        except socket.error:
            raise
        finally:
            del s

        return ip