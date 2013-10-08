#!/bin/sh
VIRTUALENV_PATH='/srv/virtualenvs/elfstats'

cp -f ${VIRTUALENV_PATH}/bin/pymunin-elfstats_calls /usr/share/munin/plugins/elfstats_calls
cp -f ${VIRTUALENV_PATH}/bin/pymunin-elfstats_percentiles /usr/share/munin/plugins/elfstats_percentiles
cp -f ${VIRTUALENV_PATH}/bin/pymunin-elfstats_response_codes /usr/share/munin/plugins/elfstats_response_codes
cp -f ${VIRTUALENV_PATH}/bin/pymunin-elfstats_response_times /usr/share/munin/plugins/elfstats_response_times