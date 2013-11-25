#!/usr/bin/env python
#
# -*- coding: <utf-8> -*-

import os
import sys
import locale
import socket
import time
import thread
from optparse import OptionParser

#cherrypy
import cherrypy
from cherrypy import server
from cherrypy.process.plugins import PIDFile

#libs
from lib.configobj import ConfigObj

#core
import core
import core.base 
from core.Config import Config
from core.DBFunctions import DBFunction
from core.Logger import log


from core.PluginManager import *

# Fixed paths to Headphones
if hasattr(sys, 'frozen'):
	core.ABS_PATH = os.path.abspath(sys.executable)
else:
	core.ABS_PATH = os.path.abspath(__file__)
    
core.PROG_DIR = os.path.dirname(core.ABS_PATH)

locale.setlocale(locale.LC_ALL, '')

def main():
       
    # Set up and gather command line arguments
    usage = "usage: %prog [-options] [arg]"
    p = OptionParser(usage=usage)

    p.add_option('-d', '--daemonize', action = "store_true",
                 dest = 'daemonize', help = "Run the server as a daemon")
    p.add_option('-p', '--pidfile',
                 dest = 'pidfile', default = None,
                 help = "Store the process id in the given file")
    p.add_option('-P', '--port',
                 dest = 'port', default = None,
                 help = "Force webinterface to listen on this port")

    options, args = p.parse_args()

    # Daemonize
    if options.daemonize:
       print "------------------- Preparing to run in daemon mode -------------------"
       #LogEvent("Preparing to run in daemon mode")  
       core.PROG_DAEMONIZE = True

    # Set port
    if options.port:
        print "------------------- Port manual set to " + options.port + " -------------------"
        core.HTTP_PORT = int(options.port)

	 
    # PIDfile
    if options.pidfile:
        print "------------------- Set PIDfile to " + options.pidfile + " -------------------"
        PIDFile(cherrypy.engine, options.pidfile).subscribe()

   
    # Set config file
    core.CONFIG_FILE = os.path.join(core.PROG_DIR, 'config.ini')
   
    # Set Database file
    core.DB_FILE = os.path.join(core.PROG_DIR, 'homepy.db')

    core.CFG = ConfigObj(core.CONFIG_FILE, encoding='UTF8')
 

    # Check and read config 
    Config().Check()
    log("Checking configfile", 'info')

    # Check DB
    try:
         DBFunction().CeckDatabase()
    except Exception, e:
         log(e,'error')


    # Gogogo

    try:
         # Initial and start the Plugins
         log('Initial Plugins', 'info')
         plugins = pluginmgr.get_plugins()
         for key in plugins:
              plugin = pluginmgr.get_plugins()[key]		
              plugin().start()
         core.base.start()
         while True: time.sleep(100)
         

    except KeyboardInterrupt:
         log('Homepy is shutting down ....', 'info')
         cherrypy.engine.exit()
         for key in plugins:
              plugin = pluginmgr.get_plugins()[key]		
              plugin().shutdown()
         sys.exit
    


if __name__ == "__main__":

	main()

	


