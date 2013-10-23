#!/usr/bin/env python

"""
Elfstats Calls - Munin plugin to monitor number of calls from web servers' access logs.
Displays number of calls and stalled calls for method groups.
"""

# Munin  - Magic Markers
#%# family=auto
#%# capabilities=autoconf suggest

import sys
from elfstatsm import MuninPlugin, MuninGraph, muninMain
from elfstatsm.elfstats_munin import ElfstatsInfo

NO_DATA_GRAPH = 'elfstats_calls_no_data'


class MuninElfstatsCallsPlugin(MuninPlugin):
    """Multigraph Munin Plugin for monitoring web servers."""

    plugin_name = 'elfstats_calls'
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
        self._category = self.envGet('category', default='elfstats_calls')
        self._show_dummy_graph = self.envGet('show_dummy_graph', default=1, conv=int)

        #
        # DRAWING
        #

        keys = self._elfstatsInfo.get_method_keys()

        #Special case when no data is available. Output dummy graph not to confuse Munin.
        if not keys and self._show_dummy_graph:
            if self.graphEnabled(NO_DATA_GRAPH):
                graph = MuninGraph('Calls - no data available', self._category, info='No data')
                self.appendGraph(NO_DATA_GRAPH, graph)

        #NUMBER OF CALLS for method groups
        for key in keys:
            method = self._elfstatsInfo.get_method_by_key(key)
            graph_name = method.get_graph_group_prefix() + 'total_calls'
            if self.graphEnabled(graph_name):
                if self.hasGraph(graph_name):
                    graph = self._getGraph(graph_name)
                else:
                    graph = MuninGraph('elfstats - number of calls for %s methods' % method.group.upper(),
                                       self._category,
                                       info='Method group %s' % method.group.upper(),
                                       args='--base 1000',
                                       vlabel='Number of calls in 5 min')
                    self.appendGraph(graph_name, graph)
                graph.addField(method.name, method.name, draw='LINE1', type='GAUGE', info=method.name)

        #NUMBER OF STALLED CALLS for method groups
        for key in keys:
            method = self._elfstatsInfo.get_method_by_key(key)
            graph_name = method.get_graph_group_prefix() + 'stalled_calls'
            if self.graphEnabled(graph_name):
                if self.hasGraph(graph_name):
                    graph = self._getGraph(graph_name)
                else:
                    graph = MuninGraph('elfstats - number of stalled calls for %s methods' % method.group.upper(),
                                       self._category,
                                       info='Method group %s: number of calls exceeding the threshold'
                                            % method.group.upper(),
                                       args='--base 1000',
                                       vlabel='Number of stalled calls in 5 min')
                    self.appendGraph(graph_name, graph)
                graph.addField(method.name, method.name, draw='LINE1', type='GAUGE', info=method.name)

    def retrieveVals(self):

        #
        #RETRIEVING VALUES
        #

        keys = self._elfstatsInfo.get_method_keys()

        #NUMBER OF CALLS for method groups
        for key in keys:
            method = self._elfstatsInfo.get_method_by_key(key)
            graph_name = method.get_graph_group_prefix() + 'total_calls'
            if self.hasGraph(graph_name):
                self.setGraphVal(graph_name, method.name, method.calls)

        #NUMBER OF STALLED CALLS for method groups
        for key in keys:
            method = self._elfstatsInfo.get_method_by_key(key)
            graph_name = method.get_graph_group_prefix() + 'stalled_calls'
            if self.hasGraph(graph_name):
                self.setGraphVal(graph_name, method.name, method.stalled_calls)

    def autoconf(self):
        return True

    def parse_key(self, key):
        split = key.split('_')
        return split[0], split[1]


def main():
    sys.exit(muninMain(MuninElfstatsCallsPlugin))


if __name__ == "__main__":
    main()


