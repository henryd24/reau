package com.reau.app.aa

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ExitGuardTest {
    @Test
    fun `a request to leave with no select before it is the rider's own`() {
        assertFalse(ExitGuard().isSlip(10_000))
    }

    @Test
    fun `a request to leave right after the joystick's select is a slip onto Exit`() {
        val guard = ExitGuard()
        guard.selectSent(10_000)
        assertTrue(guard.isSlip(10_050))
        assertTrue(guard.isSlip(10_000 + ExitGuard.WINDOW_MS))
    }

    @Test
    fun `a request to leave long after the select is the rider's own`() {
        val guard = ExitGuard()
        guard.selectSent(10_000)
        assertFalse(guard.isSlip(10_000 + ExitGuard.WINDOW_MS + 1))
    }

    @Test
    fun `a later select moves the window along`() {
        val guard = ExitGuard()
        guard.selectSent(10_000)
        guard.selectSent(20_000)
        assertTrue(guard.isSlip(20_500))
    }
}
