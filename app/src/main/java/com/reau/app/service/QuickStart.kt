package com.reau.app.service

import android.app.PendingIntent
import android.content.Intent
import android.graphics.drawable.Icon
import android.os.Build
import android.service.quicksettings.Tile
import android.service.quicksettings.TileService
import com.reau.app.MainActivity
import com.reau.app.R

/** The way in from the launcher's shortcut and the quick settings tile: REau opens and, if it is off, switches the projection on. */
object QuickStart {
    const val ACTION = "com.reau.app.QUICK_START"

    /** Whether an intent with [action] is a quick start, and whether the projection in [phase] should be switched on by it (only a stopped one). */
    fun switchesOn(action: String?, phase: Phase): Boolean = action == ACTION && phase == Phase.STOPPED

    fun intent(context: android.content.Context): Intent =
        Intent(context, MainActivity::class.java).setAction(ACTION).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP)
}

/**
 * The quick settings tile "REau": one touch from the notification shade opens REau and switches the projection on, so the
 * rider can do it at home, before the helmet. Opening an activity from a tile is how Android lets it ask for permissions and
 * show the Android Auto warning; the tile itself starts nothing in the background.
 */
class QuickStartTile : TileService() {
    override fun onStartListening() {
        qsTile?.apply {
            state = if (ProjectionService.projection.value.phase == Phase.STOPPED) Tile.STATE_INACTIVE else Tile.STATE_ACTIVE
            label = getString(R.string.quick_start_label)
            icon = Icon.createWithResource(this@QuickStartTile, R.drawable.ic_stat_reau)
            updateTile()
        }
    }

    @Suppress("StartActivityAndCollapseDeprecated") // the Intent form is the only one before Android 14
    override fun onClick() {
        val intent = QuickStart.intent(this)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            startActivityAndCollapse(PendingIntent.getActivity(this, 0, intent, PendingIntent.FLAG_IMMUTABLE))
        } else {
            @Suppress("DEPRECATION")
            startActivityAndCollapse(intent)
        }
    }
}
