# Trying the stream rate and measuring the delay

Español: [stream-latency.es.md](stream-latency.es.md)

On the dash the map moves in steps: REau sends 4 pictures a second (profile A) and only 2 (profile B) when the route's next
maneuver is more than 1 km away or the speed is over about 65 km/h. Those two values, 4 and 2 fps at 100 kbps for each frame a
second, are the ones known to work on this dash: with more, the video "lagged at speed" (the dash seems to pile pictures up, and
then the delay grows instead of shrinking). This guide is for trying other values on the bike and for measuring the delay, so
the choice is made with numbers.

Nothing changes unless you change it: the defaults stay 4 / 2 fps and "Lower rate".

## What can be changed (Settings › Video profiles)

| Setting | Default | What it does |
|---|---|---|
| **Profile A rate** (experimental) | 4 fps | the rate while a maneuver is near and the speed is low; 4 to 10 in steps of 2. The bitrate follows: 100 kbps for each frame a second (never over 1 Mbps, which made the dash hitch) |
| **Profile B rate** | 2 fps | the rate far from a maneuver and at speed; from 2 up to profile A's |
| **When the two profiles disagree** | Lower rate | the maneuver profile and the speed profile often ask for different rates. *Lower rate* uses B if either asks for it (the lightest picture); *Higher rate* uses A if either does (the smoothest). It applies at once |

The rates take a new stream (the picture freezes for a second); the policy is read all the time.

A good order to try them, one step at a time, parked first and then on a short ride:

1. **Higher rate** with 4 / 2 fps. It costs nothing in bits: it only keeps profile A when either profile allows it.
2. **6 / 4 fps**, then **8 / 4 fps**, with *Higher rate* or *Lower rate*.
3. At the first sign of the picture falling behind (the maneuver arrow arrives late, the picture jumps ahead after a pause, the dash
   goes black), go back one step. 4 / 2 fps is always safe.

## Measuring the delay with the phone's clock

The delay is hard to judge by eye. REau can write the phone's clock, with milliseconds, on the dash's video, and the
phone's own screen shows the same clock live; filmed together, the difference between the two is the time the picture takes to
reach the dash.

1. Open **Android Auto screen** (the shortcut on the main screen) and scroll to the end: **Phone clock on the video**. Switch it on.
2. Put the box on the picture: with the whole image shown, the box at the default place is above it, outside the preview. Raise **Vertical
   (Y)** to about 90 px (and **Horizontal (X)** to taste). The same box, with the same clock, is drawn on the preview of that page.
3. Leave that page open on the phone, with the projection on, and put the phone **beside the dash**.
4. **Film both in one shot**, in slow motion or at 60 fps if the camera allows it, for 10 to 20 seconds. Do it **parked, or with
   someone else filming**: never film while riding.
5. Pause the video on a few frames and read both clocks. The phone's is the current time; the dash's is the time the frame was composed.
   *Delay = phone clock − dash clock.* The phone's own display adds a few tens of milliseconds, small next to the dash's.
6. Repeat with the settings you want to compare (4 / 2, 6 / 4, 8 / 4), standing still and, if it can be done safely, with the map
   moving (zooming with the joystick).
7. Switch the clock off when done: it is a test aid, not for riding.

To read the video later: `ffmpeg -i video.mp4 -vf fps=10 frames/f-%04d.png`, and look at the frames where both clocks are readable.

## Trying it without the bike

The fake dash ([scripts/emu/FAKE_DASH.md](../scripts/emu/FAKE_DASH.md)) records the stream and shows that the rates really change
(the 5-second line of the ride log says `target=8 sent=8.0`, and the dash acknowledges the same). It cannot say how the real dash
copes: that is what the filmed clock is for.

## Putting it back

Profile A 4 fps, profile B 2 fps, *Lower rate*, clock off. There is no restore button in the Video profiles group; use the steppers.
