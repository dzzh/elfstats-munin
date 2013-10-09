from ez_setup import use_setuptools
use_setuptools()

import os
import pkgutil
import glob
from setuptools import setup, find_packages
import pymunin
import pymunin.plugins

PYMUNIN_SCRIPT_FILENAME_PREFIX = u'pymunin'


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()

if hasattr(pkgutil, "iter_modules"):  # Python > 2.5
    modules = [modname for importer, modname, ispkg in 
               pkgutil.iter_modules(pymunin.plugins.__path__)]
else:
    modules = []
    for path in glob.glob(os.path.join(pymunin.plugins.__path__[0], 
                                       u'[A-Za-z]*.py')):
        file_path = os.path.basename(path)
        modules.append(file_path[:-3])

console_scripts = []
plugin_names = []
for modname in modules:
    params = {
        'script_name': u'%s-%s' % (PYMUNIN_SCRIPT_FILENAME_PREFIX, modname),
        'script_path': u'%s.%s' % (pymunin.plugins.__name__,  modname),
        'entry': 'main',
    }
    plugin_names.append(modname)
    console_scripts.append(u'%(script_name)s = %(script_path)s:%(entry)s' % params)

setup(
    name='elfstats-munin',
    version=pymunin.__version__,
    author=pymunin.__author__,
    author_email=pymunin.__author_email__,
    maintainer=pymunin.__maintainer__,
    maintainer_email=pymunin.__maintainer_email__,
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/dzzh/elfstats-munin',
    license=pymunin.__license__,
    description=u'A set of Munin monitoring plugins to display aggregated data from web servers access logs '
                u'that is gathered using elfstatsd. Based on PyMunin framework.',
    long_description=read('README.md'),
    keywords="munin plugin monitoring apache tomcat nginx elf access log",
    install_requires=['elfstatsd>=1.17'],
    platforms=['POSIX'],
    classifiers=[
        'Topic :: System :: Monitoring',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2 :: Only',
        "Topic :: Internet :: Log Analysis",
        "Topic :: System :: Monitoring",
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX',
    ],
    entry_points={'console_scripts': console_scripts},
    data_files=[
        ('/etc/munin/plugin-conf.d', ['config/elfstats.conf']),
    ]
)
