#!/usr/bin/env python3
"""
Skid-steer kontrolcü: /cmd_vel (Twist) mesajını 4 bağımsız teker hızına çevirir
ve /wheel_velocity_controller/commands konusuna yayınlar.

Teker sırası: [ön sol, ön sağ, arka sol, arka sağ] (rover_controllers.yaml ile aynı)
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray

WHEEL_RADIUS = 0.19        # m
WHEEL_SEPARATION = 1.10    # m (sol-sağ teker arası mesafe)


class SkidSteerController(Node):
    def __init__(self):
        super().__init__('skid_steer_controller')

        self.declare_parameter('wheel_radius', WHEEL_RADIUS)
        self.declare_parameter('wheel_separation', WHEEL_SEPARATION)

        self.wheel_radius = self.get_parameter('wheel_radius').value
        self.wheel_separation = self.get_parameter('wheel_separation').value

        self.cmd_pub = self.create_publisher(
            Float64MultiArray, '/wheel_velocity_controller/commands', 10)
        self.cmd_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)

        self.get_logger().info(
            f'Skid-steer kontrolcü hazır (r={self.wheel_radius} m, '
            f'W={self.wheel_separation} m)')

    def cmd_vel_callback(self, msg: Twist):
        v = msg.linear.x    # ileri hız (m/s)
        w = msg.angular.z   # dönüş hızı (rad/s), pozitif = sola

        # Skid-steer kinematiği: sol ve sağ taraf teker açısal hızları (rad/s)
        left = (v - w * self.wheel_separation / 2.0) / self.wheel_radius
        right = (v + w * self.wheel_separation / 2.0) / self.wheel_radius

        cmd = Float64MultiArray()
        # [ön sol, ön sağ, arka sol, arka sağ]
        cmd.data = [left, right, left, right]
        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = SkidSteerController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
