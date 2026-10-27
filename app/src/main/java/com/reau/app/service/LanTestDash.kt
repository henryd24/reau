package com.reau.app.service

import android.content.Context
import android.net.Network
import com.reau.app.BuildConfig
import com.reau.app.dash.DashSocket
import java.io.File
import java.net.InetAddress
import java.net.InetSocketAddress

/**
 * A test dash on the local network, for a developer without the bike at hand (tools/fake_dash on a computer).
 *
 * Debug builds only, and only while the file [FILE] holds an IPv4 address, in the app's own external folder (what
 * `adb push` reaches, nothing the rider's screens write): the session then talks to that address instead of the
 * bike's 192.168.1.x, and does not join the bike's Wi-Fi. A release build never reads the file.
 */
object LanTestDash {
    const val FILE = "lan_dash_host.txt"

    private val IPV4 = Regex("""(25[0-5]|2[0-4]\d|1?\d?\d)(\.(25[0-5]|2[0-4]\d|1?\d?\d)){3}""")

    /** The address in [text]'s first line, or null when it is not a plain IPv4 one. */
    fun parse(text: String?): String? = text?.lineSequence()?.firstOrNull()?.trim()?.takeIf { IPV4.matches(it) }

    /** The test dash's address on this phone, null in a release build or with no file. */
    fun host(context: Context): String? {
        if (!BuildConfig.DEBUG) return null
        val file = File(context.getExternalFilesDir(null) ?: return null, FILE)
        return parse(runCatching { file.takeIf { it.isFile }?.readText() }.getOrNull())
    }

    fun socket(host: String): (Network?) -> DashSocket = {
        DashSocket(
            null,
            InetSocketAddress(InetAddress.getByName(host), DashSocket.CTRL_PORT),
            InetSocketAddress(InetAddress.getByName(host), DashSocket.RTP_PORT),
        )
    }
}

/** The link up for [LanTestDash]: there is nothing to join, the test dash is reachable already. */
internal class LanDashLinkUp : DashLinkUp {
    override fun start(onReady: (ssid: String, network: Network?) -> Unit, onFailed: (String) -> Unit) {
        onReady(SSID, null)
    }

    override fun stop() = Unit

    companion object {
        const val SSID = "RE_FAKE_LAN"
    }
}
