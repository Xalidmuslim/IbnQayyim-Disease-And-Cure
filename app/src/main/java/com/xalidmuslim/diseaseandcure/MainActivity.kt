package com.xalidmuslim.diseaseandcure

import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient

/**
 * Minimal Android shell for the existing v44 reading engine.
 * The book, design, quiz, progress and bottom navigation are the original HTML.
 * This is a packaging bridge, not a claim of native Compose migration.
 */
class MainActivity : Activity() {
    private lateinit var reader: WebView
    private val homeUrl = "file:///android_asset/index.html"

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = Color.rgb(238, 240, 237)
        window.navigationBarColor = Color.rgb(238, 240, 237)
        @Suppress("DEPRECATION")
        window.decorView.systemUiVisibility = android.view.View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR or
                android.view.View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR

        reader = WebView(this).apply {
            setBackgroundColor(Color.rgb(238, 240, 237))
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true
            settings.allowFileAccess = false // android_asset remains accessible
            settings.allowContentAccess = false
            settings.setSupportZoom(false)
            settings.builtInZoomControls = false
            settings.displayZoomControls = false
            settings.mediaPlaybackRequiresUserGesture = true
            @Suppress("DEPRECATION")
            settings.allowFileAccessFromFileURLs = false
            @Suppress("DEPRECATION")
            settings.allowUniversalAccessFromFileURLs = false
            webChromeClient = WebChromeClient()
            webViewClient = object : WebViewClient() {
                override fun shouldOverrideUrlLoading(
                    view: WebView,
                    request: WebResourceRequest
                ): Boolean {
                    val u = request.url
                    if (u.scheme == "file" && u.path?.startsWith("/android_asset/") == true) {
                        return false
                    }
                    if (u.scheme == "https" || u.scheme == "http") {
                        try {
                            startActivity(Intent(Intent.ACTION_VIEW, u))
                        } catch (_: Exception) {
                            // No external browser: stay in the offline reader.
                        }
                    }
                    return true
                }
            }
        }
        setContentView(reader)
        if (savedInstanceState == null || reader.restoreState(savedInstanceState) == null) {
            reader.loadUrl(homeUrl)
        }
    }

    @Deprecated("Android Back dispatches to the book's existing back() hierarchy")
    override fun onBackPressed() {
        // The v44 HTML defines back() and handles read/quiz/home transitions.
        reader.evaluateJavascript("if (typeof back === 'function') { back(); }", null)
    }

    override fun onSaveInstanceState(outState: Bundle) {
        reader.saveState(outState)
        super.onSaveInstanceState(outState)
    }

    override fun onDestroy() {
        reader.stopLoading()
        reader.destroy()
        super.onDestroy()
    }
}
