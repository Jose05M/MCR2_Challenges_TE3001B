#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from rcl_interfaces.msg import SetParametersResult
import numpy as np


class PIDController(Node):

    def __init__(self):
        super().__init__("controller")

        # Parameters
        self.declare_parameter("kp", 1.0)
        self.declare_parameter("ki", 0.0)
        self.declare_parameter("kd", 0.0)
        self.declare_parameter("Ts", 0.01)

        self.kp = self.get_parameter("kp").value
        self.ki = self.get_parameter("ki").value
        self.kd = self.get_parameter("kd").value
        self.Ts = self.get_parameter("Ts").value

        # States
        self.e_prev = 0.0
        self.integral = 0.0
        self.y = 0.0
        self.sp = 0.0

        # Subscribers
        self.create_subscription(Float32, "set_point", self.sp_callback, 10)
        self.create_subscription(Float32, "motor_speed_y", self.y_callback, 10)

        # Publisher
        self.pub = self.create_publisher(Float32, "motor_input_u", 10)

        # Timer
        self.timer = self.create_timer(self.Ts, self.control_loop)
        
        #Parameter Callback
        self.add_on_set_parameters_callback(self.parameters_callback)

    def sp_callback(self, msg):
        self.sp = msg.data

    def y_callback(self, msg):
        self.y = msg.data

    def control_loop(self):
        e = self.sp - self.y

        self.integral += e * self.Ts
        derivative = (e - self.e_prev) / self.Ts

        u = (
            self.kp * e
            + self.ki * self.integral
            + self.kd * derivative
        )

        msg = Float32()
        msg.data = float(u)
        self.pub.publish(msg)

        self.e_prev = e

    def parameters_callback(self, params):
        for param in params:
            if param.name == "kp":
                if param.value < 0.0:
                    self.get_logger().warn("Kp cannot be negative.")
                    return SetParametersResult(successful=False, reason="Kp must be >= 0")
                else:
                    self.kp = param.value # Update internal variable
                    self.get_logger().info(f"Kp updated to {self.kp}")

            if param.name == "ki":
                if param.value < 0.0:
                    self.get_logger().warn("Ki cannot be negative.")
                    return SetParametersResult(successful=False, reason="Ki must be >= 0")
                else:
                    self.ki = param.value # Update internal variable
                    self.get_logger().info(f"Ki updated to {self.ki}")

            if param.name == "kd":
                if param.value < 0.0:
                    self.get_logger().warn("Kd cannot be negative.")
                    return SetParametersResult(successful=False, reason="Kd must be >= 0")
                else:
                    self.kd = param.value # Update internal variable
                    self.get_logger().info(f"Kd updated to {self.kd}")
                
            if param.name == "Ts":
                if param.value < 0.0:
                    self.get_logger().warn("Ts cannot be negative.")
                    return SetParametersResult(successful=False, reason="Ts must be >= 0")
                else:
                    self.Ts = param.value # Update internal variable
                    self.get_logger().info(f"Ts updated to {self.Ts}")

        return SetParametersResult(successful=True)


def main(args=None):
    rclpy.init(args=args)
    node = PIDController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
