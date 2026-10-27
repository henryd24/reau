#!/usr/bin/env python3
"""A stand-in for the Tripper dash, to try REau without the bike (debug builds only).

What it plays, from REau's own protocol code (dash/protocol, DashSession, DashAuth):
  - UDP :2000  the phone's control packets in; the dash's answers go to the phone's :2002.
  - UDP :5000  the phone's RTP H.264 (single NAL and FU-A); written as Annex-B to --out, so what the dash would
               have shown can be looked at (`python3 fake_dash.py frames FILE`; see FAKE_DASH.md).
  - the key exchange (08 04 -> its RSA public key 07 00 / 07 03, 08 00 -> 07 01 01), a heartbeat so the phone's RX
    watchdog stays quiet, and the decode notices (09 06 55 per keyframe, 09 04 55 per other frame).
  - joystick presses (09 00 0001 XX): `python3 fake_dash.py button left` while the dash runs.

On the phone (a debug build of REau): put the computer's IPv4 address in the file
`Android/data/<app id>/files/lan_dash_host.txt` (see `phone-host`), then switch REau on. The phone and the
computer must be on the same network (client isolation off).

Needs the `cryptography` package. Run:  python3 fake_dash.py run [--out DIR]
"""
from __future__ import annotations

import argparse
import datetime
import os
import socket
import struct
import subprocess
import sys
import threading
import time

PHONE_RX_PORT = 2002
CONTROL_PORT = 2999  # on 127.0.0.1: `button` talks to a running dash through it
RSA_BITS = 1024
HEARTBEAT_S = 0.5

# What a press is, by the code the dash sends (REau's DashButtonEvent and JoystickMap).
BUTTONS = {
    "map-right": 0x13, "map-left": 0x14, "map-down": 0x15, "map-click": 0x18,
    "next": 0x09, "prev": 0x0A, "vol-up": 0x06, "vol-down": 0x07, "play": 0x05,
    "back": 0x12,
    # Short names for the map mode, where the dash is at start.
    "left": 0x14, "right": 0x13, "down": 0x15, "click": 0x18,
}


def tlv(kind: int, sub: int, value: bytes) -> bytes:
    return bytes([kind, sub]) + struct.pack(">H", len(value)) + value


def to_phone(*tlvs: bytes) -> bytes:
    """A dash -> phone packet: [len][segment count][4 ignored] then the TLVs."""
    body = b"".join(tlvs)
    return struct.pack(">HH", 8 + len(body), len(tlvs)) + b"\0\0\0\0" + body


def from_phone(data: bytes) -> list[tuple[int, int, bytes]]:
    """The TLVs of a phone -> dash packet (they start after the 17-byte header, seq included)."""
    out, i = [], 17
    while i + 4 <= len(data):
        kind, sub, n = data[i], data[i + 1], struct.unpack(">H", data[i + 2:i + 4])[0]
        out.append((kind, sub, data[i + 4:i + 4 + n]))
        i += 4 + n
    return out


