"""Implements PgInfo Class for gathering stats from PostgreSQL Database Server.

The statistics are obtained by connecting to and querying local and/or 
remote PostgreSQL Servers. 

"""

import util
import psycopg2.extras

__author__ = "Ali Onur Uyar"
__copyright__ = "Copyright 2011, Ali Onur Uyar"
__credits__ = []
__license__ = "GPL"
__version__ = "0.9.19"
__maintainer__ = "Ali Onur Uyar"
__email__ = "aouyar at gmail.com"
__status__ = "Development"


defaultPGport = 5432


class PgInfo:
    """Class to retrieve stats for PostgreSQL Database"""
    
    lockModes = ('AccessExclusive', 'Exclusive', 'ShareRowExclusive', 
                 'Share', 'ShareUpdateExclusive', 'RowExclusive', 
                 'RowShare', 'AccessShare',)

    def __init__(self, host=None, port=None,
                 database=None, user=None, password=None, autoInit=True):
        """Initialize connection to PostgreSQL Database.
        
        @param host:     PostgreSQL Host
                         (Defaults to UNIX socket if not provided.)
        @param port:     PostgreSQL Port
                         (Defaults to 5432 for network connections.)
        @param database: PostgreSQL Database
                         (The default is the login the for connecting user.)
        @param user:     PostgreSQL User
                         (The default is the login of OS user for UNIX sockets.
                         Must be specified for network connections.)
        @param password: PostgreSQL Password
                         (Attempt login without password by default.)
        @param autoInit: If True connect to PostgreSQL Database on instantiation.
            
        """
        self._conn = None
        self._connParams = {}
        self._version = None
        self._conn = None
        if host is not None:
            self._connParams['host'] = host
            if port is not None:
                self._connParams['port'] = int(port)
            else:
                self._connParams['port'] = defaultPGport
        elif port is not None:
            self._connParams['host'] = '127.0.0.1'
            self._connParams['port'] = int(port)
        if database is not None:
            self._connParams['database'] = database
        if user is not None:
            self._connParams['user'] = user
            if password is not None:
                self._connParams['password'] = password
        if autoInit:
            self._connect()
        
    def __del__(self):
        """Cleanup."""
        if self._conn is not None:
            self._conn.close()
            
    def _connect(self):
        """Establish connection to PostgreSQL Database."""
        if self._connParams:
            self._conn = psycopg2.connect(**self._connParams)
        else:
            self._conn = psycopg2.connect('')
        try:
            ver_str = self._conn.get_parameter_status('server_version')
        except AttributeError:
            ver_str = self.getParam('server_version')
        self._version = util.SoftwareVersion(ver_str)
    
    def _createStatsDict(self, headers, rows):
        """Utility method that returns database stats as a nested dictionary.
        
        @param headers: List of columns in query result.
        @param rows:    List of rows in query result.
        @return:        Nested dictionary of values.
                        First key is the database name and the second key is the 
                        statistics counter name. 
            
        """
        dbstats = {}
        for row in rows:
            dbstats[row[0]] = dict(zip(headers[1:], row[1:]))
        return dbstats
    
    def _createTotalsDict(self, headers, rows):
        """Utility method that returns totals for database statistics.
        
        @param headers: List of columns in query result.
        @param rows:    List of rows in query result.
        @return:        Dictionary of totals for each statistics column. 
            
        """
        totals = [sum(col) for col in zip(*rows)[1:]]
        return dict(zip(headers[1:], totals))
    
    def _simpleQuery(self, query):
        """Executes simple query which returns a single column.
        
        @param query: Query string.
        @return:      Query result string.
        
        """
        cur = self._conn.cursor()
        cur.execute(query)
        row = cur.fetchone()
        return util.parse_value(row[0])
    
    def getVersion(self):
        """Returns PostgreSQL Server version string.
        
        @return: Version string.
        
        """
        return str(self._version)
    
    def checkVersion(self, verstr):
        """Checks if PostgreSQL Server version is higher than or equal to 
        version identified by verstr.
        
        @param version: Version string.
        
        """
        return self._version >= util.SoftwareVersion(verstr)
    
    def getStartTime(self):
        """Returns PostgreSQL Server start time.
        
        @return: Date/time the server started.
        
        """
        return self._simpleQuery("SELECT pg_postmaster_start_time();")
    
    def getParam(self, key):
        """Returns value of Run-time Database Parameter 'key'.
        
        @param key: Run-time parameter name.
        @return:    Run-time parameter value.
        
        """
        cur = self._conn.cursor()
        cur.execute("SHOW %s" % key)
        row = cur.fetchone()
        return util.parse_value(row[0])
    
    def getParams(self):
        """Returns dictionary of all run-time parameters.
        
        @return: Dictionary of all Run-time parameters.
        
        """
        cur = self._conn.cursor()
        cur.execute("SHOW ALL")
        rows = cur.fetchall()
        info_dict = {}
        for row in rows:
            key = row[0]
            val = util.parse_value(row[1])
            info_dict[key] = val
        return info_dict
    
    def getDatabases(self):
        """Returns list of databases.
        
        @return: List of databases.
        
        """
        cur = self._conn.cursor()
        cur.execute("""SELECT datname FROM pg_database;""")
        rows = cur.fetchall()
        if rows:
            return [row[0] for row in rows]
        else:
            return []
    
    def getConnectionStats(self):
        """Returns dictionary with number of connections for each database.
        
        @return: Dictionary of database connection statistics.
        
        """
        cur = self._conn.cursor()
        cur.execute("""SELECT datname,numbackends FROM pg_stat_database;""")
        rows = cur.fetchall()
        if rows:
            return dict(rows)
        else:
            return {}
        
    def getDatabaseStats(self):
        """Returns database block read, transaction and tuple stats for each 
        database.
        
        @return: Nested dictionary of stats.
        
        """
        headers = ('datname', 'numbackends', 'xact_commit', 'xact_rollback', 
                   'blks_read', 'blks_hit', 'tup_returned', 'tup_fetched', 
                   'tup_inserted', 'tup_updated', 'tup_deleted', 'disk_size')
        cur = self._conn.cursor()
        cur.execute("SELECT %s, pg_database_size(datname) FROM pg_stat_database;" 
                    % ",".join(headers[:-1]))
        rows = cur.fetchall()
        dbstats = self._createStatsDict(headers, rows)
        totals = self._createTotalsDict(headers, rows)
        return {'databases': dbstats, 'totals': totals}
    
    def getLockStatsMode(self):
        """Returns the number of active lock discriminated by lock mode.
        
        @return: : Dictionary of stats.
        
        """
        info_dict = {'all': dict(zip(self.lockModes, (0,) * len(self.lockModes))),
                     'wait': dict(zip(self.lockModes, (0,) * len(self.lockModes)))}
        cur = self._conn.cursor()
        cur.execute("SELECT TRIM(mode, 'Lock'), granted, COUNT(*) FROM pg_locks "
                    "GROUP BY TRIM(mode, 'Lock'), granted;")
        rows = cur.fetchall()
        for (mode, granted, cnt) in rows:
            info_dict['all'][mode] += cnt
            if not granted:
                info_dict['wait'][mode] += cnt
        return info_dict
    
    def getLockStatsDB(self):
        """Returns the number of active lock discriminated by database.
        
        @return: : Dictionary of stats.
        
        """
        info_dict = {'all': {},
                     'wait': {}}
        cur = self._conn.cursor()
        cur.execute("SELECT d.datname, l.granted, COUNT(*) FROM pg_database d "
                    "JOIN pg_locks l ON d.oid=l.database "
                    "GROUP BY d.datname, l.granted;")
        rows = cur.fetchall()
        for (db, granted, cnt) in rows:
            info_dict['all'][db] = info_dict['all'].get(db, 0) + cnt
            if not granted:
                info_dict['wait'][db] = info_dict['wait'].get(db, 0) + cnt
        return info_dict
    
    def getBgWriterStats(self):
        """Returns Global Background Writer and Checkpoint Activity stats.
        
        @return: Nested dictionary of stats.
        
        """
        info_dict = {}
        if self.checkVersion('8.3'):
            cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT * FROM pg_stat_bgwriter")
            info_dict = cur.fetchone()
        return info_dict
    
    def getXlogStatus(self):
        """Returns Transaction Logging or Recovery Status.
        
        @return: Dictionary of status items.
        
        """
        inRecovery = None
        if self.checkVersion('9.0'):
            inRecovery = self._simpleQuery("SELECT pg_is_in_recovery();")
        cur = self._conn.cursor()
        if inRecovery:
            cols = ['pg_last_xlog_receive_location()', 
                    'pg_last_xlog_replay_location()',]
            headers = ['xlog_receive_location',
                       'xlog_replay_location',]
            if self.checkVersion('9.1'):
                cols.extend(['pg_last_xact_replay_timestamp()',
                             'pg_is_xlog_replay_paused()',])
                headers.extend(['xact_replay_timestamp', 
                                'xlog_replay_paused',])
            cur.execute("""SELECT %s;""" % ','.join(cols))
            headers = ('xlog_receive_location', 'xlog_replay_location')
        else:
            cur.execute("""SELECT
                pg_current_xlog_location(), 
                pg_xlogfile_name(pg_current_xlog_location());""")
            headers = ('xlog_location', 'xlog_filename')
        row = cur.fetchone()
        info_dict = dict(zip(headers, row))
        if inRecovery is not None:
            info_dict['in_recovery'] = inRecovery
        return info_dict
               
    def getSlaveStatus(self):
        """Returns status of replication slaves.
        
        @return: Dictionary of status items.
        
        """
        info_dict = {}
        if self.checkVersion('9.1'):
            cols = ['procpid', 'usename', 'application_name', 
                    'client_addr', 'client_port', 'backend_start', 'state', 
                    'sent_location', 'write_location', 'flush_location', 
                    'replay_location', 'sync_priority', 'sync_state',]
            cur = self._conn.cursor()
            cur.execute("""SELECT %s FROM pg_stat_replication;""" 
                        % ','.join(cols))
            rows = cur.fetchall()
            for row in rows:
                info_dict[row[0]] = dict(zip(cols[1:], row[1:]))
        else:
            return None
        return info_dict
    
    def getSlaveConflictStats(self):
        if self.checkVersion('9.1'):
            headers = ('datname', 'confl_tablespace', 'confl_lock', 'confl_snapshot', 
                       'confl_bufferpin', 'confl_deadlock')
            cur = self._conn.cursor()
            cur.execute("SELECT %s FROM pg_stat_database_conflicts;" 
                    % ",".join(headers))
            rows = cur.fetchall()
            dbstats = self._createStatsDict(headers, rows)
            totals = self._createTotalsDict(headers, rows)
            return {'databases': dbstats, 'totals': totals}
        else:
            return None