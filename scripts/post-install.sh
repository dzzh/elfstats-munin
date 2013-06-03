VIRTUALENV_PATH='/srv/virtualenvs/munin'

cp -f $VIRTUALENV_PATH/bin/pymunin-tomtomstats_calls /usr/share/munin/plugins/tomtomstats_calls
cp -f $VIRTUALENV_PATH/bin/pymunin-tomtomstats_percentiles /usr/share/munin/plugins/tomtomstats_percentiles
cp -f $VIRTUALENV_PATH/bin/pymunin-tomtomstats_response_codes /usr/share/munin/plugins/tomtomstats_response_codes
cp -f $VIRTUALENV_PATH/bin/pymunin-tomtomstats_response_times /usr/share/munin/plugins/tomtomstats_response_times
