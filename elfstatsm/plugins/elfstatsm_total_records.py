#!/usr/bin/env python

"""
Elfstats Total Records - Munin Plugin to monitor total number of records per each status from web servers' access logs.
Displays the numbers of parsed, skipped and erroneous records found in the log, as well as total number of records.
"""

# Munin  - Magic Markers
#%# family=auto
#%# capabilities=autoconf suggest
import sys
from elfstatsm import MuninPlugin, MuninGraph, muninMain
from elfstatsm.elfstats_munin import ElfstatsInfo

NO_DATA_GRAPH = 'elfstats_total_records_no_data'

#Values for these statuses will not be shown on the graph
STATUSES_TO_SKIP = {'total', 'parsed'}


class MuninElfstatsTotalRecordsPlugin(MuninPlugin):
    """Multigraph Munin Plugin for monitoring web servers."""

    plugin_name = 'elfstats_total_records'
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
        self._category = self.envGet('category', default='elfstats_total_records')
        self._show_dummy_graph = self.envGet('show_dummy_graph', default=1, conv=int)

        #
        # DRAWING
        #

        all_statuses = set(self._elfstatsInfo.get_records_statuses())
        statuses_to_draw = all_statuses.difference(STATUSES_TO_SKIP)

        #Special case when no data is available. Output dummy graph not to confuse Munin.
        if not statuses_to_draw and self._show_dummy_graph:
            if self.graphEnabled(NO_DATA_GRAPH):
                graph = MuninGraph('Total records - no data available', self._category, info='No data')
                self.appendGraph(NO_DATA_GRAPH, graph)

        graph_name = 'elfstats_total_records'
        if self.graphEnabled(graph_name):
            if self.hasGraph(graph_name):
                graph = self._getGraph(graph_name)
            else:
                graph = MuninGraph('elfstats - Total records per status', self._category,
                                   info='Total number of records ',
                                   args='--base 1000  --logarithmic --units=si',
                                   vlabel='Number of records per 5 min')
                self.appendGraph(graph_name, graph)

            for status in statuses_to_draw:
                graph.addField(status, status, draw='LINE2', type='GAUGE', info=status)

    def retrieveVals(self):

        #
        #RETRIEVING VALUES
        #

        all_statuses = set(self._elfstatsInfo.get_records_statuses())
        statuses_to_draw = all_statuses.difference(STATUSES_TO_SKIP)

        for status in statuses_to_draw:
            graph_name = 'elfstats_total_records'
            if self.hasGraph(graph_name):
                self.setGraphVal(graph_name, status, self._elfstatsInfo.get_number_records_by_status(status))

    def autoconf(self):
        return True

    def parse_key(self, key):
        split = key.split('_')
        return split[0], split[1]


def main():
    sys.exit(muninMain(MuninElfstatsTotalRecordsPlugin))


if __name__ == "__main__":
    main()


