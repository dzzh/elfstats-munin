if [ "$1" = 0  ]; then
rm -f /usr/share/munin/plugins/tomtomstats_*
/sbin/service munin-node restart
fi
