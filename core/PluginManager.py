import os
import sys

from core.DBFunctions import DBFunction
from core.Logger import log


'''
Code came from http://yannik520.github.io/python_plugin_framework.html
'''

class _Plugin(object):
     
     class __metaclass__(type):
        def __init__(cls,name, bases, attrs):
            if not hasattr(cls, 'plugins'):
                cls.plugins = {}
            else:
                cls.plugins[attrs['__module__']] = cls


        def show_plugins(cls):
            for kls in cls.plugins.values():
                    print kls
        def get_plugins(cls):
            return cls.plugins


class PluginMgr(object):
    plugin_dirs = { }
    # make the manager class as singleton
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PluginMgr, cls).__new__(cls, *args, **kwargs)

        return cls._instance
    def __init__(self):

        self.plugin_dirs.update({
                                 'plugins/homeautomation/' : False,
                                 'plugins/multimedia/' : False,
                                 'plugins/web/' : False,
                                 })

    def _load_all(self):
        for (pdir, loaded) in self.plugin_dirs.iteritems():
            if loaded: continue

            sys.path.insert(0, pdir)
            for mod in [x[:-3] for x in os.listdir(pdir) if x.endswith('.py')]:
                if mod and mod != '__init__':
                    if mod in sys.modules:
                        log('Module %s already exists, skip' % mod, 'info')
                    else:
                        try:
                            pymod = __import__(mod)
                            self.plugin_dirs[pdir] = True
                            log("Plugin Found [Name] %s	[Path] %s"% (mod, pymod.__file__), 'info')
                            DBFunction().AddPlugin(mod, pymod.__file__.split('/')[1])
                        except ImportError, e:
                            log ('Loading failed, skip plugin %s/%s' % (os.path.basename(pdir), mod), 'error')

            del(sys.path[0])


    def get_plugins(self):
        """ the return value is dict of name:class pairs """
        self._load_all()
        return _Plugin.get_plugins()



pluginmgr = PluginMgr()


         