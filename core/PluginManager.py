import os

import core
import core.DBFunctions.DBFunction as DBFunction
import core.Logger as Logger

class PluginHomeautomation(object):
    '''
    This is a construct for homeautomation plugins
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.company = 'None'
        self.name = 'Homeautomation'
        self.serial = 'None'
        self.type = 'None'
        self.roomName = ''
        DBFunction.AddDevice(self.serial, self.name, self.type, self.roomName, self.company)

        
    def status(self):
        '''
        This return the staus of dives(es) in a dict
        '''
        
        self.status = {}    
        return  self.status
    
    def switch(self):
        '''
        This switch a specified device
        '''
        
        return False
    
    def dim(self): 
        '''
        This dim a specified device
        '''
        
        return False
    
    def add(self):
        '''
        Add device to config
        '''
        
        return False
    
    def remove(self):
        '''
        Remove device from config
        '''
        
        return False
    
class PluginMultimedia(object):
    '''
    This is a construct for multimedia plugins
    '''      

    def __init__(self):
        '''
        Constructor
        '''
        
        self.company = 'None'
        self.name = 'Homeautomation'
        self.roomName = ''
        
    def status(self):
        '''
        Get status of device
        '''
        
        return False
    
    def add(self):
        '''
        Add device to configuration
        '''    
        
        return False
    
    def remove(self):
        '''
        Remove device from configuration
        '''
        
        return False
    
    def action(self):
        
        return False
    
        
class Plugins(object):
    
    def __init__(self):
        self.path = core.ABS_PATH
        self.plugindir = 'module'
        
        
    
    
         
         
         