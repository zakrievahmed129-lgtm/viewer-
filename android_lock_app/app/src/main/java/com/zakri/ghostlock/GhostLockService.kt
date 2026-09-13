package com.zakri.ghostlock

import android.annotation.SuppressLint
import android.app.AlarmManager
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.bluetooth.le.AdvertiseCallback
import android.bluetooth.le.AdvertiseData
import android.bluetooth.le.AdvertiseSettings
import android.bluetooth.le.BluetoothLeAdvertiser
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.ServiceInfo
import android.graphics.Color
import android.net.ConnectivityManager
import android.net.Network
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.ParcelUuid
import android.os.PowerManager
import android.os.SystemClock
import android.os.VibrationEffect
import android.os.Vibrator
import android.widget.RemoteViews
import android.widget.Toast
import androidx.core.app.NotificationCompat
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken
import org.eclipse.paho.client.mqttv3.MqttCallback
import org.eclipse.paho.client.mqttv3.MqttClient
import org.eclipse.paho.client.mqttv3.MqttConnectOptions
import org.eclipse.paho.client.mqttv3.MqttMessage
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.UUID

class GhostLockService : Service() {

    companion object {
        const val CHANNEL_ID = "ghost_lock_service_24_7"
        const val ALERTS_CHANNEL_ID = "ghost_alerts_channel"
        const val NOTIF_ID = 1001
        var isServiceRunning = false
        var instance: GhostLockService? = null
    }

    private var wakeLock: PowerManager.WakeLock? = null
    private var bluetoothAdapter: BluetoothAdapter? = null
    private var advertiser: BluetoothLeAdvertiser? = null
    private val serviceUuid = UUID.fromString("0000ffe0-0000-1000-8000-00805f9b34fb")
    private var isAdvertising = false
    private var isProximityEnabled = true

    private var mqttClient: MqttClient? = null
    private val mainHandler = Handler(Looper.getMainLooper())
    private var networkCallback: ConnectivityManager.NetworkCallback? = null
    private val reconnectRunnable = Runnable { connectMqtt() }
    private var isConnectingMqtt = false
    private var targetPc = "pc-zakriev"
    private val brokerUri = "tcp://broker.hivemq.com:1883"
    private var topicStatus = "ghost_lock/$targetPc/status"
    private var topicCmd = "ghost_lock/$targetPc/cmd"
    private var topicHeartbeat = "ghost_lock/$targetPc/heartbeat"
    private var topicStreamCmd = "ghost_lock/$targetPc/phone_stream/cmd"

    private var isPcLocked = false

