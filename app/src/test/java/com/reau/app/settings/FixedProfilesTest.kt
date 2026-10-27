package com.reau.app.settings

import com.reau.app.dash.BitrateMode
import com.reau.app.dash.DashConfig
import com.reau.app.data.KeystoreBackedPrefsTest
import org.junit.Assert.assertEquals
import org.junit.Test

/**
 * The stream has two profiles and nothing else. Profile 1 is 4 frames a second at
 * 400 kbps, a constant bitrate, a keyframe every second; profile 2 is half of it, 2 frames a second at 200 kbps. Those
 * are the defaults and the values known to work on the dash. The mode and the keyframe are fixed; the two rates may be
 * raised to try them (to [DashConfig.EXPERIMENT_MAX_FPS]), the bitrate following at [DashConfig.BPS_PER_FPS] for each
 * frame a second; the navigation profiles are what moves the stream to profile 2 and back.
 */
class FixedProfilesTest {

    @Test
    fun `the defaults are profile 1`() {
        val s = REauSettings()
        assertEquals(4, s.fpsCeiling)
        assertEquals(400_000, s.streamBitrateBps)
        assertEquals(BitrateMode.CBR, s.bitrateMode)
        assertEquals(1, s.keyframeSec)
        assertEquals(true, s.aaNewProtocol)
    }

    @Test
    fun `the constants are the two profiles`() {
        assertEquals(listOf(4, 400_000, 1), listOf(DashConfig.PROFILE_FULL_FPS, DashConfig.PROFILE_FULL_BPS, DashConfig.PROFILE_KEYFRAME_SEC))
        assertEquals(listOf(2, 200_000), listOf(DashConfig.PROFILE_REDUCED_FPS, DashConfig.PROFILE_REDUCED_BPS))
        assertEquals("profile 2 is half of profile 1", DashConfig.PROFILE_FULL_BPS / 2, DashConfig.PROFILE_REDUCED_BPS)
        assertEquals("profile 2 is half of profile 1", DashConfig.PROFILE_FULL_FPS / 2, DashConfig.PROFILE_REDUCED_FPS)
    }

    @Test
    fun `a rate set in code is brought into what is offered, and the bitrate follows it`() {
        val s = REauSettings(fpsCeiling = 16, streamBitrateBps = 900_000, bitrateMode = BitrateMode.VBR, keyframeSec = 2).sanitized()
        assertEquals("the most that is offered", 10, s.fpsCeiling)
        assertEquals("100 kbps for each frame a second", 1_000_000, s.streamBitrateBps)
        assertEquals(BitrateMode.CBR, s.bitrateMode)
        assertEquals("the keyframe stays fixed", 1, s.keyframeSec)
        assertEquals("automatic keyframe is gone too", 1, REauSettings(keyframeSec = 0).sanitized().keyframeSec)
        assertEquals("an odd rate goes to the even step below, never under 4", listOf(6, 600_000), REauSettings(fpsCeiling = 7).sanitized().let { listOf(it.fpsCeiling, it.streamBitrateBps) })
        assertEquals(listOf(4, 400_000), REauSettings(fpsCeiling = 1).sanitized().let { listOf(it.fpsCeiling, it.streamBitrateBps) })
    }

    @Test
    fun `profile 2 is kept even, from 2 up to profile 1`() {
        assertEquals(2, REauSettings().reducedFps)
        assertEquals("never above profile 1", 6, REauSettings(fpsCeiling = 6, reducedFps = 10).sanitized().reducedFps)
        assertEquals("never under 2", 2, REauSettings(reducedFps = 0).sanitized().reducedFps)
        assertEquals("even steps from 2", 4, REauSettings(fpsCeiling = 8, reducedFps = 5).sanitized().reducedFps)
        assertEquals("lowering profile 1 pulls profile 2 with it", 4, REauSettings(fpsCeiling = 4, reducedFps = 8).sanitized().reducedFps)
    }

