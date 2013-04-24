#!/usr/bin/env python

""" TomTomStats Response Codes - Munin Plugin to monitor TomTom servers using Apache access logs.
    Displays response codes grouped by 100 and important codes placed at separate charts.
"""

# Munin  - Magic Markers
#%# family=auto
#%# capabilities=autoconf suggest
import sys
from pymunin import MuninPlugin, MuninGraph, muninMain
from pysysinfo.tomtom import TomTomInfo

class MuninTomTomResponseCodesPlugin(MuninPlugin):
    """Multigraph Munin Plugin for monitoring Community servers."""

    plugin_name = 'tomtomstats_response_codes'
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
        self._category = self.envGet('category',default='tt_resp_codes')

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

    def retrieveVals(self):

        #
        #RETRIEVING VALUES
        #

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
    sys.exit(muninMain(MuninTomTomResponseCodesPlugin))

if __name__ == "__main__":
    main()


