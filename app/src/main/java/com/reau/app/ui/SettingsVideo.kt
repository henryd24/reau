package com.reau.app.ui

import androidx.compose.runtime.Composable
import androidx.compose.ui.res.stringResource
import com.reau.app.R
import com.reau.app.dash.DashConfig
import com.reau.app.dash.NavProfileMode
import com.reau.app.settings.REauSettings
import com.reau.app.ui.components.Info
import com.reau.app.ui.components.LockedRow
import com.reau.app.ui.components.SegmentedRow
import com.reau.app.ui.components.StepperRow

// The stream's bitrate mode and keyframe are fixed, and so is the bitrate's rule (100 kbps for each frame a second). The two
// profiles' rates are the experiment: the proven 4 and 2 fps by default, to be raised and tried on the bike.

/**
 * The stream's rows: the rate of each of the two profiles (experimental, taken on the next start), and what follows from them
 * (the bitrate) or never changes (mode, keyframe). The navigation profiles below choose between the two.
 */
@Composable
internal fun StreamProfileRows(s: REauSettings, change: (REauSettings) -> Unit) {
    val step = DashConfig.STREAM_FPS_STEP
    val reducedKbps = s.reducedFps * DashConfig.BPS_PER_FPS / 1000
    StepperRow(
        stringResource(R.string.fps_title), "${s.fpsCeiling} fps",
        { change(s.copy(fpsCeiling = s.fpsCeiling - step)) }, { change(s.copy(fpsCeiling = s.fpsCeiling + step)) }, "fps_full",
        sub = stringResource(R.string.profiles_fps_sub),
        info = Info(
            stringResource(R.string.fps_title),
            stringResource(R.string.profiles_info, s.fpsCeiling, s.streamBitrateBps / 1000, s.reducedFps, reducedKbps),
        ),
    )
    StepperRow(
        stringResource(R.string.fps_reduced_title), "${s.reducedFps} fps",
        { change(s.copy(reducedFps = s.reducedFps - step)) }, { change(s.copy(reducedFps = s.reducedFps + step)) }, "fps_reduced",
        sub = stringResource(R.string.fps_reduced_sub),
    )
    LockedRow(
        stringResource(R.string.bitrate_title), stringResource(R.string.bitrate_value, s.streamBitrateBps / 1000), "bitrate",
        sub = stringResource(R.string.profiles_bitrate_sub, reducedKbps),
    )
    LockedRow(stringResource(R.string.bitrate_mode_title), stringResource(R.string.bitrate_cbr), "bitrate_mode")
    LockedRow(stringResource(R.string.keyframe_title), "${s.keyframeSec} s", "keyframe")
}

/**
 * The profile by maneuver and the profile by speed are always on; what the rider picks is which one wins when they disagree
 * (applies at once): the lower rate (profile B, the default) or the higher one.
 */
@Composable
internal fun NavProfileRows(s: REauSettings, change: (REauSettings) -> Unit) {
    val on = stringResource(R.string.profiles_on)
    LockedRow(
        stringResource(R.string.maneuver_fps_title), on, "maneuver_fps_profile",
        info = Info(stringResource(R.string.maneuver_fps_title), stringResource(R.string.maneuver_profile_info)),
    )
    LockedRow(
        stringResource(R.string.speed_fps_title), on, "speed_fps_profile",
        info = Info(stringResource(R.string.speed_fps_title), stringResource(R.string.speed_profile_info)),
    )
    val modes = listOf(NavProfileMode.PESSIMISTA, NavProfileMode.OTIMISTA)
    SegmentedRow(
        stringResource(R.string.profile_policy_title),
        listOf(
            stringResource(R.string.profile_policy_low) to "profile_policy_low",
            stringResource(R.string.profile_policy_high) to "profile_policy_high",
        ),
        modes.indexOf(s.navProfileMode), { change(s.copy(navProfileMode = modes[it])) },
        now = true, info = Info(stringResource(R.string.profile_policy_title), stringResource(R.string.profile_policy_info)),
        tag = "profile_policy",
    )
}