    private val bluetoothReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent?.action == BluetoothAdapter.ACTION_STATE_CHANGED) {
                val state = intent.getIntExtra(BluetoothAdapter.EXTRA_STATE, BluetoothAdapter.ERROR)
                if (state == BluetoothAdapter.STATE_ON) {
                    startBleBeacon()
                } else if (state == BluetoothAdapter.STATE_OFF || state == BluetoothAdapter.STATE_TURNING_OFF) {
                    isAdvertising = false
                }
            }
        }
    }

    private val heartbeatRunnable = object : Runnable {
        override fun run() {
            if (isProximityEnabled && mqttClient?.isConnected == true) {
                Thread {
                    try {
                        val json = JSONObject().apply {
                            put("action", "heartbeat")
                            put("device", "redmi_a3")
                            put("service", true)
                            put("timestamp", System.currentTimeMillis())
                        }
                        mqttClient?.publish(topicHeartbeat, MqttMessage(json.toString().toByteArray()).apply { qos = 0 })
                    } catch (e: Exception) {}
                }.start()
            }
            mainHandler.postDelayed(this, 4000)
        }
    }

    override fun onCreate() {
        super.onCreate()
        instance = this
        isServiceRunning = true

        targetPc = GhostPrefs.getSelectedPc(this)
        topicStatus = "ghost_lock/$targetPc/status"
        topicCmd = "ghost_lock/$targetPc/cmd"
        topicHeartbeat = "ghost_lock/$targetPc/heartbeat"
        topicStreamCmd = "ghost_lock/$targetPc/phone_stream/cmd"

        createNotificationChannel()
        val notification = buildNotification("Surveillance active 24/7", "Connecté à $targetPc")

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(NOTIF_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_CONNECTED_DEVICE)
        } else {
            startForeground(NOTIF_ID, notification)
        }

        acquireWakeLock()
        initBluetooth()
        connectMqtt()
        registerNetworkMonitor()
        mainHandler.post(heartbeatRunnable)

        val filter = IntentFilter(BluetoothAdapter.ACTION_STATE_CHANGED)
        registerReceiver(bluetoothReceiver, filter)
    }

    fun switchTargetPc(newPc: String) {
        val clean = newPc.trim().lowercase()
        if (clean.isEmpty() || clean == targetPc) return
        val oldPc = targetPc
        targetPc = clean
        topicStatus = "ghost_lock/$targetPc/status"
        topicCmd = "ghost_lock/$targetPc/cmd"
        topicHeartbeat = "ghost_lock/$targetPc/heartbeat"
        topicStreamCmd = "ghost_lock/$targetPc/phone_stream/cmd"

        updateNotification("Surveillance active 24/7", "Connecté à $targetPc")

        Thread {
            try {
                mqttClient?.let { client ->
                    if (client.isConnected) {
                        try {
                            client.unsubscribe("ghost_lock/$oldPc/status")
                            client.unsubscribe("ghost_lock/$oldPc/cmd")
                            client.unsubscribe("ghost_lock/$oldPc/phone_stream/cmd")
                        } catch (e: Exception) {}

                        client.subscribe(topicStatus, 1)
                        client.subscribe(topicCmd, 1)
                        client.subscribe(topicStreamCmd, 1)

                        val json = JSONObject().apply {
                            put("action", "heartbeat")
                            put("device", "redmi_a3")
                            put("service", true)
                            put("timestamp", System.currentTimeMillis())
                        }
                        client.publish(topicHeartbeat, MqttMessage(json.toString().toByteArray()).apply { qos = 0 })
                    }
                }
            } catch (e: Exception) {}
        }.start()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action
        if (action == "STOP") {
            stopSelf()
            return START_NOT_STICKY
        }

        if (action == "ACTION_CHANGE_TARGET_PC") {
            val newPc = intent.getStringExtra("target_pc") ?: GhostPrefs.getSelectedPc(this)
            switchTargetPc(newPc)
            return START_STICKY
        }

        // Vérification et relance du beacon si éteint
        if (isProximityEnabled && !isAdvertising) {
            startBleBeacon()
        }

        return START_STICKY
    }

    private fun acquireWakeLock() {
        try {
            val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
            wakeLock = powerManager.newWakeLock(
                PowerManager.PARTIAL_WAKE_LOCK,
                "GhostLock::ServiceWakeLock"
            ).apply {
                setReferenceCounted(false)
                acquire(24 * 60 * 60 * 1000L) // 24h renouvelable
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = getSystemService(NotificationManager::class.java)
            val channel = NotificationChannel(
                CHANNEL_ID,
                "GhostLock Vision Pro (Arrière-plan 24/7)",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Maintient la balise Bluetooth de distance et la surveillance active en continu"
                setShowBadge(false)
                lockscreenVisibility = Notification.VISIBILITY_PUBLIC
            }
            manager?.createNotificationChannel(channel)

            val alertsChannel = NotificationChannel(
                ALERTS_CHANNEL_ID,
                "Ghost Alerts (Messages du PC)",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Alertes instantanées et messages reçus depuis le PC"
                enableVibration(true)
                enableLights(true)
                setShowBadge(true)
            }
            manager?.createNotificationChannel(alertsChannel)
        }
    }

    private fun buildNotification(title: String, text: String): Notification {
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
            },
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val iconRes = if (isPcLocked) R.drawable.ic_padlock_locked else R.drawable.ic_padlock_unlocked

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(text)
            .setSmallIcon(iconRes)
            .setOngoing(true)
            .setContentIntent(pendingIntent)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .build()
    }

    private fun updateNotification(title: String, text: String) {
        val manager = getSystemService(NotificationManager::class.java)
        manager?.notify(NOTIF_ID, buildNotification(title, text))
    }

    private fun initBluetooth() {
        val bluetoothManager = getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
        bluetoothAdapter = bluetoothManager?.adapter
        startBleBeacon()
    }

    @SuppressLint("MissingPermission")
    fun startBleBeacon() {
        if (!isProximityEnabled) return
        try {
            if (bluetoothAdapter == null || !bluetoothAdapter!!.isEnabled) return

            advertiser = bluetoothAdapter?.bluetoothLeAdvertiser
            if (advertiser == null) return

            val settings = AdvertiseSettings.Builder()
                .setAdvertiseMode(AdvertiseSettings.ADVERTISE_MODE_LOW_LATENCY)
                .setTxPowerLevel(AdvertiseSettings.ADVERTISE_TX_POWER_MEDIUM)
                .setConnectable(false)
                .setTimeout(0)
                .build()

            val data = AdvertiseData.Builder()
                .setIncludeDeviceName(true)
                .addServiceUuid(ParcelUuid(serviceUuid))
                .build()

            advertiser?.startAdvertising(settings, data, advertiseCallback)
            isAdvertising = true
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    @SuppressLint("MissingPermission")
    fun stopBleBeacon() {
        try {
            if (isAdvertising) {
                advertiser?.stopAdvertising(advertiseCallback)
                isAdvertising = false
            }
        } catch (e: Exception) {}
    }

    fun setProximityEnabled(enabled: Boolean) {
        isProximityEnabled = enabled
        if (enabled) {
            startBleBeacon()
            updateNotification("🛡️ GhostLock — 24/7 Actif", "Balise Bluetooth de distance active")
        } else {
            stopBleBeacon()
            updateNotification("⏸️ GhostLock — En pause", "Proximité désactivée")
        }
    }

    private val advertiseCallback = object : AdvertiseCallback() {
        override fun onStartSuccess(settingsInEffect: AdvertiseSettings?) {
            super.onStartSuccess(settingsInEffect)
            isAdvertising = true
        }

        override fun onStartFailure(errorCode: Int) {
            super.onStartFailure(errorCode)
            isAdvertising = false
        }
    }

    private fun registerNetworkMonitor() {
        try {
            val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            networkCallback = object : ConnectivityManager.NetworkCallback() {
                override fun onAvailable(network: Network) {
                    scheduleMqttReconnect(200)
                }

                override fun onLost(network: Network) {}
            }
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                cm.registerDefaultNetworkCallback(networkCallback!!)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun scheduleMqttReconnect(delayMs: Long) {
        mainHandler.removeCallbacks(reconnectRunnable)
        mainHandler.postDelayed(reconnectRunnable, delayMs)
    }

    private fun connectMqtt() {
        mainHandler.removeCallbacks(reconnectRunnable)
        Thread {
            synchronized(this) {
                if (isConnectingMqtt) return@Thread
                isConnectingMqtt = true
            }
            try {
                // Fermeture propre préalable de toute socket résiduelle
                val staleClient = mqttClient
                mqttClient = null
                if (staleClient != null) {
                    try {
                        if (staleClient.isConnected) staleClient.disconnectForcibly(500)
                        staleClient.close()
                    } catch (e: Exception) {}
                }

                val clientId = "RedmiA3_Service_${System.currentTimeMillis()}"
                val client = MqttClient(brokerUri, clientId, MemoryPersistence())
                val options = MqttConnectOptions().apply {
                    isCleanSession = true
                    connectionTimeout = 8
                    keepAliveInterval = 15 // Maintien actif de la translation CGNAT en 4G mobile
                    isAutomaticReconnect = true
                    maxInflight = 50
                }

                client.setCallback(object : MqttCallback {
                    override fun connectionLost(cause: Throwable?) {
                        scheduleMqttReconnect(2500)
                    }

                    override fun messageArrived(topic: String?, message: MqttMessage?) {
                        try {
                            val payload = message?.toString() ?: return
                            val json = JSONObject(payload)

                            if (topic == topicStreamCmd) {
                                val action = json.optString("action")
                                if (action == "notification") {
                                    val title = json.optString("title", "Message du PC 💻")
                                    val messageText = json.optString("message", "")
                                    showCustomPhoneNotification(title, messageText)
                                }
                                return
                            }

                            val locked = json.optBoolean("locked", false)
                            val online = json.optBoolean("online", true)
                            val armed = json.optBoolean("armed", false)
                            isPcLocked = locked

                            if (online) {
                                if (locked) {
                                    updateNotification("🔒 PC Verrouillé (Sécurisé)", "GhostLock veille 24/7")
                                } else {
                                    val armText = if (armed) "Réarmé (Près du PC)" else "En attente"
                                    updateNotification("🔓 PC Déverrouillé", "Auto-lock : $armText")
                                }
                            } else {
                                updateNotification("🔴 PC Hors ligne", "En attente du bouclier")
                            }
                        } catch (e: Exception) {}
                    }

                    override fun deliveryComplete(token: IMqttDeliveryToken?) {}
                })

                client.connect(options)
                client.subscribe(topicStatus, 1)
                client.subscribe(topicStreamCmd, 1)

                mqttClient = client
            } catch (e: Exception) {
                scheduleMqttReconnect(3500)
            } finally {
                synchronized(this) {
                    isConnectingMqtt = false
                }
            }
        }.start()
    }

    fun showCustomPhoneNotification(title: String, message: String) {
        try {
            val validTitle = if (title.isNotBlank()) title else "Message du PC 💻"
            val validMessage = if (message.isNotBlank()) message else "Transmission reçue en direct du PC."

            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            val timeStr = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())

            // 1. Déclenche immédiatement l'écran d'alerte HUD plein écran (visionOS Floating Card)
            try {
                val alertIntent = Intent(this, GhostAlertActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
                    putExtra("alert_title", validTitle)
                    putExtra("alert_message", validMessage)
                }
                startActivity(alertIntent)
            } catch (e: Exception) {
                e.printStackTrace()
            }

            // 2. Vibreur puissant triple impulsion pour alerte
            try {
                val vibrator = getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    vibrator?.vibrate(VibrationEffect.createWaveform(longArrayOf(0, 300, 100, 300, 100, 500), -1))
                } else {
                    @Suppress("DEPRECATION")
                    vibrator?.vibrate(400)
                }
            } catch (e: Exception) {}

            // Toast immédiat à l'écran
            mainHandler.post {
                Toast.makeText(applicationContext, "📢 $validTitle : $validMessage", Toast.LENGTH_LONG).show()
            }

            // 3. PendingIntents interactifs pour la notification
            val fullScreenIntent = PendingIntent.getActivity(
                this,
                (System.currentTimeMillis() % 10000).toInt(),
                Intent(this, GhostAlertActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                    putExtra("alert_title", validTitle)
                    putExtra("alert_message", validMessage)
                },
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )

            val viewerIntent = PendingIntent.getActivity(
                this,
                (System.currentTimeMillis() % 10000).toInt() + 1,
                Intent(this, ViewerActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                },
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )

            // 4. RemoteViews stylé Vision Pro futuriste
            val smallView = RemoteViews(packageName, R.layout.custom_notification_alert_small).apply {
                setTextViewText(R.id.notif_title_small, validTitle)
                setTextViewText(R.id.notif_message_small, validMessage)
                setTextViewText(R.id.notif_time_small, timeStr)
            }

            val bigView = RemoteViews(packageName, R.layout.custom_notification_alert).apply {
                setTextViewText(R.id.notif_title, validTitle)
                setTextViewText(R.id.notif_message, validMessage)
                setTextViewText(R.id.notif_time, timeStr)
                setOnClickPendingIntent(R.id.btn_notif_viewer, viewerIntent)
                setOnClickPendingIntent(R.id.btn_notif_lock, fullScreenIntent)
            }

            val notifId = (System.currentTimeMillis() % 100000).toInt() + 2000
            val notif = NotificationCompat.Builder(this, ALERTS_CHANNEL_ID)
                .setSmallIcon(R.drawable.ic_padlock_unlocked)
                .setContentTitle(validTitle)
                .setContentText(validMessage)
                .setCustomContentView(smallView)
                .setCustomBigContentView(bigView)
                .setCustomHeadsUpContentView(bigView)
                .setStyle(NotificationCompat.DecoratedCustomViewStyle())
                .setPriority(NotificationCompat.PRIORITY_MAX)
                .setCategory(NotificationCompat.CATEGORY_ALARM)
                .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
                .setFullScreenIntent(fullScreenIntent, true)
                .setDefaults(Notification.DEFAULT_ALL)
                .setAutoCancel(true)
                .setColor(Color.parseColor("#00F0FF"))
                .setColorized(true)
                .setContentIntent(fullScreenIntent)
                .build()

            notificationManager.notify(notifId, notif)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    override fun onTaskRemoved(rootIntent: Intent?) {
        // Redémarrage automatique garanti si l'application est glissée hors du multitâche
        val restartServiceIntent = Intent(applicationContext, GhostLockService::class.java).apply {
            setPackage(packageName)
        }
        val restartServicePendingIntent = PendingIntent.getService(
            applicationContext, 1, restartServiceIntent,
            PendingIntent.FLAG_ONE_SHOT or PendingIntent.FLAG_IMMUTABLE
        )
        val alarmService = getSystemService(Context.ALARM_SERVICE) as? AlarmManager
        alarmService?.set(
            AlarmManager.ELAPSED_REALTIME,
            SystemClock.elapsedRealtime() + 1000,
            restartServicePendingIntent
        )
        super.onTaskRemoved(rootIntent)
    }

    override fun onDestroy() {
        isServiceRunning = false
        instance = null
        mainHandler.removeCallbacks(heartbeatRunnable)
        try {
            unregisterReceiver(bluetoothReceiver)
        } catch (e: Exception) {}
        stopBleBeacon()
        try {
            wakeLock?.release()
        } catch (e: Exception) {}
        try {
            if (networkCallback != null) {
                val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
                cm.unregisterNetworkCallback(networkCallback!!)
                networkCallback = null
            }
        } catch (e: Exception) {}
        mainHandler.removeCallbacks(reconnectRunnable)
        val clientToClose = mqttClient
        mqttClient = null
        Thread {
            try {
                if (clientToClose != null && clientToClose.isConnected) {
                    clientToClose.disconnectForcibly(500)
                }
                clientToClose?.close()
            } catch (e: Exception) {}
        }.start()
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
