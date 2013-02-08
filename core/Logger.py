import os
import logging


def log(message, info_level):

	logging.basicConfig( 
				filename="homepy.log", 
				level = logging.DEBUG, 
				format = "%(asctime)s [%(levelname)-8s] %(message)s",
				datefmt = "%d.%m.%Y %H:%M:%S")  

	logger = getattr(logging, info_level)
	logger(message)