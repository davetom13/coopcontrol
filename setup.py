from distutils.core import setup

setup(
    name='coopcontrol',
    version='2.0.0',
    description='Chicken Coop Control Automation and API',
    url='http://github.com/isometimescode/coopcontrol',
    author='Toni Wells',
    author_email='isometimescode@users.noreply.github.com',
    license='GNU General Public License v3 or later (GPLv3+)',
    packages=['coopcontrol'],
    install_requires=['flask', 'pyyaml', 'python-dateutil', 'dataset']
)
