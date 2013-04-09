"""Implements generic utilities for monitoring classes.

"""

import sys
import re
import subprocess
import urllib, urllib2
import socket
import telnetlib


__author__ = "Ali Onur Uyar"
__copyright__ = "Copyright 2011, Ali Onur Uyar"
__credits__ = []
__license__ = "GPL"
__version__ = "0.9.12"
__maintainer__ = "Ali Onur Uyar"
__email__ = "aouyar at gmail.com"
__status__ = "Development"


buffSize = 4096
timeoutHTTP = 10


def parse_value(val, parsebool=False):
    """Parse input string and return int, float or str depending on format.
    
    @param val:       Input string.
    @param parsebool: If True parse yes / no, on / off as boolean.
    @return:          Value of type int, float or str.
        
    """
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except:
        pass
    if parsebool:
        if re.match('yes|on', str(val), re.IGNORECASE):
            return True
        elif re.match('no|off', str(val), re.IGNORECASE):
            return False
    return val
    

def safe_sum(seq):
    """Returns the sum of a sequence of numbers. Returns 0 for empty sequence 
    and None if any item is None.
    
    @param seq: Sequence of numbers or None.
    
    """
    if None in seq:
        return None
    else:
        return sum(seq)


def socket_read(fp):
    """Buffered read from socket. Reads all data available from socket.
    
    @fp:     File pointer for socket.
    @return: String of characters read from buffer.
    
    """
    response = ''
    oldlen = 0
    newlen = 0
    while True:
        response += fp.read(buffSize)
        newlen = len(response)
        if newlen - oldlen == 0:
            break
        else:
            oldlen = newlen
    return response


def exec_command(args, env=None):
    """Convenience function that executes command and returns result.
    
    @param args: Tuple of command and arguments.
    @param env:  Dictionary of environment variables.
                 (Environment is not modified if None.)
    @return:     Command output.
    
    """ 
    try:
        cmd = subprocess.Popen(args, 
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, 
                               bufsize=buffSize,
                               env=env)
    except OSError, e:
        raise Exception("Execution of command failed.\n",
                        "  Command: %s\n  Error: %s" % (' '.join(args), str(e)))
    out, err = cmd.communicate(None)
    if cmd.returncode != 0:
        raise Exception("Execution of command failed with error code: %s\n%s\n" 
                        % (cmd.returncode, err))
    return out


def get_url(url, user=None, password=None, params=None, use_post=False):
    if user is not None and password is not None:
        pwdmgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        pwdmgr.add_password(None, url, user, password)
        auth_handler = urllib2.HTTPBasicAuthHandler(pwdmgr)
        opener = urllib2.build_opener(auth_handler)
    else:
        opener = urllib2.build_opener()
    if params is not None:
        req_params = urllib.urlencode(params)
        if use_post:
            req_url = url
            data = req_params
        else:
            req_url = "%s?%s" % (url, req_params)
            data = None
    else:
        req_url = url
        data = None
    try:
        if sys.version_info[:2] < (2,6):
            resp = opener.open(req_url, data)
        else:
            resp = opener.open(req_url, data, timeoutHTTP)
    except urllib2.URLError, e:
        raise Exception("Retrieval of URL failed.\n"
                        "  url: %s\n  Error: %s" % (url, str(e)))
    return socket_read(resp)
        


class NestedDict(dict):
    """Dictionary class facilitates creation of nested dictionaries.
    
    This works:
        NestedDict d
        d[k1][k2][k3] ... = v
        
    """
    def __getitem__(self, key):
        """x.__getitem__(y) <==> x[y]"""
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            value = self[key] = type(self)()
            return value
        
    def set_nested(self, klist, value):
        """D.set_nested((k1, k2,k3, ...), v) -> D[k1][k2][k3] ... = v"""
        keys = list(klist)
        if len(keys) > 0:
            curr_dict = self
            last_key = keys.pop()
            for key in keys:
                if not curr_dict.has_key(key) or not isinstance(curr_dict[key], 
                                                                NestedDict):
                    curr_dict[key] = type(self)()
                curr_dict = curr_dict[key]
            curr_dict[last_key] = value

    
class SoftwareVersion(tuple):
    """Class for parsing, storing and comparing versions.
    
    All standard operations for tuple class are supported.
    
    """
    def __init__(self, version):
        """Initialize the new instance of class.
        
        @param version: Version must either be a string or a tuple of integers
                        or strings representing integers. 
    
        Version strings must begin with integer numbers separated by dots and 
        may end with any string.
        
        """
        self._versionstr = '.'.join([str(v) for v in self])
                   
    def __new__(cls, version):
        """Static method for creating a new instance which is a subclass of 
        immutable tuple type. Versions are parsed and stored as a tuple of 
        integers internally.
        
        @param cls:     Class
        @param version: Version must either be a string or a tuple of integers
                        or strings representing integers. 
    
        Version strings must begin with integer numbers separated by dots and 
        may end with any string.
        
        """
        if isinstance(version, basestring):
            mobj = re.match('(?P<version>\d+(\.\d+)*)(?P<suffix>.*)$', version)
            if mobj:
                version = [int(i) for i in mobj.groupdict()['version'].split('.')]
                return tuple.__new__(cls, version)
            else:
                raise ValueError('Invalid version string format.')
        else:
            try:
                return tuple.__new__(cls, [int(v) for v in version])
            except:
                raise TypeError("Version must either be a string or an iterable"
                                " of integers.")
        
    def __str__(self):
        """Returns string representation of version.
        
        """
        return self._versionstr


