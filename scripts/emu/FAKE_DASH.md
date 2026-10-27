# Trying REau without the bike: the fake dash

The Tripper dash is on the motorcycle, and REau only talks to it over the dash's own Wi-Fi. `fake_dash.py` plays the
dash on your computer, and a **debug build** of REau can be pointed at it, so you can change the picture, the joystick
or the settings and see the result without going to the bike.

What the fake dash does:

- answers the key exchange (the RSA public key, `07 01 01`), so REau reaches "Transmitting";
- sends a heartbeat, so REau's watchdog does not end the session, and confirms each frame it decodes (`09 06 55`, `09 04 55`);
- **records the video** REau sends (the real 526×300 H.264 stream) so you can look at it;
- **presses the joystick buttons** (`09 00 0001 XX`) when you ask.

What it does not do: it is not the dash. It draws nothing itself (the round glass and the ring the dash puts over the
picture are drawn afterwards, by `frames --mask`, from measured numbers), it does not judge colours, brightness or how
the real firmware reacts, and it skips the Wi-Fi part (joining `RE_xxxx`, the saved password, auto-join). What you
settle here still needs one ride, or one minute on the bike, to confirm.

## What you need

- A computer and the phone **on the same Wi-Fi network** (the router must not isolate clients; guest networks usually do).
- The phone with USB debugging on, connected by `adb`, and **unlocked** (a locked phone shows a black screen and ignores taps).
- JDK 21 and the Android SDK, as for any build of REau (see the README).
- Python 3.9 or newer, and `ffmpeg` (`brew install ffmpeg`) to look at the recorded video.
- Android Auto on the phone with its developer "head unit server" available, as for a normal ride. In the Lite edition,
  REau opens Android Auto's settings by itself the first time; touch ⋮ and "Start head unit server".

## Quick start

From the repository root, in two terminals.

```
cd scripts/emu
make setup          # once: a Python environment with the two packages in requirements.txt
make install        # the debug build of the Lite edition on the phone (the one with the test hook)
```

Terminal 1, leave it running:

```
make dash           # the fake dash; it prints "phone at <address>" once REau reaches it
```

Terminal 2:

```
make phone-host     # tells the phone's debug app to use this computer as the dash
make start          # switches REau on (or touch Encender on the phone)
make button B=left  # presses a joystick button; see the list below
make frames         # cuts the recorded video into PNG frames with the round glass and the ring drawn over them
make phone-clear    # back to the real dash: ALWAYS do this when you are done
```

