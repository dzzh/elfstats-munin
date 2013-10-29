"""Implements ElfstatsInfo class to aggregate statistics from web servers' access logs."""

#Defaults
import ConfigParser
import logging

#Charts for these codes will be drawn separately, string values
IMPORTANT_RESPONSE_CODES = []

#No aggregate response time graphs for these graphs will be created
SMALL_GROUPS = ['small', 'smaller', 'smallest']

#Log file for plugins
LOG_FILE = "/tmp/elfstats-munin.log"

EMPTY_VALUE = 'U'

logger = logging.getLogger(__name__)


class ElfstatsInfo:
    """Class to retrieve stats for web servers"""

    def __init__(self, dump_file):
        self.dump_file = dump_file

        self.methods = {}
        self.response_codes = {}
        self.total_records = {}
        self.patterns = {}

        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler = logging.FileHandler(LOG_FILE)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.update_data()

    def update_data(self):
        self.methods.clear()
        self.response_codes.clear()
        self.total_records.clear()
        self.patterns.clear()

        parser = ConfigParser.RawConfigParser()
        if not self.dump_file:
            logger.error('Dump file not set. Check env.dump_file setting in plugin configuration')
        parser.read(self.dump_file)

        sections = parser.sections()

        for section in sections:
            if section.startswith('method'):
                group = section.split('_', 2)[1]
                name = section.split('_', 2)[2]
                method = MethodCallData(group, name)
                method.calls = parser.get(section, 'calls')
                method.stalled_calls = parser.get(section, 'stalled_calls')
                method.min = parser.get(section, 'shortest')
                method.max = parser.get(section, 'longest')
                method.avg = parser.get(section, 'average')
                for option in parser.options(section):
                    if option.startswith('p') and 2 <= len(option) <= 4:
                        method.percentiles[option[1:]] = parser.get(section, option)

                self.methods[method.get_key()] = method

            elif section == 'response_codes':
                for option in parser.options(section):
                    code = option[2:]
                    self.response_codes[code] = parser.get(section, option)

            elif section == 'records':
                for option in parser.options(section):
                    self.total_records[option] = parser.get(section, option)

            elif section == 'patterns':
                for option in parser.options(section):
                    self.patterns[option] = parser.get(section, option)

    def get_method_keys(self):
        return sorted(self.methods.keys())

    def get_response_codes(self):
        return sorted(self.response_codes.keys())

    def get_number_responses_by_code(self, code):
        if str(code) in self.response_codes:
            return self.response_codes[str(code)]
        else:
            return EMPTY_VALUE

    def get_records_statuses(self):
        return sorted(self.total_records.keys())

    def get_number_records_by_status(self, status):
        if str(status) in self.total_records:
            return self.total_records[str(status)]
        else:
            logger.error('Status %s not found in data' % status)
            return EMPTY_VALUE

    def get_pattern_ids(self):
        ids = set([p.rsplit('.', 1)[0] for p in self.patterns])
        return sorted(list(ids))

    def get_value_for_pattern(self, pattern_id, suffix):
        for match, value in self.patterns.iteritems():
            if match.startswith(pattern_id) and match.endswith('.' + suffix):
                return value
        return EMPTY_VALUE

    def get_method_by_key(self, key):
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

    def __init__(self, group, name):
        self.group = group
        self.name = name
        self.min = EMPTY_VALUE
        self.max = EMPTY_VALUE
        self.avg = EMPTY_VALUE
        self.calls = EMPTY_VALUE
        self.stalled_calls = EMPTY_VALUE
        self.percentiles = {}

    def get_key(self):
        return self.group + '_' + self.name

    def get_full_name(self):
        return '%s:%s' % (self.group.upper(), self.name)

    def get_graph_name(self):
        return 'elfstats_%s_%s' % (self.group.lower(), self.name)

    def get_graph_group_prefix(self):
        return 'elfstats_%s_' % self.group.lower()

    def get_percentile(self, percent):
        if str(percent) in self.percentiles:
            return self.percentiles[str(percent)]
        else:
            logger.error('Percentile %s not found in data for method %s' % (percent, self.name))
            return EMPTY_VALUE