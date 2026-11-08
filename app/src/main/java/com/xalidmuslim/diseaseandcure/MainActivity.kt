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
import android.window.OnBackInvokedCallback
import android.window.OnBackInvokedDispatcher

/**
 * Minimal Android shell for the existing v44 reading engine.
 * The book, design, quiz, progress and bottom navigation are the original HTML.
 * This is a packaging bridge, not a claim of native Compose migration.
 */
class MainActivity : Activity() {
    private lateinit var reader: WebView
    private val homeUrl = "file:///android_asset/index.html"
    private var modernBackCallback: OnBackInvokedCallback? = null

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
            // Fixed CSS pixel proportions, independent of Android system font scale.
            settings.textZoom = 100
            // Respect the existing HTML width=device-width without overview shrinkage.
            settings.useWideViewPort = true
            settings.loadWithOverviewMode = false
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
                override fun onPageFinished(view: WebView, url: String?) {
                    super.onPageFinished(view, url)
                    if (url != homeUrl) return
                    // Keep the 114 chapters and the entire v44 HTML byte-for-byte.
                    // Only chapter-card title typography is adjusted by a CSS asset.
                    view.evaluateJavascript("""
                        (function () {
                          if (document.getElementById('compact-chapter-headings-v46')) return;
                          const link = document.createElement('link');
                          link.id = 'compact-chapter-headings-v46';
                          link.rel = 'stylesheet';
                          link.href = 'compact_sections.css';
                          document.head.appendChild(link);
                        })();
                    """.trimIndent(), null)
                    // Inject a narrow DOM-text correction, leaving the protected book HTML unchanged.
                    view.evaluateJavascript("""
                        (function () {
                          if (document.getElementById('footer-notice-fix-v50')) return;
                          const script = document.createElement('script');
                          script.id = 'footer-notice-fix-v50';
                          script.src = 'footer_notice_fix.js';
                          document.head.appendChild(script);
                        })();
                    """.trimIndent(), null)
                }

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
        // Android 13+ dispatches the gesture using the new system Back API.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            val callback = OnBackInvokedCallback { navigateBackInReader() }
            modernBackCallback = callback
            onBackInvokedDispatcher.registerOnBackInvokedCallback(
                OnBackInvokedDispatcher.PRIORITY_DEFAULT, callback
            )
        }
        if (savedInstanceState == null || reader.restoreState(savedInstanceState) == null) {
            reader.loadUrl(homeUrl)
        }
    }

    private fun navigateBackInReader() {
        if (!::reader.isInitialized) return
        // The book has a navigation state machine, not WebView browser history.
        reader.evaluateJavascript(
            "if (typeof window.__androidBack === 'function') { window.__androidBack(); } " +
                "else if (typeof back === 'function') { back(); }",
            null
        )
    }

    @Deprecated("Used only by pre-Android 13 system Back dispatch")
    override fun onBackPressed() {
        navigateBackInReader()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        reader.saveState(outState)
        super.onSaveInstanceState(outState)
    }

    override fun onDestroy() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            modernBackCallback?.let { onBackInvokedDispatcher.unregisterOnBackInvokedCallback(it) }
            modernBackCallback = null
        }
        reader.stopLoading()
        reader.destroy()
        super.onDestroy()
    }
}