class Dash:
    def __init__(self, out_dir: str, log=print):
        from cryptography.hazmat.primitives.asymmetric import rsa
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=RSA_BITS)
        self.log = log
        self.peer: str | None = None
        self.ctrl = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ctrl.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ctrl.bind(("0.0.0.0", 2000))
        self.rtp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.rtp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.rtp.bind(("0.0.0.0", 5000))
        os.makedirs(out_dir, exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.video_path = os.path.join(out_dir, f"dash-{stamp}.h264")
        self.video = open(self.video_path, "wb")
        self.control = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.control.bind(("127.0.0.1", CONTROL_PORT))
        self.frames = self.keyframes = 0
        self.fu: bytearray | None = None
        self.au_idr = False
        self.stop = threading.Event()

    # ── sending ────────────────────────────────────────────────────────────
    def send(self, *tlvs: bytes) -> None:
        if self.peer:
            self.ctrl.sendto(to_phone(*tlvs), (self.peer, PHONE_RX_PORT))

    def press(self, code: int) -> None:
        self.send(tlv(0x09, 0x00, bytes([code])))
        self.log(f"-> button 0x{code:02X}")

    # ── the control plane ──────────────────────────────────────────────────
    def pubkey(self) -> None:
        from cryptography.hazmat.primitives.asymmetric import rsa  # noqa: F401
        n = self.key.public_key().public_numbers()
        modulus = n.n.to_bytes(RSA_BITS // 8, "big")
        self.send(tlv(0x07, 0x00, modulus), tlv(0x07, 0x03, n.e.to_bytes(4, "big")))
        self.log("auth: public key sent")

    def session_key(self, cipher: bytes) -> None:
        from cryptography.hazmat.primitives.asymmetric import padding
        # OpenSSL 3 answers a damaged block with random bytes instead of an error, so what came out is checked too:
        # a Wi-Fi name that is readable text, then the 32-byte AES key.
        ssid = None
        try:
            plain = self.key.decrypt(cipher, padding.PKCS1v15())
            ssid = plain[:-32].decode("utf-8") if len(plain) > 32 else None
        except Exception:
            pass
        if not ssid or not ssid.isprintable():
            self.log("auth: the session key could not be read, answering 07 01 00")
            self.send(tlv(0x07, 0x01, b"\x00"))
            return
        self.log(f"auth: session key for the Wi-Fi name {ssid!r}, answering 07 01 01")
        self.send(tlv(0x07, 0x01, b"\x01"))

    def control_loop(self) -> None:
        while not self.stop.is_set():
            try:
                data, addr = self.ctrl.recvfrom(65535)
            except OSError:
                return
            if self.peer != addr[0]:
                self.peer = addr[0]
                self.log(f"phone at {self.peer}")
            for kind, sub, value in from_phone(data):
                if (kind, sub) == (0x08, 0x04):
                    self.pubkey()
                elif (kind, sub) == (0x08, 0x00) and len(value) == RSA_BITS // 8:
                    self.session_key(value)

    def heartbeat_loop(self) -> None:
        while not self.stop.wait(HEARTBEAT_S):
            self.send(tlv(0x01, 0x01, b"\x00"))

    def command_loop(self) -> None:
        while not self.stop.is_set():
            try:
                data, _ = self.control.recvfrom(256)
            except OSError:
                return
            name = data.decode().strip()
            code = BUTTONS.get(name)
            if code is None:
                try:
                    code = int(name, 0)
                except ValueError:
                    self.log(f"unknown button {name!r}")
                    continue
            self.press(code)

    # ── the video ──────────────────────────────────────────────────────────
    def rtp_loop(self) -> None:
        last_log = time.time()
        while not self.stop.is_set():
            try:
                pkt, _ = self.rtp.recvfrom(65535)
            except OSError:
                return
            if len(pkt) < 13:
                continue
            marker = bool(pkt[1] & 0x80)
            payload = pkt[12:]
            kind = payload[0] & 0x1F
            if kind == 28:  # FU-A
                header = payload[1]
                if header & 0x80:
                    self.fu = bytearray([(payload[0] & 0xE0) | (header & 0x1F)])
                if self.fu is not None:
                    self.fu += payload[2:]
                    if header & 0x40:
                        self.nal(bytes(self.fu))
                        self.fu = None
            else:
                self.nal(payload)
            if marker:
                self.frames += 1
                code = 0x06 if self.au_idr else 0x04
                self.send(tlv(0x09, code, b"\x55"))
                if self.au_idr:
                    self.keyframes += 1
                self.au_idr = False
            if time.time() - last_log > 5 and self.frames:
                last_log = time.time()
                self.log(f"video: {self.frames} frames, {self.keyframes} keyframes -> {self.video_path}")

    def nal(self, nal: bytes) -> None:
        if (nal[0] & 0x1F) == 5 or b"\x00\x00\x00\x01\x65" in nal[:64]:
            self.au_idr = True
        self.video.write(b"\x00\x00\x00\x01" + nal)
        self.video.flush()

    def run(self) -> None:
        for target in (self.control_loop, self.heartbeat_loop, self.command_loop, self.rtp_loop):
            threading.Thread(target=target, daemon=True).start()
        self.log(f"fake dash up: control :2000, video :5000, buttons on 127.0.0.1:{CONTROL_PORT}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop.set()
            self.video.close()
            self.log(f"stopped; video in {self.video_path}")


def send_button(name: str) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(name.encode(), ("127.0.0.1", CONTROL_PORT))


def local_ip() -> str:
    """The address this computer reaches the network with (no packet is sent)."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect(("192.0.2.1", 9))
        return sock.getsockname()[0]


def phone_host(ip: str, app_id: str) -> None:
    """Writes the address into the debug app's own folder on the phone (adb); `--clear` goes back to the real dash."""
    state = subprocess.run(["adb", "get-state"], capture_output=True, text=True)
    if state.stdout.strip() != "device":
        sys.exit("adb sees no phone: connect it with USB debugging on (adb devices) and unlock it")
    folder = f"/sdcard/Android/data/{app_id}/files"
    if ip == "clear":
        subprocess.run(["adb", "shell", "rm", "-f", f"{folder}/lan_dash_host.txt"], check=True)
        print("the phone talks to the real dash again")
        return
    subprocess.run(["adb", "shell", "mkdir", "-p", folder], check=True)
    subprocess.run(["adb", "shell", f"echo {ip} > {folder}/lan_dash_host.txt"], check=True)
    print(f"the phone talks to the test dash at {ip} (from the next time REau is switched on)")


# What the rider sees of the dash's 526x300 frame (DashGlass, DashMask): the round glass cuts the top corners, and the dash
# draws its own ring over the lower left. Measured on a real dash; keep in step with those two files.
# REau sends 4 frames a second; a raw H.264 file has no clock, so ffmpeg is told.
STREAM_FPS = 4
GLASS = (263, 263, 263)
RING = (85, 233, 60)


def dash_view(png: str, scale: int = 2) -> None:
    """Draws the glass and the dash's ring over a 526x300 frame, in place (needs Pillow)."""
    from PIL import Image, ImageDraw
    frame = Image.open(png).convert("RGB")
    frame = frame.resize((frame.width * scale, frame.height * scale), Image.NEAREST)
    cx, cy, radius = (v * scale for v in GLASS)
    mask = Image.new("L", frame.size, 0)
    ImageDraw.Draw(mask).ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=255)
    out = Image.new("RGB", frame.size, (20, 20, 20))
    out.paste(frame, (0, 0), mask)
    rx, ry, rr = (v * scale for v in RING)
    ImageDraw.Draw(out).ellipse([rx - rr, ry - rr, rx + rr, ry + rr], fill=(236, 230, 215), outline=(200, 160, 60), width=3 * scale)
    out.save(png)


def frames(path: str, out_dir: str, fps: float, mask: bool = False) -> None:
    if not os.path.isfile(path) or os.path.getsize(path) < 1000:
        sys.exit(f"{path} has no video yet: switch REau on with the phone pointed at this computer (see FAKE_DASH.md)")
    os.makedirs(out_dir, exist_ok=True)
    done = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(STREAM_FPS), "-i", path, "-vf", f"fps={fps}", os.path.join(out_dir, "frame-%04d.png")],
    )
    if done.returncode != 0 or not any(n.endswith(".png") for n in os.listdir(out_dir)):
        sys.exit("ffmpeg could not read any frame (is it installed? `brew install ffmpeg`)")
    if mask:
        for name in sorted(os.listdir(out_dir)):
            if name.endswith(".png"):
                dash_view(os.path.join(out_dir, name))
    print(f"frames in {out_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="play the dash")
    run.add_argument("--out", default="fake_dash_out")
    btn = sub.add_parser("button", help="press a joystick button on a running dash: " + ", ".join(sorted(BUTTONS)))
    btn.add_argument("name")
    host = sub.add_parser("phone-host", help="tell the phone's debug app where the test dash is (adb)")
    host.add_argument("ip", nargs="?", default=None, help="default: this computer's address; `clear` undoes it")
    host.add_argument("--app", default="com.reau.app.lite")
    fr = sub.add_parser("frames", help="cut a recorded .h264 into PNG frames (needs ffmpeg)")
    fr.add_argument("file")
    fr.add_argument("--out", default="fake_dash_frames")
    fr.add_argument("--fps", type=float, default=1.0)
    fr.add_argument("--mask", action="store_true", help="draw the round glass and the dash's ring over each frame (needs Pillow)")
    args = parser.parse_args()
    if args.cmd == "run":
        Dash(args.out).run()
    elif args.cmd == "button":
        send_button(args.name)
    elif args.cmd == "phone-host":
        phone_host(args.ip or local_ip(), args.app) if args.ip != "clear" else phone_host("clear", args.app)
    else:
        frames(args.file, args.out, args.fps, args.mask)
    return 0


if __name__ == "__main__":
    sys.exit(main())
