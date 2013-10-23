#!/usr/bin/env python

"""
Elfstats Response Times - Munin Plugin to monitor requests latencies from web servers' access logs.
Displays total and average response times for method groups (except for small ones).
"""

# Munin  - Magic Markers
#%# family=auto
#%# capabilities=autoconf suggest
import sys
from elfstatsm import MuninPlugin, MuninGraph, muninMain
from elfstatsm.elfstats_munin import ElfstatsInfo, EMPTY_VALUE

NO_DATA_GRAPH = 'elfstats_response_times_no_data'


class MuninElfstatsResponseTimesPlugin(MuninPlugin):
    """Multigraph Munin Plugin for monitoring web servers."""

    plugin_name = 'elfstats_response_times'
    isMultigraph = True
    isMultiInstance = True

    def __init__(self, argv=(), env=None, debug=False):
        """Populate Munin Plugin with MuninGraph instances.

        @param argv:  List of command line arguments.
        @param env:   Dictionary of environment variables.
        @param debug: Print debugging messages if True. (Default: False)

        """
        MuninPlugin.__init__(self, argv, env, debug)
        self._elfstatsInfo = ElfstatsInfo(self.envGet('dump_file'))
        self._category = self.envGet('category', default='tt_resp_times')
        self._show_dummy_graph = self.envGet('show_dummy_graph', default=1, conv=int)

        #
        # DRAWING
        #

        keys = self._elfstatsInfo.get_method_keys()

        #Special case when no data is available. Output dummy graph not to confuse Munin.
        if not keys and self._show_dummy_graph:
            if self.graphEnabled(NO_DATA_GRAPH):
                graph = MuninGraph('Response times - no data available', self._category, info='No data')
                self.appendGraph(NO_DATA_GRAPH, graph)

        #TOTAL RESPONSE TIME for method groups (except small groups)
        for key in keys:
            method = self._elfstatsInfo.get_method_by_key(key)
            if not method.group in self._elfstatsInfo.get_small_groups():
                graph_name = method.get_graph_group_prefix() + 'response_total'
                if self.graphEnabled(graph_name):
                    if self.hasGraph(graph_name):
                        graph = self._getGraph(graph_name)
                    else:
                        graph = MuninGraph('elfstats - total response time for %s methods' % method.group.upper(),
                                           self._category,
                                           info='Method group %s' % method.group.upper(),
                                           args='--base 1000 --logarithmic --units=si',
                                           vlabel='Response time in ms')
                        self.appendGraph(graph_name, graph)
                    graph.addField(method.name, method.name, draw='LINE1', type='GAUGE', info=method.name)

        #AVERAGE RESPONSE TIME for method groups (except small groups)
        for key in keys:
            method = self._elfstatsInfo.get_method_by_key(key)
            if not method.group in self._elfstatsInfo.get_small_groups():
                graph_name = method.get_graph_group_prefix() + 'response_avg'
                if self.graphEnabled(graph_name):
                    if self.hasGraph(graph_name):
                        graph = self._getGraph(graph_name)
                    else:
                        graph = MuninGraph('elfstats - average response time for %s methods' % method.group.upper(),
                                           self._category,
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
        for key in self._elfstatsInfo.get_method_keys():
            method = self._elfstatsInfo.get_method_by_key(key)
            if not method.group in self._elfstatsInfo.get_small_groups():
                graph_name = method.get_graph_group_prefix() + 'response_total'
                if self.hasGraph(graph_name):
                    if method.calls != 'U' and method.avg != 'U':
                        self.setGraphVal(graph_name, method.name, int(method.calls) * int(method.avg))
                    else:
                        self.setGraphVal(graph_name, method.name, EMPTY_VALUE)

        #AVERAGE RESPONSE TIME for method groups (except of small groups)
        for key in self._elfstatsInfo.get_method_keys():
            method = self._elfstatsInfo.get_method_by_key(key)
            if not method.group in self._elfstatsInfo.get_small_groups():
                graph_name = method.get_graph_group_prefix() + 'response_avg'
                if self.hasGraph(graph_name):
                    self.setGraphVal(graph_name, method.name, method.avg)

    def autoconf(self):
        return True

    def parse_key(self, key):
        split = key.split('_')
        return split[0], split[1]


def main():
    sys.exit(muninMain(MuninElfstatsResponseTimesPlugin))


if __name__ == "__main__":
    main()


