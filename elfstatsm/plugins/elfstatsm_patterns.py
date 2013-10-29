#!/usr/bin/env python

"""Elfstats Patterns - Munin Plugin to monitor total number of specific patterns' met in web servers' access logs."""

# Munin  - Magic Markers
#%# family=auto
#%# capabilities=autoconf suggest
import sys
from elfstatsm import MuninPlugin, MuninGraph, muninMain
from elfstatsm.elfstats_munin import ElfstatsInfo

METRICS = ['total', 'distinct']

GRAPH_NAME_PREFIX = 'elfstats_patterns_'
NO_DATA_GRAPH = 'elfstats_patterns_no_data'


class MuninElfstatsPatternsPlugin(MuninPlugin):
    """Multigraph Munin Plugin for monitoring web servers."""

    plugin_name = 'elfstatsm_patterns'
    isMultigraph = True
    isMultiInstance = True

    def __init__(self, argv=(), env=None, debug=False):
        """
        Populate Munin Plugin with MuninGraph instances.

        @param argv:  List of command line arguments.
        @param env:   Dictionary of environment variables.
        @param debug: Print debugging messages if True. (Default: False)
        """
        MuninPlugin.__init__(self, argv, env, debug)
        self._elfstatsInfo = ElfstatsInfo(self.envGet('dump_file'))
        self._category = self.envGet('category', default='elfstats_patterns')
        self._show_dummy_graph = self.envGet('show_dummy_graph', default=1, conv=int)

        #
        # DRAWING
        #
        ids = self._elfstatsInfo.get_pattern_ids()

        #Special case when no data is available. Output dummy graph not to confuse Munin.
        if not ids and self._show_dummy_graph:
            if self.graphEnabled(NO_DATA_GRAPH):
                graph = MuninGraph('Patterns - no data available', self._category, info='No data')
                self.appendGraph(NO_DATA_GRAPH, graph)

        for pattern_id in ids:
            graph_name = GRAPH_NAME_PREFIX + pattern_id
            if self.graphEnabled(graph_name):
                if self.hasGraph(graph_name):
                    graph = self._getGraph(graph_name)
                else:
                    graph = MuninGraph('elfstats - Number of %s pattern appearances ' % pattern_id.upper(),
                                       self._category,
                                       info='Number of pattern matches in access log',
                                       args='--base 1000  --logarithmic --units=si',
                                       vlabel='Number of matches per 5 min')
                    self.appendGraph(graph_name, graph)

                for metric in METRICS:
                    graph.addField(metric, metric, draw='LINE2', type='GAUGE', info=metric)

    def retrieveVals(self):

        #
        #RETRIEVING VALUES
        #
        ids = self._elfstatsInfo.get_pattern_ids()

        for pattern_id in ids:
            graph_name = GRAPH_NAME_PREFIX + pattern_id
            if self.hasGraph(graph_name):
                for metric in METRICS:
                    self.setGraphVal(graph_name, metric, self._elfstatsInfo.get_value_for_pattern(pattern_id, metric))

    def autoconf(self):
        return True

    def parse_key(self, key):
        split = key.split('_')
        return split[0], split[1]


def main():
    sys.exit(muninMain(MuninElfstatsPatternsPlugin))


if __name__ == "__main__":
    main()


