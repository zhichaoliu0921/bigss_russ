from setuptools import setup

package_name = 'bigss_russ_gazebo'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/ament_package', ['package.xml']),
        ('lib/python3.8/site-packages', ['src/test_trajectory.py']),  # Adjust the path based on your setup
    ],
    install_requires=['setuptools', 'rclpy'],
    zip_safe=True,
)
