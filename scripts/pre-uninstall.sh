if [ "$1" = 0  ]; then
    rm -f /usr/share/munin/plugins/elfstatsm_*
    rm -f /etc/munin/plugin-conf.d/elfstats.conf
    /sbin/service munin-node restart
fi
