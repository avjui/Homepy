#
# -*- coding: <utf-8> -*-
#

import os
import sys

import cherrypy
from cherrypy.process.plugins import Daemonizer
from lib.configobj import ConfigObj

import core
from core.webserver import WebInterface


def start():


	cherrypy.config.update({
				'log.screen':			False,
				'server.thread_pool': 	10,
				'server.socket_port': 	core.HTTP_PORT,
				'server.socket_host': 	core.HTTP_HOST,
				'engine.autoreload_on':	True,
		})

	conf = {
		'/': {
			'tools.staticdir.root': os.path.join(core.PROG_DIR, 'data'),
		},

		'/interfaces':{
			'tools.staticdir.on': True,
			'tools.staticdir.dir': "interfaces"
		},

		'/cache':{
			'tools.staticdir.on': True,
			'tools.staticdir.dir': "cache"
		},

		'/images':{
			'tools.staticdir.on': True,
			'tools.staticdir.dir': "interfaces/default/images"
		},

		'/css':{
			'tools.staticdir.on': True,
			'tools.staticdir.dir': "interfaces/default/css"
		},

		'/js':{
			'tools.staticdir.on': True,
			'tools.staticdir.dir': "interfaces/default/js"
		},
	}
    
	if core.HTTP_PASSWORD != "":
		conf['/'].update({
			'tools.auth_basic.on': True,
	   		'tools.auth_basic.realm': 'homepy',
    			'tools.auth_basic.checkpassword':  cherrypy.lib.auth_basic.checkpassword_dict({core.HTTP_USERNAME:core.HTTP_PASSWORD})
		})
		

	# Prevent time-outs
	cherrypy.engine.timeout_monitor.unsubscribe()
		
	cherrypy.tree.mount(WebInterface(), config = conf)
	if core.PROG_DAEMONIZE:
		daemon = Daemonizer(cherrypy.engine)
		daemon.subscribe()

	#Make cherrypy silence
	cherrypy.log.access_log.propagate = False

	#cherrypy.process.servers.check_port(core.HTTP_HOST, core.HTTP_PORT)
	cherrypy.engine.start()
	cherrypy.engine.block
	cherrypy.server.wait()
