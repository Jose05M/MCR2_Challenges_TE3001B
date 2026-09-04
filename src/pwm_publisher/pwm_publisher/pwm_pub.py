import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import random


class PwmPublisher(Node):

    def __init__(self):
        super().__init__('pwm_pub')
        self.publisher_ = self.create_publisher(Float32, '/cmd_pwm', 10)
        self.timer = self.create_timer(5.0, self.publish_pwm)

        self.get_logger().info("PWM Random Publisher iniciado")

    def publish_pwm(self):
        msg = Float32()
        self.value = random.uniform(-1.0, 1.0)
        msg.data = float(self.value)
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publicando: {msg.data:.3f}')


def main(args=None):
    rclpy.init(args=args)
    node = PwmPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
