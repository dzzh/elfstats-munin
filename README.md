# elfstats-munin

A set of Munin plugins for visualizing aggregated data from web servers' access logs. These plugins are a part of `elfstats` project. They are intended to work with aggregated data prepared by [elfstatsd](https://github.com/dzzh/elfstatsd) daemon. Using elfstatsd and these plugins it is possible to monitor such metrics as number of calls per request, aggregated latencies (min, max, avg, percentiles) per request and response codes distribution. Development plans include adding more metrics.

Elfstats-munin plugins are written in Python programming language and are based on [PyMunin](http://aouyar.github.io/PyMunin/) framework. Python 2.6.x/2.7.x is required.

## Build and install

Elfstats-munin plugins can be installed either from source codes or as an RPM package. For their correct operation, [elfstatsd](https://github.com/dzzh/elfstatsd) has to be installed in advance, otherwise the plugins will not have a source of aggregated data to send to Munin.

TO simplify elfstats-munin installation, it is planned to add it to PyPi in future. Pre-built RPM files for RHEL6_x64 distribution can be found in [Releases](https://github.com/dzzh/elfstats-munin/releases). Packaging scripts for other POSIX flavors are not yet implemented. Let me know if you are interested in having a package for your OS distribution. Also, if you need in a distribution in a different format, you can build elfstats-munin from the sources as explained below.

It is recommended, though not required, to setup [a virtual environment](http://www.virtualenv.org) for running these plugins. An RPM with such an environment set up and ready to go is maintained in [elfstats-env](https://github.com/dzzh/elfstats-env) repository. If the provided package does not suit you, you can use default Python installation or create a virtual environment yourself. Instructions to do so are provided below. 

If you find the installation instructions below somewhat unclear, you can also refer to [PyMunin installation guide](http://aouyar.github.io/PyMunin/#installation).

### Installating elfstats-munin from source codes

* Clone the repository: `git clone https://github.com/dzzh/elfstats-munin.git` and enter it with `cd elfstats-munin`.

* Switch to the virtual environment by issuing `source /path/to/virtualenv/bin/activate` if you want to use it. If you want to install the plugins using your default Python, you can skip this step. Just make sure that your Python version is either 2.6.x or 2.7.x by running `python --version`.

* Install plugins using the setup script: `python setup.py install`. 

* If you use virtual environment, executable launchers for the Munin plugins will be placed by default to `/path/to/virtualenv/share/munin/plugins`. If you work with default Python, they will be placed in `/usr/share/munin/plugins` by default. This default directory can be substituted with one specified in `MUNIN_PLUGIN_DIR` environmental variable if you need in such customization. 

Usually, `/usr/share` is owned by root and setup script will not be able to add plugin launchers there if default Python is used and installation script is not run by a privileged user. To overcome this issue, a post-installation script will be created and placed into `/usr/local/bin/elfstats-munin-install`. Run it as root to copy the launchers to where Munin will find them. 

## Configure

work in progress

## Run

work in progress

## License

Elfstats-munin is copyrighted free software made available under the terms of the GPL License Version 3. See the accompanying COPYING.txt file for full licensing information.

Elfstats-munin is based on [PyMunin](http://aouyar.github.io/PyMunin/) framework.

Copyright © 2013 [Źmicier Žaleźničenka][me] & Andriy Yakovlev.

Developed at [TomTom](http://tomtom.com). Inspired by [Oleg Sigida](http://linkedin.com/in/olegsigida/).

[me]: https://github.com/dzzh
