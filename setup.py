from setuptools import setup
import os
from glob import glob

package_name = 'roboclaw_motor'
submodules = 'roboclaw_motor'

setup(
    name = package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        # install launch file
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'config'), glob(os.path.join('config', '*.yaml')))
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer='Lin Zhao',
    maintainer_email='linzhao@uri.edu',
    description='The roboclaw motor driver package',
    license='GPLv3',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'roboclaw_motor_driver_node = roboclaw_motor.driver_node:main',
        ],
    },
)