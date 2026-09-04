from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'signal_processing'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share',package_name, 'launch'),
        glob(os.path.join('launch','*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jose Eduardo Sanchez',
    maintainer_email='eduardo.mtz1403@gmail.com',
    description='Two ROS 2 nodes that generate a sinusoidal signal and process it '
                 '(phase shift, offset, and normalization) — Week 1 mini-challenge '
                 'of TE3001B.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'signal_gen = signal_processing.signal_gen:main',
            'signal_proc = signal_processing.signal_proc:main'
        ],
    },
)
