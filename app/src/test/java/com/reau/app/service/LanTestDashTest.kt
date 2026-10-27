package com.reau.app.service

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class LanTestDashTest {
    @Test
    fun `a plain address is read, its first line only`() {
        assertEquals("192.168.0.20", LanTestDash.parse("192.168.0.20\n"))
        assertEquals("10.0.0.5", LanTestDash.parse("  10.0.0.5 \nignored"))
    }

    @Test
    fun `anything else is no address`() {
        assertNull(LanTestDash.parse(null))
        assertNull(LanTestDash.parse(""))
        assertNull(LanTestDash.parse("example.com"))
        assertNull(LanTestDash.parse("192.168.0.256"))
        assertNull(LanTestDash.parse("192.168.0"))
        assertNull(LanTestDash.parse("192.168.0.1:2000"))
    }
}
