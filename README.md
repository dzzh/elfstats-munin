# Elfstats-munin

Elfstats-munin is a data visualization component of the [elfstats][] project.

It is a set of Munin plugins for visualizing aggregated data from web servers' access logs in Extended Log Format (ELF) that supports Apache, Tomcat, Nginx and some other HTTP servers. These plugins are supposed to work with the report files  prepared by the [elfstatsd][] daemon. Using elfstatsd and these plugins it is possible to monitor such metrics as the number of calls and slow calls, aggregated latencies (min, max, avg, percentiles), response codes distribution, the number of matches for the specific patterns and more. All these statistics are reported per different request groups specified by the user and can be as detailed as needed.  Development plans include adding more metrics.

Elfstats-munin plugins are written in Python programming language and are based on [PyMunin][] framework. Python 2.6.x/2.7.x and [elfstatsd][] are required for their correct operation. Migration to Python 3 is possible in future.

## Build and install

Elfstats-munin plugins can be installed either from the source codes or as an RPM package. To simplify elfstats-munin installation, it is planned to add it to PyPi in future. 

Pre-built RPM files for RHEL6_x64 distribution can be found in [Releases](https://github.com/dzzh/elfstats-munin/releases). The resulting RPMs may also work with the other RPM-based Linux distributions, but this has not been tested yet. 

Packaging scripts for non-RPM-based POSIX distributions are not yet implemented. Let me know if you are interested in having a package for your OS. Also, if you need in a distribution in a different format, you can build elfstats-munin from the sources as explained below.

It is recommended, though not required, to setup [a virtual environment](http://www.virtualenv.org) for running these plugins. An RPM with such environment is maintained in [elfstats-env][] repository. If the provided package does not suit you, you can use default Python installation or create a virtual environment yourself. 

If you find the installation instructions here somewhat unclear, you can also refer to [PyMunin installation guide](http://aouyar.github.io/PyMunin/#installation).

### Installing elfstats-munin from the source codes

* Clone the repository: `git clone https://github.com/dzzh/elfstats-munin.git` and enter it with `cd elfstats-munin`.

* Switch to the virtual environment by issuing `source /path/to/virtualenv/bin/activate` if you want to use it. If you want to install the plugins using your default Python, you can skip this step. Just make sure that your Python version is either 2.6.x or 2.7.x by running `python --version`.

* Install the plugins using the setup script: `python setup.py install`. 

After you install the plugins, their launchers will be placed in `/usr/share/munin/plugins` by default. This directory can be substituted with one specified in `MUNIN_PLUGIN_DIR` environmental variable, if you need in such customization. 

As `/usr/share/munin/plugins` is owned by root, setup script will not able to add plugin launchers there, if not run by a privileged user. To overcome this issue, a post-installation script will be created and placed into `/usr/bin/elfstats-munin-install`. Run it as root to copy the launchers to where Munin will find them. 

### Building and installing RPM for RHEL 6

* Clone the repository: `git clone https://github.com/dzzh/elfstats-munin.git` and enter it with `cd elfstats-munin`.

* Switch to the virtual environment by issuing `source /path/to/virtualenv/bin/activate` if you want to use it. If you want to install the plugins using your default Python, you can skip this step. Just make sure that your Python version is either 2.6.x or 2.7.x by running `python --version`.

* Build RPM: `python setup.py bdist_rpm`. After this step, the RPMs will be put in `dist/` directory.

* Install rpm: `sudo yum install dist/elfstats-munin-XX.XX.noarch.rpm`. This RPM can later be installed to the other machines without being re-built, but these machines should have virtual environment located at the same path as at the build machine or have to use default Python with installed dependencies. You can read about installing the dependencies in _Installing elfstats-munin from source codes_ section.

## Configure

When elfstats-munin is installed, all the plugins will be inactive. To activate them, you have to link the necessary plugins to `/etc/munin/plugins`. Thus, if you want to use all the plugins and you have installed elfstats-munin using default Python, you can activate them with the following command: `ln -s /usr/share/munin/plugins/elfstatsm_* /etc/munin/plugins/`.

After the plugins are activated, you have to configure them using `/etc/munin/plugin-conf.d/elfstats.conf` file. For each plugin you should add a section specifying the report file it should read and the other settings. The examples are provided in the configuration file. 

If you want to keep multiple plugin instances to work with several different access log files at once, link them to `/etc/munin/plugins` after different names and configure `elfstats.conf` accordingly.

`elfstats.conf` accepts the following settings. 

* `env.dump_file`: absolute path to the file with aggregated access log statistics prepared by [elfstatsd][].

* `env.category`: chart category. Use different categories to easier find the respective charts in Munin html reports.

* `env.instance_name`: should be different for multiple plugin instances.

* `env.show_dummy_graph`: if set to 1, an empty chart will be shown even if no data is available. If set to 0, empty charts won't be shown. However, it may confuse selinux if it is installed, thus it is set to 1 by default.

You can also refer to [PyMunin configuration guide](http://aouyar.github.io/PyMunin/#configuration) for additional information about configuring the plugins.

## License

Elfstats-munin is copyrighted free software made available under the terms of the GPL License Version 3. See the accompanying COPYING.txt file for full licensing information.

Elfstats-munin is based on [PyMunin][pymunin] framework.

Copyright © 2013 [Źmicier Žaleźničenka][me] & Andriy Yakovlev.

Developed at [TomTom](http://tomtom.com). Inspired by [Oleg Sigida](http://linkedin.com/in/olegsigida/).

[me]: https://github.com/dzzh
[elfstats]: https://github.com/dzzh/elfstats
[elfstatsd]: https://github.com/dzzh/elfstatsd
[elfstats-env]: https://github.com/dzzh/elfstats-env
[PyMunin]: http://aouyar.github.io/PyMunin/
