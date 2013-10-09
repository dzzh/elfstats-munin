#!/usr/bin/env python

"""
Elfstats Response Codes - Munin Plugin to monitor response codes distribution from web servers' access logs.
Displays response codes grouped by 100 and important codes placed at separate charts.
"""

# Munin  - Magic Markers
#%# family=auto
#%# capabilities=autoconf suggest
import sys
from pymunin import MuninPlugin, MuninGraph, muninMain
from pysysinfo.elfstats_munin import ElfstatsInfo

NO_DATA_GRAPH = 'elfstats_response_codes_no_data'


class MuninElfstatsResponseCodesPlugin(MuninPlugin):
    """Multigraph Munin Plugin for monitoring web servers."""

    plugin_name = 'elfstats_response_codes'
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
        self._category = self.envGet('category', default='elfstats_resp_codes')
        self._show_dummy_graph = self.envGet('show_dummy_graph', default=1, conv=int)

        #
        # DRAWING
        #

        important_codes = self._elfstatsInfo.get_important_response_codes()
        all_codes = self._elfstatsInfo.get_response_codes()

        #Special case when no data is available. Output dummy graph not to confuse Munin.
        if not important_codes and not all_codes and self._show_dummy_graph:
            if self.graphEnabled(NO_DATA_GRAPH):
                graph = MuninGraph('Response codes - no data available', self._category, info='No data')
                self.appendGraph(NO_DATA_GRAPH, graph)

        #IMPORTANT RESPONSE CODES
        for code in important_codes:
            graph_name = 'elfstats_response_code_' + code
            if self.graphEnabled(graph_name):
                if self.hasGraph(graph_name):
                    graph = self._getGraph(graph_name)
                else:
                    graph = MuninGraph('elfstats - Calls per response code - %s' % code, self._category,
                                       info='Response %s code' % code,
                                       args='--base 1000  --logarithmic --units=si',
                                       vlabel='Number of calls per 5 min')
                    self.appendGraph(graph_name, graph)
                graph.addField(code, code, draw='LINE2', type='GAUGE', info=code)

        #OTHER RESPONSE CODES GROUPED BY 100
        for code in all_codes:
            if not code in self._elfstatsInfo.get_important_response_codes():
                graph_name = 'elfstats_response_codes_%sXX' % code[0]
                if self.graphEnabled(graph_name):
                    if self.hasGraph(graph_name):
                        graph = self._getGraph(graph_name)
                    else:
                        graph = MuninGraph('elfstats - Calls per response codes - %sXX' % code[0], self._category,
                                           info='Response %sXX code' % code[0],
                                           args='--base 1000',
                                           vlabel='Number of calls per 5 min')
                        self.appendGraph(graph_name, graph)
                    graph.addField(code, code, draw='LINE1', type='GAUGE', info=code)

    def retrieveVals(self):

        #
        #RETRIEVING VALUES
        #

        #IMPORTANT RESPONSE CODES
        for code in self._elfstatsInfo.get_important_response_codes():
            graph_name = 'elfstats_response_code_%s' % code
            if self.hasGraph(graph_name):
                self.setGraphVal(graph_name, code, self._elfstatsInfo.get_number_responses_by_code(code))

        #OTHER RESPONSE CODES
        for code in self._elfstatsInfo.get_response_codes():
            if not code in self._elfstatsInfo.get_important_response_codes():
                graph_name = 'elfstats_response_codes_%sXX' % code[0]
                if self.hasGraph(graph_name):
                    self.setGraphVal(graph_name, code, self._elfstatsInfo.get_number_responses_by_code(code))

    def autoconf(self):
        return True

    def parse_key(self, key):
        split = key.split('_')
        return split[0], split[1]


def main():
    sys.exit(muninMain(MuninElfstatsResponseCodesPlugin))


if __name__ == "__main__":
    main()


