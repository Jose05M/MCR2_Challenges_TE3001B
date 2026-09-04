import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
import math

# Class Definition


class SignalProcessing(Node):
    def __init__(self):
        super().__init__('signal_proc')
        # Variables para guardar datos recibidos
        self.signal = 0.0
        self.time = 0.0
        self.phase_shift = math.pi / 2  # Desfase (hardcoded) 90°

        self.signal_subscription = self.create_subscription(
            Float32, '/signal', self.signal_callback, 10)

        self.time_subscription = self.create_subscription(
            Float32, '/time', self.time_callback, 10)

        # Publisher
        self.process_publisher = self.create_publisher(Float32, '/proc_signal', 10)
        timer_period = 0.1  # 0.1 seconds -> 10 Hz
        self.timer = self.create_timer(timer_period, self.timer_cb)

    def signal_callback(self, msg):  # Callback del signal
        self.signal = msg.data

    def time_callback(self, msg):  # Callback del time
        self.time = msg.data

    def timer_cb(self):  # Callback de procesamiento (10 Hz)
        sin_t = self.signal
        cos_t = math.cos(self.time)

        shifted_signal = (sin_t * math.cos(self.phase_shift) + cos_t * math.sin(self.phase_shift))
        offset_signal = shifted_signal + 1.0
        processed = 0.5 * offset_signal

        # Publicar resultado
        msg = Float32()
        msg.data = float(processed)
        self.process_publisher.publish(msg)
        # Imprimir
        self.get_logger().info(f"Time: {self.time:.2f} | Proc_Signal: {processed:.2f}")

# Main


def main(args=None):
    rclpy.init(args=args)
    signal_processing = SignalProcessing()
    try:
        rclpy.spin(signal_processing)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():  # Ensure shutdown is only called once
            rclpy.shutdown()
        signal_processing.destroy_node()


# Execute Node
if __name__ == '__main__':
    main()
