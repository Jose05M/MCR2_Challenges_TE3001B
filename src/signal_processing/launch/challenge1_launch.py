from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    signal_gen_node = Node(package='signal_processing',
                           executable='signal_gen',
                           output='screen'
                           )

    signal_proc_node = Node(package='signal_processing',
                            executable='signal_proc',
                            output='screen'
                            )
    rqt_node = Node(
        name='rqt_plot',
        package='rqt_plot',
        executable='rqt_plot',
        arguments=['/signal/data', '/proc_signal/data'],
        output='screen'
    )

    l_d = LaunchDescription([signal_gen_node, signal_proc_node, rqt_node])
    return l_d
