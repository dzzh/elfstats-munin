#!/usr/bin/env python

"""
Elfstats Percentiles - Munin Plugin to monitor percentiles of requests latencies from web servers' access logs.
Displays 50, 90 and 99 percentiles of response times for method calls as well as min, max and avg
"""

# Munin  - Magic Markers
#%# family=auto
#%# capabilities=autoconf suggest

import sys
from elfstatsm import MuninPlugin, MuninGraph, muninMain
from elfstatsm.elfstats_munin import ElfstatsInfo

NO_DATA_GRAPH = 'elfstats_percentile_no_data'

# List of percentiles to draw. Same percentiles have to be specified in settings.LATENCY_PERCENTILES in elfstatsd.
# Format: (percentile: int 0-100, munin draw format, color)
PERCENTILES = [(50, 'LINE1', '39E639'),
               (90, 'LINE1', 'FF9400'),
               (99, 'LINE2', 'FF0000')]


class MuninElfstatsPercentilesPlugin(MuninPlugin):
    """Multigraph Munin Plugin for monitoring web servers."""

    plugin_name = 'elfstatsm_percentiles'
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
        self._category = self.envGet('category', default='elfstats_percentiles')
        self._show_dummy_graph = self.envGet('show_dummy_graph', default=1, conv=int)

        #
        # DRAWING
        #

        keys = self._elfstatsInfo.get_method_keys()

        #Special case when no data is available. Output dummy graph not to confuse Munin.
        if not keys and self._show_dummy_graph:
            if self.graphEnabled(NO_DATA_GRAPH):
                graph = MuninGraph('Percentiles - no data available', self._category, info='No data')
                self.appendGraph(NO_DATA_GRAPH, graph)

        #METHOD percentiles
        for key in keys:
            method = self._elfstatsInfo.get_method_by_key(key)
            graph_name = method.get_graph_name()
            if self.graphEnabled(graph_name):
                graph = MuninGraph('elfstats - %s method calls percentiles' % method.get_full_name(), self._category,
                                   info='Method %s' % method.get_full_name(),
                                   args='--base 1000 --logarithmic --units=si',
                                   vlabel='Response time in ms')
                graph.addField('min', 'shortest', draw='LINE1', type='GAUGE', info='longest', colour='67E667')
                graph.addField('avg', 'average', draw='LINE2', type='GAUGE', info='average', colour='00CC00')
                graph.addField('max', 'longest', draw='LINE1', type='GAUGE', info='longest', colour='FF7373')
                for p, draw, colour in PERCENTILES:
                    graph.addField('p' + str(p), str(p) + '%', draw=draw, type='GAUGE', info=str(p)+'%', colour=colour)
                self.appendGraph(graph_name, graph)

    def retrieveVals(self):

        #
        #RETRIEVING VALUES
        #

        #METHOD percentiles (except of STATIC)
        for key in self._elfstatsInfo.get_method_keys():
            method = self._elfstatsInfo.get_method_by_key(key)
            graph_name = method.get_graph_name()
            if self.hasGraph(graph_name):
                self.setGraphVal(graph_name, 'min', method.min)
                self.setGraphVal(graph_name, 'avg', method.avg)
                self.setGraphVal(graph_name, 'max', method.max)
                for p, _, _ in PERCENTILES:
                    self.setGraphVal(graph_name, 'p' + str(p), method.get_percentile(p))

    def autoconf(self):
        return True

    def parse_key(self, key):
        split = key.split('_')
        return split[0], split[1]


def main():
    sys.exit(muninMain(MuninElfstatsPercentilesPlugin))


if __name__ == "__main__":
    main()


