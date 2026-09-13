package com.zakri.ghostlock

import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.app.KeyguardManager
import android.content.Context
import android.content.Intent
import android.media.RingtoneManager
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.VibrationEffect
import android.os.Vibrator
import android.view.WindowManager
import android.view.animation.OvershootInterpolator
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import org.eclipse.paho.client.mqttv3.MqttClient
import org.eclipse.paho.client.mqttv3.MqttConnectOptions
import org.eclipse.paho.client.mqttv3.MqttMessage
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class GhostAlertActivity : AppCompatActivity() {

    private val mainHandler = Handler(Looper.getMainLooper())
    private val autoDismissRunnable = Runnable { if (!isFinishing) finish() }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Réveille l'écran et passe au-dessus du verrouillage (Heads-Up HUD)
        wakeScreenAndBypassKeyguard()

        setContentView(R.layout.activity_ghost_alert)

        val title = intent?.getStringExtra("alert_title") ?: "Message du PC 💻"
        val message = intent?.getStringExtra("alert_message") ?: "Alerte reçue depuis le PC"

        val tvTitle = findViewById<TextView>(R.id.tvAlertTitle)
        val tvMessage = findViewById<TextView>(R.id.tvAlertMessage)
        val tvTime = findViewById<TextView>(R.id.tvAlertTime)
        val card = findViewById<android.view.View>(R.id.alertCard)
        val root = findViewById<android.view.View>(R.id.alertRoot)

        val timeFormat = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
        tvTitle.text = title
        tvMessage.text = message
        tvTime.text = "Reçu à ${timeFormat.format(Date())}"

        // Déclenche un retour haptique puissant et une alerte sonore
        triggerAlertFeedback()

        // Animation d'apparition visionOS / HUD futuriste
        card.scaleX = 0.75f
        card.scaleY = 0.75f
        card.alpha = 0f

        val scaleX = ObjectAnimator.ofFloat(card, "scaleX", 0.75f, 1.0f)
        val scaleY = ObjectAnimator.ofFloat(card, "scaleY", 0.75f, 1.0f)
        val alpha = ObjectAnimator.ofFloat(card, "alpha", 0f, 1.0f)

        AnimatorSet().apply {
            playTogether(scaleX, scaleY, alpha)
            duration = 380
            interpolator = OvershootInterpolator(1.3f)
            start()
        }

        // Actions
        findViewById<Button>(R.id.btnAlertViewer).setOnClickListener {
            val intent = Intent(this, ViewerActivity::class.java)
            startActivity(intent)
            finish()
        }

        findViewById<Button>(R.id.btnAlertLockPc).setOnClickListener {
            sendLockCommandToPc()
            finish()
        }

        findViewById<Button>(R.id.btnAlertDismiss).setOnClickListener {
            finish()
        }

        root.setOnClickListener {
            finish()
        }

        card.setOnClickListener {
            // Empêche la fermeture lors du clic sur la carte
        }

        // Auto-fermeture après 30 secondes
        mainHandler.postDelayed(autoDismissRunnable, 30000)
    }

    private fun wakeScreenAndBypassKeyguard() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O_MR1) {
            setShowWhenLocked(true)
            setTurnScreenOn(true)
            val km = getSystemService(Context.KEYGUARD_SERVICE) as? KeyguardManager
            km?.requestDismissKeyguard(this, null)
        } else {
            @Suppress("DEPRECATION")
            window.addFlags(
                WindowManager.LayoutParams.FLAG_SHOW_WHEN_LOCKED or
                WindowManager.LayoutParams.FLAG_DISMISS_KEYGUARD or
                WindowManager.LayoutParams.FLAG_TURN_SCREEN_ON or
                WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON
            )
        }
    }

    private fun triggerAlertFeedback() {
        try {
            val vibrator = getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                // Triple vibration intense futuriste
                vibrator?.vibrate(VibrationEffect.createWaveform(longArrayOf(0, 300, 100, 300, 100, 500), -1))
            } else {
                @Suppress("DEPRECATION")
                vibrator?.vibrate(400)
            }
        } catch (e: Exception) {}

        try {
            val notificationUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
            val r = RingtoneManager.getRingtone(applicationContext, notificationUri)
            r.play()
        } catch (e: Exception) {}
    }

    private fun sendLockCommandToPc() {
        Thread {
            try {
                val brokerUri = "tcp://broker.hivemq.com:1883"
                val clientId = "RedmiA3_AlertLock_${System.currentTimeMillis()}"
                val client = MqttClient(brokerUri, clientId, MemoryPersistence())
                val opts = MqttConnectOptions().apply {
                    isCleanSession = true
                    connectionTimeout = 5
                }
                client.connect(opts)
                val json = JSONObject().apply {
                    put("action", "lock")
                    put("device", "redmi_a3")
                    put("timestamp", System.currentTimeMillis())
                }
                client.publish("ghost_lock/pc-zakriev/cmd", MqttMessage(json.toString().toByteArray()).apply { qos = 1 })
                client.disconnect()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
    }

    override fun onDestroy() {
        mainHandler.removeCallbacks(autoDismissRunnable)
        super.onDestroy()
    }
}
