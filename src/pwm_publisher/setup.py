from setuptools import find_packages, setup

package_name = 'pwm_publisher'

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
    description='ROS 2 publisher that sends random PWM commands to control a real '
    'DC motor driven by an ESP32 running micro-ROS — Week 3 '
    'mini-challenge of TE3001B.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'pwm_pub = pwm_publisher.pwm_pub:main'
        ],
    },
)
