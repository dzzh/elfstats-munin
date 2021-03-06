from ez_setup import use_setuptools
use_setuptools()

import os
import pkgutil
import glob
import shutil
import errno
from setuptools import setup, find_packages
from setuptools.command.install import install as _install
import elfstatsm
import elfstatsm.plugins

ELFSTATSM_PLUGIN_DIR = u'/usr/share/munin/plugins'


if hasattr(pkgutil, "iter_modules"):  # Python > 2.5
    modules = [modname for importer, modname, ispkg in 
               pkgutil.iter_modules(elfstatsm.plugins.__path__)]
else:
    modules = []
    for path in glob.glob(os.path.join(elfstatsm.plugins.__path__[0],
                                       u'[A-Za-z]*.py')):
        file_path = os.path.basename(path)
        modules.append(file_path[:-3])

console_scripts = []
plugin_names = []
for modname in modules:
    params = {
        'script_name': modname,
        'script_path': u'%s.%s' % (elfstatsm.plugins.__name__,  modname),
        'entry': 'main',
    }
    plugin_names.append(modname)
    console_scripts.append(u'%(script_name)s = %(script_path)s:%(entry)s' % params)


class install(_install):
    """Extend base install class to provide a post-install step."""

    def run(self):
        if 'MUNIN_PLUGIN_DIR' in os.environ:
            munin_plugin_dir = os.environ.get('MUNIN_PLUGIN_DIR')
        elif self.root is None:
            munin_plugin_dir = ELFSTATSM_PLUGIN_DIR
        else:
            munin_plugin_dir = os.path.normpath(os.path.join(self.root, '.' + ELFSTATSM_PLUGIN_DIR))

        _install.run(self)

        # Installing the plugins requires write permission to plugins directory
        # (/usr/share/munin/plugins) which is by default owned by root.
        print "Munin Plugin Directory: %s" % munin_plugin_dir
        if self.root or os.path.exists(munin_plugin_dir):
            try:
                if not os.path.exists(munin_plugin_dir):
                    os.makedirs(munin_plugin_dir)
                lines = []
                for name in plugin_names:
                    source = os.path.join(self.install_scripts, name)
                    destination = os.path.join(munin_plugin_dir, name)
                    shutil.copy(source, destination)
                    if self.root:
                        lines.append(destination.split(self.root)[1])
                    else:
                        lines.append(destination)
                #If making an RPM with build_rpm, add new files to INSTALLED_FILES to properly install them later.
                if os.path.exists('INSTALLED_FILES'):
                    with open('INSTALLED_FILES', 'a') as f:
                        f.write('\n'.join(lines))
            except IOError, e:
                if e.errno in (errno.EACCES, errno.ENOENT):
                    # Access denied or file/directory not found.
                    print "*" * 78
                    if e.errno == errno.EACCES:
                        print ("You do not have permission to install the plugins to %s." % munin_plugin_dir)
                    if e.errno == errno.ENOENT:
                        print ("Failed installing the plugins to %s. File or directory not found." % munin_plugin_dir)
                    script = os.path.join(self.install_scripts, 'elfstats-munin-install')
                    f = open(script, 'w')
                    try:
                        f.write('#!/bin/sh\n')
                        for name in plugin_names:
                            source = os.path.join(self.install_scripts, name)
                            destination = os.path.join(munin_plugin_dir, name)
                            f.write('cp %s %s\n' % (source, destination))
                    finally:
                        f.close()
                    os.chmod(script, 0755)
                    print ("You will need to copy manually using the script: %s\n"
                           "Example: sudo %s"
                           % (script, script))
                    print "*" * 78
                else:
                    # Raise original exception
                    print e.message
                    raise

setup(
    name='elfstats-munin',
    version=elfstatsm.__version__,
    author=elfstatsm.__author__,
    author_email=elfstatsm.__author_email__,
    maintainer=elfstatsm.__maintainer__,
    maintainer_email=elfstatsm.__maintainer_email__,
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/dzzh/elfstats-munin',
    license=elfstatsm.__license__,
    description=u'A set of Munin monitoring plugins to display aggregated data from web servers access logs '
                u'that is gathered using elfstatsd. Based on PyMunin framework.',
    keywords="munin plugin monitoring apache tomcat nginx elf access log",
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
    install_requires=['elfstatsd>=1.17'],
    cmdclass={'install': install},
    entry_points={'console_scripts': console_scripts},
    data_files=[
        ('/etc/munin/plugin-conf.d', ['config/elfstats.conf']),
    ]
)
