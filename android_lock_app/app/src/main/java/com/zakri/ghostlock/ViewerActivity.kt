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

import android.view.ViewGroup
import java.util.concurrent.Executors

class ViewerActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private var mqttClient: MqttClient? = null
    private val mainHandler = Handler(Looper.getMainLooper())
    private val mqttExecutor = Executors.newSingleThreadExecutor()
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
        if (::webView.isInitialized && webView.canGoBack()) {
            webView.goBack()
        } else {
            finish()
        }
    }

    override fun onDestroy() {
        isHeartbeatActive = false
        mainHandler.removeCallbacksAndMessages(null)
        sendMqttCommand("viewer_closed")
        
        // 1. Démonter proprement la WebView pour éviter tout deadlock / freeze Chromium
        try {
            (webView.parent as? ViewGroup)?.removeView(webView)
            webView.stopLoading()
            webView.loadUrl("about:blank")
            webView.clearHistory()
            webView.removeAllViews()
            webView.destroy()
        } catch (e: Exception) {
            e.printStackTrace()
        }

        // 2. Déconnexion MQTT 100% asynchrone hors du thread UI
        val clientToClose = mqttClient
        mqttClient = null
        mqttExecutor.execute {
            try {
                if (clientToClose != null && clientToClose.isConnected) {
                    clientToClose.disconnectForcibly(500)
                }
                clientToClose?.close()
            } catch (e: Exception) {}
        }

        super.onDestroy()
    }

    private fun sendMqttCommand(action: String) {
        mqttExecutor.execute {
            try {
                if (mqttClient == null || mqttClient?.isConnected != true) {
                    val clientId = "ViewerActivity_${System.currentTimeMillis()}"
                    mqttClient = MqttClient("tcp://broker.hivemq.com:1883", clientId, MemoryPersistence())
                    val options = MqttConnectOptions().apply {
                        isCleanSession = true
                        connectionTimeout = 5
                        keepAliveInterval = 15
                        isAutomaticReconnect = true
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
                // Ignore silent network failure in executor
            }
        }
    }
}
