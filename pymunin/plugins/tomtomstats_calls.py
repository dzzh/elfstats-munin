#!/usr/bin/env python

""" TomTomStats Calls - Munin Plugin to monitor TomTom servers using Apache access logs.
    Displays number of calls and stalled calls for method groups.
"""

# Munin  - Magic Markers
#%# family=auto
#%# capabilities=autoconf suggest

import sys
from pymunin import MuninPlugin, MuninGraph, muninMain
from pysysinfo.tomtom import TomTomInfo

class MuninTomTomCallsPlugin(MuninPlugin):
    """Multigraph Munin Plugin for monitoring Community servers."""

    plugin_name = 'tomtomstats_calls'
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
        self._category = self.envGet('category',default='tt_calls')

        #
        # DRAWING
        #

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

    def retrieveVals(self):

        #
        #RETRIEVING VALUES
        #

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

    def autoconf(self):
        return True

    def parse_key(self,key):
        split = key.split('_')
        return split[0],split[1]

def main():
    sys.exit(muninMain(MuninTomTomCallsPlugin))

if __name__ == "__main__":
    main()


