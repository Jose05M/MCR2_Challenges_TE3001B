import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import math
import time

# Class Definition


class SignalGenerator(Node):
    def __init__(self):
        super().__init__('signal_gen')
        # Write your code here
        self.signal_publisher = self.create_publisher(Float32, '/signal', 10)
        self.time_publisher = self.create_publisher(Float32, '/time', 10)
        timer_period = 0.1  # 0.1 seconds -> 10 Hz
        self.timer = self.create_timer(timer_period, self.timer_cb)
        self.start_time = time.time()

        # Timer Callback
    def timer_cb(self):
        t = time.time() - self.start_time  # Tiempo t
        signal = math.sin(t)  # señal
        msg_signal = Float32()
        msg_time = Float32()

        msg_signal.data = float(signal)
        msg_time.data = float(t)

        self.signal_publisher.publish(msg_signal)
        self.time_publisher.publish(msg_time)
        self.get_logger().info(f"Time: {t:.2f} | Signal: {signal:.2f}")


def main(args=None):
    rclpy.init(args=args)
    signal_generator = SignalGenerator()
    try:
        rclpy.spin(signal_generator)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():  # Ensure shutdown is only called once
            rclpy.shutdown()
        signal_generator.destroy_node()


# Execute Node
if __name__ == '__main__':
    main()