class TableFilter:
    """Class for filtering rows of tables based on filters on values of columns.
    
    The tables are represented as nested lists (list of lists of columns.)
    
    """
    
    def __init__(self):
        """Initialize Filter."""
        self._filters = {}
    
    def registerFilter(self, column, patterns, is_regex=False, 
                       ignore_case=False):
        """Register filter on a column of table.
        
        @param column:      The column name.
        @param patterns:    A single pattern or a list of patterns used for 
                            matching column values.
        @param is_regex:    The patterns will be treated as regex if True, the 
                            column values will be tested for equality with the
                            patterns otherwise.
        @param ignore_case: Case insensitive matching will be used if True.
        
        """
        if isinstance(patterns, basestring):
            patt_list = (patterns,)
        elif isinstance(patterns, (tuple, list)):
            patt_list = list(patterns)
        else:
            raise ValueError("The patterns parameter must either be as string "
                             "or a tuple / list of strings.")
        if is_regex:
            if ignore_case:
                flags = re.IGNORECASE
            else:
                flags = 0
            patt_exprs = [re.compile(pattern, flags) for pattern in patt_list]
        else:
            if ignore_case:
                patt_exprs = [pattern.lower() for pattern in patt_list]
            else:
                patt_exprs = patt_list
        self._filters[column] = (patt_exprs, is_regex, ignore_case)
                    
    def unregisterFilter(self, column):
        """Unregister filter on a column of the table.
        
        @param column: The column header.
        
        """
        if self._filters.has_key(column):
            del self._filters[column]
            
    def registerFilters(self, **kwargs):
        """Register multiple filters at once.
        
        @param **kwargs: Multiple filters are registered using keyword 
                         variables. Each keyword must correspond to a field name 
                         with an optional suffix:
                         field:          Field equal to value or in list of 
                                         values.
                         field_ic:       Field equal to value or in list of 
                                         values, using case insensitive 
                                         comparison.
                         field_regex:    Field matches regex value or matches
                                         with any regex in list of values.
                         field_ic_regex: Field matches regex value or matches
                                         with any regex in list of values 
                                         using case insensitive match.
        """
        for (key, patterns) in kwargs.items():
            if key.endswith('_regex'):
                col = key[:-len('_regex')]
                is_regex = True
            else:
                col = key
                is_regex = False
            if col.endswith('_ic'):
                col = col[:-len('_ic')]
                ignore_case = True
            else:
                ignore_case = False
            self.registerFilter(col, patterns, is_regex, ignore_case)
            
    def applyFilters(self, headers, table):
        """Apply filter on ps command result.
        
        @param headers: List of column headers.
        @param table:   Nested list of rows and columns.
        @return:        Nested list of rows and columns filtered using 
                        registered filters.
                        
        """
        result = []
        column_idxs = {}
        for column in self._filters.keys():
            try:
                column_idxs[column] = headers.index(column)
            except ValueError:
                raise ValueError('Invalid column name %s in filter.' % column)
        for row in table:
            for (column, (patterns, 
                          is_regex, 
                          ignore_case)) in self._filters.items():
                col_idx = column_idxs[column]
                col_val = row[col_idx]
                if is_regex:
                    for pattern in patterns:
                        if pattern.search(col_val):
                            break
                    else:
                        break
                else:
                    if ignore_case:
                        col_val = col_val.lower()
                    if col_val in patterns:
                        pass
                    else:
                        break
            else:
                result.append(row)
        return result
    

class Telnet(telnetlib.Telnet):
    
    __doc__ = telnetlib.Telnet.__doc__
    
    def __init__(self, host=None, port=0, socket_file=None, 
                 timeout=socket.getdefaulttimeout()):
        """Constructor.

        When called without arguments, create an unconnected instance.
        With a host argument, it connects the instance using TCP; port number 
        and timeout are optional, socket_file must be None.
        
        With a socket_file argument, it connects the instance using
        named socket; timeout is optional and host must be None.
        
        """
        telnetlib.Telnet.__init__(self, timeout=timeout)
        if host is not None or socket_file is not None:
            self.open(host, port, socket_file, timeout=timeout)
    
    def open(self, host=None, port=0, socket_file=None, 
             timeout=socket.getdefaulttimeout()):
        """Connect to a host.

        With a host argument, it connects the instance using TCP; port number 
        and timeout are optional, socket_file must be None. The port number
        defaults to the standard telnet port (23).
        
        With a socket_file argument, it connects the instance using
        named socket; timeout is optional and host must be None.

        Don't try to reopen an already connected instance.
        
        """
        self.socket_file = socket_file
        if host is not None:
            if sys.version_info[:2] >= (2,6):
                telnetlib.Telnet.open(self, host, port, timeout)
            else:
                telnetlib.Telnet.open(self, host, port)
        elif socket_file is not None:
            self.eof = 0
            self.host = host
            self.port = port
            self.timeout = timeout
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.settimeout(timeout)
            self.sock.connect(socket_file)
        else:
            raise TypeError("Either host or socket_file argument is required.")      
        