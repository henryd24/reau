# REau on a Himalayan 450 (Tripper dash)

Español: [himalayan-450.es.md](himalayan-450.es.md)

Written with a Samsung S25 Ultra (Android 17, Android Auto 17.9) and a Himalayan 450. What differs on another phone or another
firmware is said where it applies. What could not be confirmed is marked **unconfirmed**.

## 1. What to install

The **Lite** edition (`com.reau.app.lite`) is the recommended one: it asks for no Accessibility service and needs one manual step
per session (two taps). Install it from the Releases page, or build it:

```
./gradlew assembleLiteRelease
adb install -r app/build/outputs/apk/lite/release/*.apk
```

Building needs JDK 21 and the Android SDK (see the [README](../README.md)). For a trial build, `./gradlew installLiteDebug`
installs it straight onto the phone.

## 2. Prepare Android Auto (once)

REau needs the **head unit server** that Android Auto offers in its developer mode.

1. On the phone: Settings › Android Auto, scroll to the end and touch **"Version" about ten times**; confirm.
2. The **⋮** menu with the developer settings appears.
3. In that menu is **"Start head unit server"**. It is what you touch each time you set out (the server turns off when the session
   ends and after the phone restarts).

If the menu does not appear, developer mode did not turn on: repeat the ten touches.

## 3. The first time with the bike

1. Switch the bike on and keep the phone near the dash.
2. Open REau, accept the terms and grant the permissions it asks for (the **Permissions** screen says which one is missing and what
   each is for; the location is used only to see the Wi-Fi list and find the dash's full name).
3. Touch **Turn on**. In the Lite, REau opens Android Auto's settings by itself: touch **⋮ › Start head unit server** and go back
   to REau.
4. Android may ask whether REau may connect to the dash's Wi-Fi (`RE_xxxx_yymmdd`): touch **Connect**.
5. When the app says **Streaming**, the dash shows Android Auto.

Later times there is a shortcut on the app's icon and a Quick Settings tile, **Turn REau on**: they open REau and switch the
projection on at once.

## 4. The picture: what shows and what does not

The dash's glass is round and cuts the two top corners. The dash also draws a **ring with orange icons** over the lower left of the
picture, and REau cannot turn it off. So with Android Auto in its usual layout (buttons on the left), the microphone and the apps
launcher button are covered.

The **Android Auto screen** page (a shortcut on the main screen) has a **Mask** button that draws the glass and the ring over the
preview, to see what reaches the glass without going to the bike.

The setting that worked best:

| Setting | Value | Why |
|---|---|---|
| Mode | **Whole image** | no edge is lost: the search bar and the whole side bar show |
| Android Auto DPI | 180 (240 for larger text) | at 240 Android Auto shows fewer things at once |
| **Apps bar on the right** | on | the side bar moves to the right, away from the dash's ring |
| Move vertically | to taste | sets the picture against the bottom edge |

"Fill the dome" with the bar on the right gives a much larger picture and also keeps the whole side bar in view, but it cuts the
search bar on the left. Changing the DPI, the margins or the side of the bar restarts Android Auto's session: wait a few seconds.

**Unconfirmed on the bike:** these comparisons were made with a fake dash and the measures in the code; the final result is seen on
the real dash.

## 5. The joystick

On the **Dash joystick** page, the **Use the four arrows** button sets up, down, left and right to move Android Auto's focus in two
dimensions, and the centre as **Confirm**. With that:

- **Apps menu:** two quick taps (under 0.7 s) on **Back**.
- **Back:** one tap on Back.
- **In the dash's map mode**, up belongs to the dash (it asks whether to leave the navigation) and the centre switches to media; so
  there only left, right and down are available.
- **Careful with "Exit":** when the apps menu opens, the first focus is on **Exit**. Pressing Confirm right then closes Android Auto
  (REau opens it again within a second, but the route on screen is lost). Move the focus before confirming.

"Reset to default" on the same page goes back to the previous joystick.

## 6. When something does not work

| What happens | What to try |
|---|---|
| "Android Auto does not accept the connection" | the server is off: ⋮ › "Start head unit server"; after a phone restart it has to be repeated |
| The dash keeps the last frame, or goes black | force-stop Android Auto and switch REau on again |
| It does not connect to the dash | an active VPN (leave REau out of the tunnel), battery saver, or the other REau edition running: they must not run at once |
| Android Auto closes with the screen off | **unconfirmed**: twice in the logs the session ended just as the screen turned off; if it happens, note the time and share the logs |
| I changed the setting and it looks wrong | "Reset to default" on the Android Auto screen page |

**Sharing the logs** (to analyse them on the computer): in Settings, under **Debug**, there is a share button. The log carries no
location; `scripts/registro/` has tools to read it.

## 7. Trying things without the bike

To change something and see the result without going to the bike, there is a fake dash for the computer:
[scripts/emu/FAKE_DASH.md](../scripts/emu/FAKE_DASH.md).

## Safety

Do not handle the phone while riding. Use the handlebar joystick, and only when the motorcycle is in a safe condition.
