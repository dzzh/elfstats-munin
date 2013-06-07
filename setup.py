import os
import pkgutil
import glob
from setuptools import setup, find_packages
import pymunin #@UnusedImport
import pymunin.plugins

PYMUNIN_SCRIPT_FILENAME_PREFIX = u'pymunin'

if hasattr(pkgutil, "iter_modules"): # Python > 2.5
    modules = [modname for importer, modname, ispkg in 
               pkgutil.iter_modules(pymunin.plugins.__path__)]
else:
    modules = []
    for path in glob.glob(os.path.join(pymunin.plugins.__path__[0], 
                                       u'[A-Za-z]*.py')):
        file = os.path.basename(path)
        modules.append(file[:-3])

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
    name='pymunin-tomtom',
    version=pymunin.__version__,
    author=pymunin.__author__,
    author_email=pymunin.__email__,
    maintainer=pymunin.__author__,
    maintainer_email=pymunin.__email__,
    packages=find_packages(),
    include_package_data=True,
    url='http://vos.intra.local/display/SS3/Monitoring+Apache+performance+at+Community+servers+with+Munin',
    license=pymunin.__license__,
    description=u'Python Module for developing Munin Multigraph Monitoring Plugins.',
    classifiers=[
        'Topic :: System :: Monitoring',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Development Status :: 4 - Beta',
        'Operating System :: RHEL 5/6',
    ],
    entry_points={'console_scripts': console_scripts},
    data_files = [
        ('/etc/munin/plugin-conf.d',['config/tomtomstats.conf']),
    ]
)
