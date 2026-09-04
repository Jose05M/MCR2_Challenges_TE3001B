from setuptools import find_packages, setup

package_name = 'control_motor_challenge'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Jose Eduardo Sanchez',
    maintainer_email='eduardo.mtz1403@gmail.com',
    description='Closed-loop speed controller for a real DC motor with encoder '
                 'feedback via micro-ROS: reference signal generator and data '
                 'logger nodes for the TE3001B Final Challenge.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'save_data = control_motor_challenge.save_data:main',
            'set_point = control_motor_challenge.set_point:main'
        ],
    },
)
