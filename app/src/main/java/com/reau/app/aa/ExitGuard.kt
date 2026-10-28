package com.reau.app.aa

/**
 * Keeps the joystick from leaving Android Auto by accident. In Android Auto's app menu the first focus is "Exit": a select
 * (Enter) there makes the phone ask for the native screen, which ends the session, and with the dash's joystick a select is
 * one tap away from it. A request to leave that comes within [WINDOW_MS] of a select sent by the joystick is taken as
 * that slip and refused; one the rider made on the phone's own screen comes with no select before it and is honoured.
 */
class ExitGuard(private val windowMs: Long = WINDOW_MS) {
    @Volatile private var lastSelectMs: Long? = null

    /** The joystick's select went to Android Auto at [nowMs]. */
    fun selectSent(nowMs: Long) {
        lastSelectMs = nowMs
    }

    /** Whether a request to leave at [nowMs] follows a select of the joystick closely enough to be its slip. */
    fun isSlip(nowMs: Long): Boolean {
        val last = lastSelectMs ?: return false
        return nowMs - last in 0..windowMs
    }

    companion object {
        const val WINDOW_MS = 2_000L
    }
}
