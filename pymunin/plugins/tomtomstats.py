#!/usr/bin/env python

""" TomTomStats - Munin Plugin to monitor TomTom servers using Apache access logs."""

# Munin  - Magic Markers
#%# family=auto
#%# capabilities=autoconf suggest
import logging

import sys
from pymunin import MuninPlugin, MuninGraph, muninMain
from pysysinfo.tomtom import TomTomInfo

class MuninTomTomPlugin(MuninPlugin):
    """Multigraph Munin Plugin for monitoring Community servers."""

    plugin_name = 'tomtomstats'
    isMultigraph = True
    isMultiInstance = False

    def __init__(self, argv=(), env=None, debug=False):
        """Populate Munin Plugin with MuninGraph instances.

        @param argv:  List of command line arguments.
        @param env:   Dictionary of environment variables.
        @param debug: Print debugging messages if True. (Default: False)

        """
        MuninPlugin.__init__(self, argv, env, debug)
        self._data = self.envGet('data')

        self._ttInfo = TomTomInfo()
        self._category = 'TomTom'

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler = logging.FileHandler("/tmp/tomtomstats.log")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        #
        # DRAWING
        #

        #IMPORTANT RESPONSE CODES
        for code in self._ttInfo.get_important_response_codes():
            graph_name = 'tomtom_response_code_' + code
            if self.graphEnabled(graph_name):
                if self.hasGraph(graph_name):
                    graph = self._getGraph(graph_name)
                else:
                    graph = MuninGraph('Apache - Calls per response code - %s' % code, self._category,
                        info='Response %s code' % code,
                        args='--base 1000  --logarithmic --units=si',
                        vlabel='Number of calls per 5 min')
                    self.appendGraph(graph_name, graph)
                graph.addField(code, code, draw='LINE2', type='GAUGE', info=code)

        #OTHER RESPONSE CODES GROUPED BY 100
        for code in self._ttInfo.get_response_codes():
            if not code in self._ttInfo.get_important_response_codes():
                graph_name = 'tomtom_response_codes_%sXX' % code[0]
                if self.graphEnabled(graph_name):
                    if self.hasGraph(graph_name):
                        graph = self._getGraph(graph_name)
                    else:
                        graph = MuninGraph('Apache - Calls per response codes - %sXX' % code[0], self._category,
                            info='Response %sXX code' % code[0],
                            args='--base 1000',
                            vlabel='Number of calls per 5 min')
                        self.appendGraph(graph_name, graph)
                    graph.addField(code, code, draw='LINE1', type='GAUGE', info=code)

        #TOTAL RESPONSE TIME for method groups (except small groups)
        for key in self._ttInfo.get_method_keys():
            method = self._ttInfo.get_method_by_key(key)
            if not method.group in self._ttInfo.get_small_groups():
                graph_name = method.get_graph_group_prefix()+'response_total'
                if self.graphEnabled(graph_name):
                    if self.hasGraph(graph_name):
                        graph = self._getGraph(graph_name)
                    else:
                        graph = MuninGraph('Apache - total response time for %s methods' % method.group.upper(), self._category,
                            info='Method group %s' % method.group.upper(),
                            args='--base 1000 --logarithmic --units=si',
                            vlabel='Response time in ms')
                        self.appendGraph(graph_name, graph)
                    graph.addField(method.name, method.name, draw='LINE1', type='GAUGE', info=method.name)

        #AVERAGE RESPONSE TIME for method groups (except small groups)
        for key in self._ttInfo.get_method_keys():
            method = self._ttInfo.get_method_by_key(key)
            if not method.group in self._ttInfo.get_small_groups():
                graph_name = method.get_graph_group_prefix()+'response_avg'
                if self.graphEnabled(graph_name):
                    if self.hasGraph(graph_name):
                        graph = self._getGraph(graph_name)
                    else:
                        graph = MuninGraph('Apache - average response time for %s methods' % method.group.upper(), self._category,
                            info='Method group %s' % method.group.upper(),
                            args='--base 1000 --logarithmic --units=si',
                            vlabel='Response time in ms')
                        self.appendGraph(graph_name, graph)
                    graph.addField(method.name, method.name, draw='LINE1', type='GAUGE', info=method.name)

        #NUMBER OF CALLS for method groups
        for key in self._ttInfo.get_method_keys():
            method = self._ttInfo.get_method_by_key(key)
            graph_name = method.get_graph_group_prefix()+'total_calls'
            if self.graphEnabled(graph_name):
                if self.hasGraph(graph_name):
                    graph = self._getGraph(graph_name)
                else:
                    graph = MuninGraph('Apache - number of calls for %s methods' % method.group.upper(), self._category,
                        info='Method group %s' % method.group.upper(),
                        args='--base 1000',
                        vlabel='Number of calls in 5 min')
                    self.appendGraph(graph_name, graph)
                graph.addField(method.name, method.name, draw='LINE1', type='GAUGE', info=method.name)

        #NUMBER OF STALLED CALLS for method groups
        for key in self._ttInfo.get_method_keys():
            method = self._ttInfo.get_method_by_key(key)
            graph_name = method.get_graph_group_prefix()+'stalled_calls'
            if self.graphEnabled(graph_name):
                if self.hasGraph(graph_name):
                    graph = self._getGraph(graph_name)
                else:
                    graph = MuninGraph('Apache - number of stalled calls for %s methods' % method.group.upper(), self._category,
                        info='Method group %s' % method.group.upper(),
                        args='--base 1000',
                        vlabel='Number of stalled calls in 5 min')
                    self.appendGraph(graph_name, graph)
                graph.addField(method.name, method.name, draw='LINE1', type='GAUGE', info=method.name)

        #METHOD percentiles (except of STATIC)
        for key in self._ttInfo.get_method_keys():
            method = self._ttInfo.get_method_by_key(key)
            graph_name = method.get_graph_name()
            if not method.group == 'static':
                if self.graphEnabled(graph_name):
                    graph = MuninGraph('Apache - %s method calls percentiles' % method.get_full_name(), self._category,
                        info='Method %s' % method.get_full_name(),
                        args='--base 1000 --logarithmic --units=si',
                        vlabel='Response time in ms')
                    graph.addField('min', 'shortest', draw='LINE1', type='GAUGE', info='longest', colour='696969')
                    graph.addField('p50', 'median', draw='LINE1', type='GAUGE', info='median',colour='006400')
                    graph.addField('avg', 'average', draw='LINE2', type='GAUGE', info='average',colour='000080')
                    graph.addField('p90', '90%', draw='LINE1', type='GAUGE', info='90%',colour='FF1493')
                    graph.addField('p99', '99%', draw='LINE2', type='GAUGE', info='99%',colour='800000')
                    graph.addField('max', 'longest', draw='LINE1', type='GAUGE', info='longest',colour='FF0000')
                    self.appendGraph(graph_name, graph)

    def retrieveVals(self):

        #
        #RETRIEVING VALUES
        #

        #METHOD percentiles (except of STATIC)
        for key in self._ttInfo.get_method_keys():
            method = self._ttInfo.get_method_by_key(key)
            graph_name = method.get_graph_name()
            if not method.group == 'static':
                if self.hasGraph(graph_name):
                    self.setGraphVal(graph_name,'min',method.min)
                    self.setGraphVal(graph_name,'p50',method.p50)
                    self.setGraphVal(graph_name,'avg',method.avg)
                    self.setGraphVal(graph_name,'p90',method.p90)
                    self.setGraphVal(graph_name,'p99',method.p99)
                    self.setGraphVal(graph_name,'max',method.max)

        #TOTAL RESPONSE TIME for method groups (except of small groups)
        for key in self._ttInfo.get_method_keys():
            method = self._ttInfo.get_method_by_key(key)
            if not method.group in self._ttInfo.get_small_groups():
                graph_name = method.get_graph_group_prefix()+'response_total'
                if self.hasGraph(graph_name):
                    self.setGraphVal(graph_name,method.name,int(method.calls) * int(method.avg))

        #AVERAGE RESPONSE TIME for method groups (except of small groups)
        for key in self._ttInfo.get_method_keys():
            method = self._ttInfo.get_method_by_key(key)
            if not method.group in self._ttInfo.get_small_groups():
                graph_name = method.get_graph_group_prefix()+'response_avg'
                if self.hasGraph(graph_name):
                    self.setGraphVal(graph_name,method.name,method.avg)

        #NUMBER OF CALLS for method groups
        for key in self._ttInfo.get_method_keys():
            method = self._ttInfo.get_method_by_key(key)
            graph_name = method.get_graph_group_prefix()+'total_calls'
            if self.hasGraph(graph_name):
                self.setGraphVal(graph_name,method.name,method.calls)

        #NUMBER OF STALLED CALLS for method groups
        for key in self._ttInfo.get_method_keys():
            method = self._ttInfo.get_method_by_key(key)
            graph_name = method.get_graph_group_prefix()+'stalled_calls'
            if self.hasGraph(graph_name):
                self.setGraphVal(graph_name,method.name,method.stalled_calls)

        #IMPORTANT RESPONSE CODES
        for code in self._ttInfo.get_important_response_codes():
            graph_name = 'tomtom_response_code_%s' % code
            if self.hasGraph(graph_name):
                self.setGraphVal(graph_name, code, self._ttInfo.get_number_responses_by_code(code))

        #OTHER RESPONSE CODES
        for code in self._ttInfo.get_response_codes():
            if not code in self._ttInfo.get_important_response_codes():
                graph_name = 'tomtom_response_codes_%sXX' % code[0]
                if self.hasGraph(graph_name):
                    self.setGraphVal(graph_name, code, self._ttInfo.get_number_responses_by_code(code))

    def autoconf(self):
        return True

    def parse_key(self,key):
        split = key.split('_')
        return split[0],split[1]

def main():
    sys.exit(muninMain(MuninTomTomPlugin))

if __name__ == "__main__":
    main()


