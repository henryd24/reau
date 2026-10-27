"""The fake dash against the phone's side of the protocol, as REau's Kotlin code writes it (DashCommands, DashAuth)."""
import os
import socket
import struct
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import fake_dash  # noqa: E402

AUTH_REQUEST = bytes.fromhex("0016000200000000020100054b314720000804000101")
SEND_KEY_HEADER = bytes.fromhex("0095000200000000020100054B3147200008000080")


def parse_incoming(data):
    """K1GPacket.parseIncoming: segments from offset 8, as many as the count says."""
    count = struct.unpack(">H", data[2:4])[0]
    i, out = 8, []
    for _ in range(count):
        kind, sub, n = data[i], data[i + 1], struct.unpack(">H", data[i + 2:i + 4])[0]
        out.append((kind, sub, data[i + 4:i + 4 + n]))
        i += 4 + n
    return out


class FakeDashTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dash = fake_dash.Dash(tempfile.mkdtemp(), log=lambda *_: None)
        threading.Thread(target=cls.dash.control_loop, daemon=True).start()
        threading.Thread(target=cls.dash.rtp_loop, daemon=True).start()
        threading.Thread(target=cls.dash.command_loop, daemon=True).start()
        cls.phone = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cls.phone.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        cls.phone.bind(("0.0.0.0", fake_dash.PHONE_RX_PORT))
        cls.phone.settimeout(2)

    @classmethod
    def tearDownClass(cls):
        cls.dash.stop.set()
        cls.phone.close()

    def ask(self):
        return parse_incoming(self.phone.recvfrom(65535)[0])

    def test_handshake_video_and_buttons(self):
        from cryptography.hazmat.primitives.asymmetric import padding, rsa
        self.phone.sendto(AUTH_REQUEST, ("127.0.0.1", 2000))
        got = self.ask()
        self.assertEqual([(0x07, 0x00), (0x07, 0x03)], [(k, s) for k, s, _ in got])
        modulus, exponent = int.from_bytes(got[0][2], "big"), int.from_bytes(got[1][2], "big")
        self.assertEqual(128, len(got[0][2]))
        public = rsa.RSAPublicNumbers(exponent, modulus).public_key()
        cipher = public.encrypt(b"RE_TEST_000000" + os.urandom(32), padding.PKCS1v15())
        self.phone.sendto(SEND_KEY_HEADER + cipher, ("127.0.0.1", 2000))
        self.assertEqual([(0x07, 0x01, b"\x01")], self.ask())

        # A damaged session key is refused, so the phone asks again.
        self.phone.sendto(SEND_KEY_HEADER + os.urandom(128), ("127.0.0.1", 2000))
        self.assertEqual([(0x07, 0x01, b"\x00")], self.ask())

        # An IDR in two FU-A pieces, then a single-NAL P frame: a 09 06 55 and a 09 04 55.
        rtp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        head = lambda marker: bytes([0x80, (0x80 if marker else 0) | 96]) + b"\0" * 10
        indicator = (0x65 & 0xE0) | 28
        rtp.sendto(head(False) + bytes([indicator, 0x80 | 5]) + b"aa", ("127.0.0.1", 5000))
        rtp.sendto(head(True) + bytes([indicator, 0x40 | 5]) + b"bb", ("127.0.0.1", 5000))
        self.assertEqual([(0x09, 0x06, b"\x55")], self.ask())
        rtp.sendto(head(True) + bytes([0x41]) + b"cc", ("127.0.0.1", 5000))
        self.assertEqual([(0x09, 0x04, b"\x55")], self.ask())
        time.sleep(0.1)
        self.dash.video.flush()
        with open(self.dash.video_path, "rb") as f:
            self.assertEqual(b"\0\0\0\1\x65aabb\0\0\0\1\x41cc", f.read())

        fake_dash.send_button("left")
        self.assertEqual([(0x09, 0x00, b"\x14")], self.ask())
        fake_dash.send_button("0x12")
        self.assertEqual([(0x09, 0x00, b"\x12")], self.ask())


if __name__ == "__main__":
    unittest.main()
