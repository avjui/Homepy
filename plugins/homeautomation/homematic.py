import os, sys
from core.PluginManager import _Plugin

class client(_Plugin):
    name = 'Homematic'

    def get_name(self):
        return self.name