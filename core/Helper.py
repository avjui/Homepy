import re


def Replacesq(string):
	
	try:
		cleanstr = string.replace("'", "''")

	except:
		cleanstr = string

	return string