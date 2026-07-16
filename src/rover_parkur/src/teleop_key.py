#!/usr/bin/env python3
"""
4 Motorlu Rover - Bağımsız Motor Teleop Kontrolü
=================================================
Her teker için ayrı klavye tuşu var.
Komutlar direkt /wheel_velocity_controller/commands topic'ine gönderilir.

Tuş Düzeni:
  [Q] [W]   [E] [R]
   ↓   ↑     ↑   ↓
  ÖN SOL    ÖN SAĞ

  [A] [S]   [D] [F]
   ↓   ↑     ↑   ↓
 ARKA SOL  ARKA SAĞ

Genel:
  SPACE  → Tüm motorları durdur
  Ctrl+C → Çıkış
"""

import sys
import select
import termios
import tty
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

# ============================================================
# HIZLANMA ADIMI (rad/s) — Buradan değiştirebilirsin
# ============================================================
STEP      = 1.0    # Her tuşa basışta hız kaç rad/s değişsin
MAX_SPEED = 15.0   # Maksimum hız (rad/s)
# ============================================================

BANNER = """
╔══════════════════════════════════════════════════════╗
║         4 Motorlu Rover - Bağımsız Kontrol           ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║    [Q]İLERİ   [W]İLERİ  │  [E]İLERİ   [R]İLERİ     ║
║    ÖN SOL     ÖN SAĞ    │  ÖN SAĞ   ARKA SOL (!)    ║
║                          │                           ║
║    Tuş Haritası:                                     ║
║    W → Ön Sol  İleri    Q → Ön Sol  Geri            ║
║    E → Ön Sağ  İleri    R → Ön Sağ  Geri            ║
║    S → Arka Sol İleri   A → Arka Sol Geri            ║
║    D → Arka Sağ İleri   F → Arka Sağ Geri            ║
║    SPACE → Tüm Motorları DURDUR                      ║
║    Ctrl+C → Çıkış                                    ║
╚══════════════════════════════════════════════════════╝
"""

def get_key(settings):
    """Terminal'den 1 tuş oku (bloklama yok)."""
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key


class MotorTeleop(Node):
    def __init__(self):
        super().__init__('motor_teleop')

        # /wheel_velocity_controller/commands topic'ine yayın yap
        # Float64MultiArray: [ön_sol, ön_sağ, arka_sol, arka_sağ]
        self.pub = self.create_publisher(
            Float64MultiArray,
            '/wheel_velocity_controller/commands',
            10
        )

        self.settings = termios.tcgetattr(sys.stdin)

        # 4 motor hızı: [ön_sol, ön_sağ, arka_sol, arka_sağ]
        self.speeds = [0.0, 0.0, 0.0, 0.0]
        # İsimler (print için)
        self.names = ['ÖN-SOL', 'ÖN-SAĞ', 'ARK-SOL', 'ARK-SAĞ']

        self.get_logger().info('Motor Teleop başlatıldı.')

    def clamp(self, val):
        """Hızı maksimum sınır içinde tut."""
        return max(-MAX_SPEED, min(MAX_SPEED, val))

    def run(self):
        print(BANNER)
        self.print_speeds()

        try:
            while rclpy.ok():
                key = get_key(self.settings)

                changed = True

                # ── ÖN SOL (indeks 0) ──────────────────────────
                if key == 'w':    # İleri
                    self.speeds[0] = self.clamp(self.speeds[0] + STEP)
                elif key == 'q':  # Geri / yavaşla
                    self.speeds[0] = self.clamp(self.speeds[0] - STEP)

                # ── ÖN SAĞ (indeks 1) ──────────────────────────
                elif key == 'e':  # İleri
                    self.speeds[1] = self.clamp(self.speeds[1] + STEP)
                elif key == 'r':  # Geri / yavaşla
                    self.speeds[1] = self.clamp(self.speeds[1] - STEP)

                # ── ARKA SOL (indeks 2) ────────────────────────
                elif key == 's':  # İleri
                    self.speeds[2] = self.clamp(self.speeds[2] + STEP)
                elif key == 'a':  # Geri / yavaşla
                    self.speeds[2] = self.clamp(self.speeds[2] - STEP)

                # ── ARKA SAĞ (indeks 3) ────────────────────────
                elif key == 'd':  # İleri
                    self.speeds[3] = self.clamp(self.speeds[3] + STEP)
                elif key == 'f':  # Geri / yavaşla
                    self.speeds[3] = self.clamp(self.speeds[3] - STEP)

                # ── GENEL KONTROL ──────────────────────────────
                elif key == ' ':  # SPACE → hepsini durdur
                    self.speeds = [0.0, 0.0, 0.0, 0.0]
                elif key == '\x03':  # Ctrl+C → çıkış
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
            # Çıkışta tüm motorları durdur
            self.speeds = [0.0, 0.0, 0.0, 0.0]
            self.publish()
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
            print('\nTüm motorlar durduruldu. Çıkıldı.')

    def publish(self):
        """Motor hızlarını topic'e gönder."""
        msg = Float64MultiArray()
        msg.data = self.speeds
        self.pub.publish(msg)

    def print_speeds(self):
        """Mevcut motor hızlarını ekrana yaz."""
        # \r ile aynı satırın üzerine yaz
        line = '  |  '.join(
            f'{name}: {spd:+6.1f}' for name, spd in zip(self.names, self.speeds)
        )
        sys.stdout.write(f'\r  {line}    ')
        sys.stdout.flush()


def main(args=None):
    rclpy.init(args=args)
    node = MotorTeleop()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
