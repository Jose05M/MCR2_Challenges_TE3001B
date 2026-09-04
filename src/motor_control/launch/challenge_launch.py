import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    config = os.path.join(
        get_package_share_directory('motor_control'),
        'config',
        'params.yaml'
    )

    motor_node_1 = Node(name="motor_sys_1",
                        package='motor_control',
                        executable='dc_motor',
                        emulate_tty=True,
                        output='screen',
                        namespace="group1",
                        parameters=[config]
                        )

    sp_node_1 = Node(name="sp_gen_1",
                     package='motor_control',
                     executable='set_point',
                     emulate_tty=True,
                     output='screen',
                     namespace="group1",
                     parameters=[config]
                     )

    control_node_1 = Node(name="control_1",
                          package='motor_control',
                          executable='controller',
                          emulate_tty=True,
                          output='screen',
                          namespace="group1",
                          parameters=[config]
                          )

    motor_node_2 = Node(name="motor_sys_2",
                        package='motor_control',
                        executable='dc_motor',
                        emulate_tty=True,
                        output='screen',
                        namespace="group2",
                        parameters=[config]
                        )

    sp_node_2 = Node(name="sp_gen_2",
                     package='motor_control',
                     executable='set_point',
                     emulate_tty=True,
                     output='screen',
                     namespace="group2",
                     parameters=[config]
                     )
    control_node_2 = Node(name="control_2",
                          package='motor_control',
                          executable='controller',
                          emulate_tty=True,
                          output='screen',
                          namespace="group2",
                          parameters=[config]
                          )

    motor_node_3 = Node(name="motor_sys_3",
                        package='motor_control',
                        executable='dc_motor',
                        emulate_tty=True,
                        output='screen',
                        namespace="group3",
                        parameters=[config]
                        )

    sp_node_3 = Node(name="sp_gen_3",
                     package='motor_control',
                     executable='set_point',
                     emulate_tty=True,
                     output='screen',
                     namespace="group3",
                     parameters=[config]
                     )
    control_node_3 = Node(name="control_3",
                          package='motor_control',
                          executable='controller',
                          emulate_tty=True,
                          output='screen',
                          namespace="group3",
                          parameters=[config]
                          )

    l_d = LaunchDescription([motor_node_1,
                             sp_node_1,
                             control_node_1,
                             motor_node_2,
                             sp_node_2,
                             control_node_2,
                             motor_node_3,
                             sp_node_3,
                             control_node_3])

    return l_d
