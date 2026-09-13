package com.zakri.ghostlock

import android.annotation.SuppressLint
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.View
import android.view.WindowManager
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
import org.eclipse.paho.client.mqttv3.MqttClient
import org.eclipse.paho.client.mqttv3.MqttConnectOptions
import org.eclipse.paho.client.mqttv3.MqttMessage
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence
import org.json.JSONObject

class ViewerActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private var mqttClient: MqttClient? = null
    private val mainHandler = Handler(Looper.getMainLooper())
    private var targetPc = "pc-zakriev"
    private var topicCmd = "ghost_lock/$targetPc/cmd"
    private var isHeartbeatActive = false

    private val heartbeatRunnable = object : Runnable {
        override fun run() {
            if (isHeartbeatActive) {
                sendMqttCommand("viewer_heartbeat")
                mainHandler.postDelayed(this, 5000)
            }
        }
    }


    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        targetPc = GhostPrefs.getSelectedPc(this)
        topicCmd = "ghost_lock/$targetPc/cmd"

        // Plein écran et garder l'écran allumé pendant le visionnage
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)

        webView = WebView(this).apply {
            settings.apply {
                javaScriptEnabled = true
                domStorageEnabled = true
                databaseEnabled = true
                allowFileAccess = true
                allowContentAccess = true
                loadWithOverviewMode = true
                useWideViewPort = true
                setSupportZoom(true)
                builtInZoomControls = true
                displayZoomControls = false
                mediaPlaybackRequiresUserGesture = false
                cacheMode = WebSettings.LOAD_DEFAULT
            }
            webViewClient = WebViewClient()
            webChromeClient = WebChromeClient()
            setLayerType(View.LAYER_TYPE_HARDWARE, null)
        }

        setContentView(webView)
        webView.loadUrl("file:///android_asset/ghost_web_viewer.html")
    }

    override fun onResume() {
        super.onResume()
        isHeartbeatActive = true
        sendMqttCommand("viewer_resumed")
        mainHandler.postDelayed(heartbeatRunnable, 5000)
    }


    override fun onPause() {
        super.onPause()
        isHeartbeatActive = false
        mainHandler.removeCallbacks(heartbeatRunnable)
        sendMqttCommand("viewer_left")
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }

    override fun onDestroy() {
        isHeartbeatActive = false
        mainHandler.removeCallbacks(heartbeatRunnable)
        sendMqttCommand("viewer_closed")
        webView.destroy()
        try {
            mqttClient?.disconnect()
        } catch (e: Exception) {}
        super.onDestroy()
    }

    private fun sendMqttCommand(action: String) {
        Thread {
            try {
                if (mqttClient == null || !mqttClient!!.isConnected) {
                    val clientId = "ViewerActivity_${System.currentTimeMillis()}"
                    mqttClient = MqttClient("tcp://broker.hivemq.com:1883", clientId, MemoryPersistence())
                    val options = MqttConnectOptions().apply {
                        isCleanSession = true
                        connectionTimeout = 5
                        keepAliveInterval = 30
                    }
                    mqttClient?.connect(options)
                }
                val json = JSONObject().apply {
                    put("action", action)
                    put("device", "redmi_a3")
                    put("timestamp", System.currentTimeMillis())
                }
                val msg = MqttMessage(json.toString().toByteArray()).apply { qos = 1 }
                mqttClient?.publish(topicCmd, msg)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
    }
}
