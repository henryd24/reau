# Trying REau without the bike: the fake dash on this computer, a debug build on the phone. See FAKE_DASH.md.
#
#   make setup                  once: the Python environment
#   make install                the debug build of the Lite edition on the phone (adb)
#   make dash                   plays the dash (leave it running)      -- in a second terminal:
#   make phone-host             points the phone at this computer
#   make start                  switches REau on (the phone unlocked)
#   make button B=left          presses a joystick button
#   make frames                 cuts the recorded video into PNG frames, with the glass and the dash's ring drawn
#   make phone-clear            back to the real dash (ALWAYS do this when you are done)
#
# Variables: APP (the app id, default the Lite edition), OUT (where the video goes), IP (this computer, by default its own).

APP ?= com.reau.app.lite
OUT ?= fake_dash_out
IP  ?=
B   ?= left
ROOT := $(abspath ../..)
VENV := .venv
PY := $(VENV)/bin/python3
FAKE := $(PY) -u fake_dash.py

.PHONY: setup install dash phone-host phone-clear start button frames test help

help:
	@sed -n '3,12p' Makefile

$(PY):
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -q -r requirements.txt

setup: $(PY)

install:
	cd $(ROOT) && ./gradlew installLiteDebug

dash: $(PY)
	$(FAKE) run --out $(OUT)

phone-host: $(PY)
	$(FAKE) phone-host $(IP) --app $(APP)

phone-clear: $(PY)
	$(FAKE) phone-host clear --app $(APP)

start:
	adb shell am force-stop $(APP)
	adb shell am start -a com.reau.app.QUICK_START -n $(APP)/com.reau.app.MainActivity

button: $(PY)
	$(FAKE) button $(B)

frames: $(PY)
	@f=$$(ls -t $(OUT)/*.h264 | head -1); echo "cutting $$f"; $(FAKE) frames $$f --out fake_dash_frames --fps 0.5 --mask

test: $(PY)
	$(PY) -W ignore test_fake_dash.py