`make help` repeats this list. The variables you may want: `APP` (the app id, `com.reau.app.lite` by default; the full
edition is `com.reau.app`, but it is the Lite one that is tried here), `IP` (this computer's address, when it guesses wrong),
`OUT` (where the video goes) and `B` (the button).

macOS asks once whether Python may accept incoming connections: allow it, or the phone never reaches the fake dash.

## What `make phone-host` does

A debug build of REau reads one file, `lan_dash_host.txt`, in its own external folder on the phone:

```
/sdcard/Android/data/com.reau.app.lite/files/lan_dash_host.txt      one line: an IPv4 address
```

While that file holds an address, REau does not join the bike's Wi-Fi: it sends the control packets to that address on
UDP 2000 and the video on UDP 5000, and listens on 2002, exactly as it does with the dash at 192.168.1.1. `make
phone-host` writes the file (with `adb`) and `make phone-clear` removes it. The ride log says so when it is in use
(`test dash on the local network: <address>`), and a **release build never reads the file**. The code is
`app/src/main/java/com/reau/app/service/LanTestDash.kt`, tested by `LanTestDashTest`.

The file is read when REau is switched on, so a change of address (or `phone-clear`) takes effect the next time you
touch Encender.

Without `make`, the same by hand:

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python3 fake_dash.py run --out fake_dash_out
.venv/bin/python3 fake_dash.py phone-host                 # or: phone-host 192.168.0.13 / phone-host clear
.venv/bin/python3 fake_dash.py button left
.venv/bin/python3 fake_dash.py frames fake_dash_out/dash-<time>.h264 --out fake_dash_frames --fps 0.5 --mask
```

## The buttons

`make button B=<name>`, with the names below, or a raw code (`B=0x13`). The dash sends different codes in its two modes:

| Name | Code | What the dash sent it for |
|---|---|---|
| `left`, `right`, `down`, `click` | 0x14, 0x13, 0x15, 0x18 | the joystick in the dash's **map** mode (zoom out/in, down, the centre) |
| `prev`, `next`, `vol-up`, `vol-down`, `play` | 0x0A, 0x09, 0x06, 0x07, 0x05 | the joystick in the dash's **media** mode |
| `back` | 0x12 | the back button (twice within 0.7 s is the apps menu) |

What REau does with each one is on the Joystick page of the app. The four arrows move Android Auto's focus; "Use the
four arrows" sets them. In the apps menu the first focus is **Exit**: do not press Confirm right after opening it.

## Looking at the picture

The recording is the stream the dash would have received: 526×300, raw H.264, one file for each run of `make dash`
(`fake_dash_out/dash-<time>.h264`). `make frames` cuts the newest one into `fake_dash_frames/frame-0001.png`, ... every two
seconds, and draws over each:

- the **round glass**, 526 px across, which hides the two top corners (`DashGlass`);
- the **dash's own ring**, 120 px across at the lower left, which covers part of the picture (`DashMask`).

Both are the numbers measured on a real dash, copied into `fake_dash.py` (`GLASS`, `RING`); if they change in the app, change
them there too. For the whole stream as one sheet: `ffmpeg -framerate 4 -i FILE -vf "fps=1/3,scale=263:150,tile=6x6" sheet.png`.

Tips from trying it:

- A raw `.h264` file has no clock: tell ffmpeg the real rate (`-framerate 4`, as `make frames` does) or `fps=` counts the wrong seconds.
- Decode from the start (as `make frames` does). Seeking near the end of the file (`-sseof`) lands on a frame without
  its parameters and gives a black or stale picture.
- An `error while decoding MB` or `cbp too large` line from ffmpeg at the very start is harmless: it is the first frame.
- A notification on the phone (a chat message, say) appears over Android Auto's picture, and so in the recording.
- Changing the DPI, the margins or the side of the apps bar restarts Android Auto's session: wait 10 to 15 seconds before
  you look at the new picture.
- To compare settings, change one at a time on the "Android Auto screen" page of the app, wait, and cut the frames; the page's
  own preview also draws the glass and the ring (the "Máscara" button).

## When something does not work

| Symptom | Likely cause |
|---|---|
| `make phone-host`: "adb sees no phone" | the cable or USB debugging; `adb devices` must list it as `device` |
| The phone does nothing for `adb` taps; screenshots are black | it is locked; unlock it (never leave a PIN to a script) |
| REau says "Transmitting" but `make dash` prints nothing | the phone is not writing to this computer: wrong `IP`, another network, client isolation, or the macOS firewall prompt was declined |
| REau stays waiting for Android Auto | the head unit server is off: touch ⋮ then "Start head unit server" in Android Auto's settings |
| REau refuses to start, or never hears the dash | another REau, or another app of the dash, holds UDP 2002: stop it |
| `make frames`: "has no video yet" | REau was not switched on against the fake dash; run `make phone-host`, then `make start` |
| On the bike REau never joins the dash | `make phone-clear` was not run: the file is still on the phone |

## Tests

```
make test                                     # the fake dash against the phone's side of the protocol
./gradlew :app:testLiteDebugUnitTest --tests '*LanTestDashTest'
```

`test_fake_dash.py` plays the phone with the byte layouts of `DashCommands` and `DashAuth` (auth request, RSA session key,
FU-A video, buttons) and checks what comes back.

## About the code

`fake_dash.py` is written from REau's own protocol code (`dash/protocol/`, `DashSession`, `DashAuth`; the K1G format is
credited in `NOTICE`). It does not copy another project's emulator. The control packet format, in short: the phone sends
`[len][count][4 zeros][02 01 00 05]["K1G "][seq]` followed by TLVs `[type][sub][len:2][value]`; the dash answers with
`[len][count][4 ignored]` followed by TLVs, to the phone's UDP 2002.
