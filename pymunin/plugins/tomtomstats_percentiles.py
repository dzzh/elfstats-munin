#!/usr/bin/env python

""" TomTomStats Percentiles - Munin Plugin to monitor TomTom servers using Apache access logs.
    Displays 50,90 and 99 percentiles of response times for method calls as well as min, max and avg
    STATIC methods are omitted
"""

# Munin  - Magic Markers
#%# family=auto
#%# capabilities=autoconf suggest

import sys
from pymunin import MuninPlugin, MuninGraph, muninMain
from pysysinfo.tomtom import TomTomInfo

NO_DATA_GRAPH = 'tomtomstats_percentile_no_data'

class MuninTomTomPercentilesPlugin(MuninPlugin):
    """Multigraph Munin Plugin for monitoring Community servers."""

    plugin_name = 'tomtomstats_percentiles'
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
        self._category = self.envGet('category',default='tt_percentiles')
        self._show_dummy_graph = self.envGet('show_dummy_graph',default=1,conv=int)

        #
        # DRAWING
        #

        keys = self._ttInfo.get_method_keys()

        #Special case when no data is available. Output dummy graph not to confuse selinux if it is enabled.
        if not keys and self._show_dummy_graph:
            if self.graphEnabled(NO_DATA_GRAPH):
                graph = MuninGraph('Percentiles - no data available', self._category,info='No data')
                self.appendGraph(NO_DATA_GRAPH,graph)

        #METHOD percentiles (except of STATIC)
        for key in keys:
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

        #No data case
        if self.hasGraph(NO_DATA_GRAPH) and self._show_dummy_graph:
            self.setGraphVal(NO_DATA_GRAPH,'x',1)

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

    def autoconf(self):
        return True

    def parse_key(self,key):
        split = key.split('_')
        return split[0],split[1]

def main():
    sys.exit(muninMain(MuninTomTomPercentilesPlugin))

if __name__ == "__main__":
    main()


