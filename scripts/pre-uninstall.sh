#!/bin/sh
if [ "$1" = 0  ]; then
    rm -f /usr/share/munin/plugins/elfstats_*
    /sbin/service munin-node restart
fi
