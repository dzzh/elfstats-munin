""" Implements TomTomInfo class to gather statistics for TomTom servers"""

#Defaults
import ConfigParser
import logging

#Charts for these codes will be drawn separately, string values
IMPORTANT_RESPONSE_CODES = []

#No aggregate response time graphs for these graphs will be created
SMALL_GROUPS = ['server','main','activation']

#Log file for plugins
LOG_FILE = "/tmp/tomtom.log"

class TomTomInfo:
    """Class to retrieve stats for TomTom servers"""

    def __init__(self, dump_file):
        self.dump_file = dump_file

        self.methods = dict()
        self.response_codes = dict()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler = logging.FileHandler(LOG_FILE)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.update_data()

    def update_data(self):
        self.methods.clear()
        self.response_codes.clear()

        parser = ConfigParser.RawConfigParser()
        if not self.dump_file:
            self.logger.error('Dump file not set. Check env.dump_file setting in plugin configuration')
        parser.read(self.dump_file)

        sections = parser.sections()

        for section in sections:
            if section.startswith('method'):
                group = section.split('_',2)[1]
                name = section.split('_',2)[2]
                method = MethodCallData(group, name)
                method.calls = parser.get(section,'calls')
                method.stalled_calls = parser.get(section,'stalled_calls')
                method.min = parser.get(section,'shortest')
                method.max = parser.get(section,'longest')
                method.avg = parser.get(section,'average')
                method.p50 = parser.get(section,'p50')
                method.p90 = parser.get(section,'p90')
                method.p99 = parser.get(section,'p99')
                self.methods[method.get_key()] = method
            if section == 'response_codes':
                for option in parser.options(section):
                    self.response_codes[option] = parser.get(section,option)

    def get_method_keys(self):
            return sorted(self.methods.keys())

    def get_response_codes(self):
            return sorted(self.response_codes.keys())

    def get_number_responses_by_code(self,code):
        if str(code) in self.response_codes:
            return self.response_codes[str(code)]
        else:
            return '0'

    def get_method_by_key(self,key):
        """
        @param string key: key
        @return MethodCallData: method
        """
        return self.methods[key]

    def get_important_response_codes(self):
        return IMPORTANT_RESPONSE_CODES

    def get_small_groups(self):
        return SMALL_GROUPS

class MethodCallData():

    def __init__(self,group,name):
        self.group = group
        self.name = name
        self.min = 0
        self.max = 0
        self.avg = 0
        self.calls = 0
        self.stalled_calls = 0
        self.p50 = 0
        self.p90 = 0
        self.p99 = 0

    def get_key(self):
        return self.group + '_' + self.name

    def get_full_name(self):
        return '%s:%s' %(self.group.upper(),self.name)

    def get_graph_name(self):
        return 'tomtom_%s_%s' %(self.group.lower(),self.name)

    def get_graph_group_prefix(self):
        return 'tomtom_%s_' % self.group.lower()
