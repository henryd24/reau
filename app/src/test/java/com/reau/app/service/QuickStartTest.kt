package com.reau.app.service

import org.junit.Assert.assertEquals
import org.junit.Test

/** The launcher shortcut and the quick settings tile: they switch a stopped projection on, and nothing else. */
class QuickStartTest {
    @Test
    fun `only the quick start action on a stopped projection switches it on`() {
        assertEquals(true, QuickStart.switchesOn(QuickStart.ACTION, Phase.STOPPED))
        Phase.entries.filter { it != Phase.STOPPED }.forEach { assertEquals(false, QuickStart.switchesOn(QuickStart.ACTION, it)) }
        assertEquals(false, QuickStart.switchesOn("android.intent.action.MAIN", Phase.STOPPED))
        assertEquals(false, QuickStart.switchesOn(null, Phase.STOPPED))
    }
}
