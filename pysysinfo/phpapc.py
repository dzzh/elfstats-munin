"""Implements APCinfo Class for gathering stats from Alternative PHP Accelerator.

The statistics are obtained through a request to custom apcinfo.php script
that must be placed in the Web Server Document Root Directory.

"""

import util

__author__ = "Ali Onur Uyar"
__copyright__ = "Copyright 2011, Ali Onur Uyar"
__credits__ = []
__license__ = "GPL"
__version__ = "0.9.23"
__maintainer__ = "Ali Onur Uyar"
__email__ = "aouyar at gmail.com"
__status__ = "Development"


defaultHTTPport = 80
defaultHTTPSport = 443


class APCinfo:
    """Class to retrieve stats from APC from Web Server."""

    def __init__(self, host=None, port=None, user=None, password=None,
                 monpath=None, ssl=False, extras=False, autoInit=True):
        """Initialize URL for APC stats access.
        
        @param host:     Web Server Host. (Default: 127.0.0.1)
        @param port:     Web Server Port. (Default: 80, SSL: 443)
        @param user:     Username. (Not needed unless authentication is required 
                         to access status page.
        @param password: Password. (Not needed unless authentication is required 
                         to access status page.
        @param monpath:  APC status script path relative to Document Root.
                         (Default: apcinfo.php)
        @param ssl:      Use SSL if True. (Default: False)
        @param extras:   Include extra metrics, which can be computationally more 
                         expensive.
        @param autoInit: If True connect to Web Server on instantiation.
            
        """
        if host is not None:
            self._host = host
        else:
            self._host = '127.0.0.1'
        if port is not None:
            self._port = int(port)
        else:
            if ssl:
                self._port = defaultHTTPSport
            else:
                self._port = defaultHTTPport
        self._user = user
        self._password = password
        if ssl:
            self._proto = 'https'
        else:
            self._proto = 'http'
        if monpath:
            self._monpath = monpath
        else:
            self._monpath = 'apcinfo.php'
        self._extras = extras
        self._statusDict = None
        if autoInit:
            self.initStats()

    def initStats(self, extras=None):
        """Query and parse Web Server Status Page.
        
        @param extras: Include extra metrics, which can be computationally more 
                       expensive.
        
        """
        if extras is not None:
            self._extras = extras
        if self._extras:
            detail = 1
        else:
            detail = 0
        url = "%s://%s:%d/%s?detail=%s" % (self._proto, self._host, self._port, 
                                           self._monpath, detail)
        response = util.get_url(url, self._user, self._password)
        self._statusDict = {}
        for line in response.splitlines():
            cols = line.split(':')
            if not self._statusDict.has_key(cols[0]):
                self._statusDict[cols[0]] = {}
            self._statusDict[cols[0]][cols[1]] = util.parse_value(cols[2])
    
    def getMemoryStats(self):
        """Return Memory Utilization Stats for APC.
        
        @return: Dictionary of stats.
        
        """
        return self._statusDict.get('memory');
    
    def getSysCacheStats(self):
        """Return System Cache Stats for APC.
        
        @return: Dictionary of stats.
        
        """
        return self._statusDict.get('cache_sys');
    
    def getUserCacheStats(self):
        """Return User Cache Stats for APC.
        
        @return: Dictionary of stats.
        
        """
        return self._statusDict.get('cache_user');

    def getAllStats(self):
        """Return All Stats for APC.
        
        @return: Nested dictionary of stats.
        
        """
        return self._statusDict;