    @Test
    fun `a rate stored by this version is read back, within what is offered`() {
        val prefs = KeystoreBackedPrefsTest.FakePrefs()
        prefs.edit().putBoolean("conservative_video_20261010", true).putInt("fps_ceiling", 12).putInt("stream_bitrate", 1_024_000)
            .putInt("reduced_fps", 3).putString("bitrate_mode", "VBR").putInt("keyframe_sec", 2).putInt("density", 200).apply()
        val s = SettingsStore(prefs).load()
        assertEquals(listOf(10, 1_000_000, 1), listOf(s.fpsCeiling, s.streamBitrateBps, s.keyframeSec))
        assertEquals(2, s.reducedFps)
        assertEquals(BitrateMode.CBR, s.bitrateMode)
        assertEquals("the rest stays", 200, s.density)
    }

    @Test
    fun `a phone saved by an older version gets the newer protocol on, and keeps the rest`() {
        val prefs = KeystoreBackedPrefsTest.FakePrefs()
        prefs.edit().putInt("fps_ceiling", 4).putBoolean("aa_slow_pace", true).putInt("aa_slow_pace_fps", 18)
            .putBoolean("aa_new_protocol", false).putInt("density", 200).putBoolean("gemini", false).apply()
        val s = SettingsStore(prefs).load()
        assertEquals(4, s.fpsCeiling)
        assertEquals("protocol 1.7, always", true, s.aaNewProtocol)
        assertEquals("the rest stays", 200 to false, s.density to s.gemini)
    }

    @Test
    fun `saving and loading keeps the rates and the fixed mode`() {
        val prefs = KeystoreBackedPrefsTest.FakePrefs()
        SettingsStore(prefs).save(REauSettings(fpsCeiling = 8, reducedFps = 4, bitrateMode = BitrateMode.VBR))
        val back = SettingsStore(prefs).load()
        assertEquals(listOf(8, 800_000, 1), listOf(back.fpsCeiling, back.streamBitrateBps, back.keyframeSec))
        assertEquals(4, back.reducedFps)
        assertEquals(BitrateMode.CBR, back.bitrateMode)
        assertEquals("and again at the next start", back, SettingsStore(prefs).load())
    }

    @Test
    fun `when the two navigation profiles disagree the lower rate wins unless the rider chose the higher`() {
        assertEquals(com.reau.app.dash.NavProfileMode.PESSIMISTA, REauSettings().navProfileMode)
        val high = REauSettings(navProfileMode = com.reau.app.dash.NavProfileMode.OTIMISTA).sanitized()
        assertEquals(com.reau.app.dash.NavProfileMode.OTIMISTA, high.navProfileMode)
        val prefs = KeystoreBackedPrefsTest.FakePrefs()
        SettingsStore(prefs).save(high)
        assertEquals(com.reau.app.dash.NavProfileMode.OTIMISTA, SettingsStore(prefs).load().navProfileMode)
        val none = KeystoreBackedPrefsTest.FakePrefs()
        none.edit().putBoolean("conservative_video_20261010", true).apply()
        assertEquals(com.reau.app.dash.NavProfileMode.PESSIMISTA, SettingsStore(none).load().navProfileMode)
    }

    @Test
    fun `the profile by maneuver and the profile by speed are always on`() {
        val s = REauSettings()
        assertEquals(true to true, s.maneuverFpsProfile to s.speedFpsProfile)
        val off = REauSettings(maneuverFpsProfile = false, speedFpsProfile = false, maneuverData = false).sanitized()
        assertEquals(true to true, off.maneuverFpsProfile to off.speedFpsProfile)
        assertEquals("the data they live on is fixed on too", true, off.maneuverData)
        val prefs = KeystoreBackedPrefsTest.FakePrefs()
        prefs.edit().putBoolean("conservative_video_20261010", true).putBoolean("maneuver_fps_profile", false)
            .putBoolean("speed_fps_profile", false).apply()
        val back = SettingsStore(prefs).load()
        assertEquals(true to true, back.maneuverFpsProfile to back.speedFpsProfile)
    }
}
