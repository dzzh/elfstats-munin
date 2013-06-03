#!/usr/bin/env python

""" TomTomStats Response Times - Munin Plugin to monitor TomTom servers using Apache access logs.
    Displays total and average response times for method groups (except for small ones)
"""

# Munin  - Magic Markers
#%# family=auto
#%# capabilities=autoconf suggest
import sys
from pymunin import MuninPlugin, MuninGraph, muninMain
from pysysinfo.tomtom import TomTomInfo

NO_DATA_GRAPH = 'tomtomstats_response_times_no_data'

class MuninTomTomResponseTimesPlugin(MuninPlugin):
    """Multigraph Munin Plugin for monitoring Community servers."""

    plugin_name = 'tomtomstats_response_times'
    isMultigraph = True
    isMultiInstance = False

    def __init__(self, argv=(), env=None, debug=False):
        """Populate Munin Plugin with MuninGraph instances.

        @param argv:  List of command line arguments.
        @param env:   Dictionary of environment variables.
        @param debug: Print debugging messages if True. (Default: False)

        """
        MuninPlugin.__init__(self, argv, env, debug)
        self._ttInfo = TomTomInfo(self.envGet('dump_file'))
        self._category = self.envGet('category',default='tt_resp_times')
        self._show_dummy_graph = self.envGet('show_dummy_graph',default=1,conv=int)

        #
        # DRAWING
        #

        keys = self._ttInfo.get_method_keys()

        #Special case when no data is available. Output dummy graph not to confuse selinux if it is enabled.
        if not keys and self._show_dummy_graph:
            if self.graphEnabled(NO_DATA_GRAPH):
                graph = MuninGraph('Response times - no data available', self._category, info='No data')
                self.appendGraph(NO_DATA_GRAPH,graph)

        #TOTAL RESPONSE TIME for method groups (except small groups)
        for key in keys:
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
        for key in keys:
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

    def retrieveVals(self):

        #
        #RETRIEVING VALUES
        #

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

    def autoconf(self):
        return True

    def parse_key(self,key):
        split = key.split('_')
        return split[0],split[1]

def main():
    sys.exit(muninMain(MuninTomTomResponseTimesPlugin))

if __name__ == "__main__":
    main()


