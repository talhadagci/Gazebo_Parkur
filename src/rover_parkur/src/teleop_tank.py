#!/usr/bin/env python3
"""
2 Kanalli Tank Teleop - SOL ve SAG motor gruplari
==================================================
Sol grup  = on sol + arka sol teker (ayni hiz)
Sag grup  = on sag + arka sag teker (ayni hiz)

Komutlar /wheel_velocity_controller/commands topic'ine
[on_sol, on_sag, arka_sol, arka_sag] = [sol, sag, sol, sag]
seklinde gonderilir. Kontrolcu tarafinda degisiklik gerekmez.

Tus Duzeni =
  W -> SOL grup ileri  (+1 rad/s)
  A -> SOL grup geri   (-1 rad/s)
  S -> SAG grup ileri  (+1 rad/s)
  D -> SAG grup geri   (-1 rad/s)
  SPACE -> tum motorlari durdur
  Ctrl+C -> cikis
"""

import sys
import select
import termios
import tty
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

# ============================================================
# HIZLANMA ADIMI (rad/s) - Buradan degistirebilirsin
# ============================================================
STEP      = 1.0    # Her tusa basista hiz kac rad/s degissin
MAX_SPEED = 15.0   # Maksimum hiz (rad/s)
# ============================================================

BANNER = """
╔══════════════════════════════════════════════╗
║        2 Kanalli Tank Teleop (SOL/SAG)       ║
╠══════════════════════════════════════════════╣
║                                              ║
║   [W] SOL ileri        [S] SAG ileri         ║
║   [A] SOL geri         [D] SAG geri          ║
║                                              ║
║   SPACE -> DUR         Ctrl+C -> Cikis       ║
║                                              ║
║   Saga donus  = W (sol hizlanir)             ║
║   Sola donus  = S (sag hizlanir)             ║
║   Yerinde don = W + D  veya  S + A           ║
╚══════════════════════════════════════════════╝
"""


def get_key(settings):
    """Terminal'den 1 tus oku (bloklama yok)."""
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


class TankTeleop(Node):
    def __init__(self):
        super().__init__('tank_teleop')

        # [on_sol, on_sag, arka_sol, arka_sag] sirasiyla yayinlanir
        self.pub = self.create_publisher(
            Float64MultiArray,
            '/wheel_velocity_controller/commands',
            10
        )

        self.settings = termios.tcgetattr(sys.stdin)

        # Sadece 2 deger tutuyoruz = sol ve sag grup hizi
        self.sol = 0.0
        self.sag = 0.0

        self.get_logger().info('Tank Teleop baslatildi (W/A sol, S/D sag).')

    def clamp(self, val):
        """Hizi maksimum sinir icinde tut."""
        return max(-MAX_SPEED, min(MAX_SPEED, val))

    def run(self):
        print(BANNER)
        self.print_speeds()

        try:
            while rclpy.ok():
                key = get_key(self.settings)

                changed = True

                # ── SOL GRUP (on sol + arka sol) ───────────────
                if key == 'w':    # Ileri
                    self.sol = self.clamp(self.sol + STEP)
                elif key == 'a':  # Geri
                    self.sol = self.clamp(self.sol - STEP)

                # ── SAG GRUP (on sag + arka sag) ───────────────
                elif key == 's':  # Ileri
                    self.sag = self.clamp(self.sag + STEP)
                elif key == 'd':  # Geri
                    self.sag = self.clamp(self.sag - STEP)

                # ── GENEL KONTROL ──────────────────────────────
                elif key == ' ':  # SPACE -> hepsini durdur
                    self.sol = 0.0
                    self.sag = 0.0
                elif key == '\x03':  # Ctrl+C -> cikis
                    break
                else:
                    changed = False

                if changed:
                    self.publish()
                    self.print_speeds()

                rclpy.spin_once(self, timeout_sec=0.01)

        except Exception as e:
            print(f'\nHata: {e}')
        finally:
            # Cikista tum motorlari durdur
            self.sol = 0.0
            self.sag = 0.0
            self.publish()
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
            print('\nTum motorlar durduruldu. Cikildi.')

    def publish(self):
        """Grup hizlarini 4 tekere dagitip gonder."""
        msg = Float64MultiArray()
        # Sira = [on_sol, on_sag, arka_sol, arka_sag]
        msg.data = [self.sol, self.sag, self.sol, self.sag]
        self.pub.publish(msg)

    def print_speeds(self):
        """Mevcut grup hizlarini ekrana yaz."""
        sys.stdout.write(f'\r  SOL: {self.sol:+6.1f} rad/s  |  SAG: {self.sag:+6.1f} rad/s    ')
        sys.stdout.flush()


def main(args=None):
    rclpy.init(args=args)
    node = TankTeleop()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
