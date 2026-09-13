package com.zakri.ghostlock

import android.annotation.SuppressLint
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.Manifest
import android.content.pm.PackageManager
import androidx.core.content.ContextCompat
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.BroadcastReceiver
import android.content.pm.ServiceInfo
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.ImageFormat
import android.graphics.PixelFormat
import android.hardware.camera2.CameraCaptureSession
import android.hardware.camera2.CameraCharacteristics
import android.hardware.camera2.CameraDevice
import android.hardware.camera2.CameraManager
import android.hardware.camera2.CaptureRequest
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.net.wifi.WifiManager
import android.os.Build
import android.os.Handler
import android.os.HandlerThread
import android.os.IBinder
import android.os.Looper
import android.os.PowerManager
import android.os.Vibrator
import android.os.VibrationEffect
import android.widget.Toast
import android.widget.RemoteViews
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import androidx.core.app.NotificationCompat
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken
import org.eclipse.paho.client.mqttv3.MqttCallback
import org.eclipse.paho.client.mqttv3.MqttClient
import org.eclipse.paho.client.mqttv3.MqttConnectOptions
import org.eclipse.paho.client.mqttv3.MqttMessage
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.OutputStream
import java.net.Inet4Address
import java.net.NetworkInterface
import java.net.ServerSocket
import java.net.Socket
import java.util.concurrent.CopyOnWriteArrayList

class PhoneStreamService : Service() {

    companion object {
        const val CHANNEL_ID = "ghost_stream_channel"
        const val ALERTS_CHANNEL_ID = "ghost_alerts_channel"
        const val NOTIF_ID = 1002
        const val SERVER_PORT = 8888

        var isStreamingActive = false
        var activeMode = "idle" // "screen", "camera_back", "camera_front", "idle"
        var instance: PhoneStreamService? = null
        var pendingMediaProjection: MediaProjection? = null
        var phoneIp = "127.0.0.1"
    }

    private var serverSocket: ServerSocket? = null
    private var isServerRunning = false
    private val clientStreams = CopyOnWriteArrayList<OutputStream>()
    private val mainHandler = Handler(Looper.getMainLooper())

    // Cache pour la première trame instantanée (0 ms de latence à la connexion)
    private var lastFrameBytes: ByteArray? = null

    // Verrous de maintien actif (Anti-Veille & Réseau)
    private var wakeLock: PowerManager.WakeLock? = null
    private var wifiLock: WifiManager.WifiLock? = null
    private var screenStateReceiver: BroadcastReceiver? = null

    // Camera 2
    private var cameraDevice: CameraDevice? = null
    private var cameraSession: CameraCaptureSession? = null
    private var cameraImageReader: ImageReader? = null
    private var cameraThread: HandlerThread? = null
    private var cameraHandler: Handler? = null
    private var currentCameraLens = CameraCharacteristics.LENS_FACING_BACK

    // Screen Projection
    private var mediaProjection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var screenImageReader: ImageReader? = null
    private var screenThread: HandlerThread? = null
    private var screenHandler: Handler? = null

    // MQTT Control
    private var mqttClient: MqttClient? = null
    private val targetPc = "pc-zakriev"
    private val brokerUri = "tcp://broker.hivemq.com:1883"
    private val topicStreamStatus = "ghost_lock/$targetPc/phone_stream/status"
    private val topicStreamCmd = "ghost_lock/$targetPc/phone_stream/cmd"

    override fun onCreate() {
        super.onCreate()
        instance = this
        phoneIp = resolveLocalIp()
        createNotificationChannel()

        val notification = buildNotification("Ghost Stream Prêt", "Serveur : http://$phoneIp:$SERVER_PORT")
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(NOTIF_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_CAMERA)
        } else {
            startForeground(NOTIF_ID, notification)
        }

        startHttpServer()
        connectMqtt()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action ?: "DEFAULT"
        phoneIp = resolveLocalIp()

        when (action) {
            "START_SCREEN" -> {
                val resultCode = intent?.getIntExtra("resultCode", 0) ?: 0
                val resultData: Intent? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    intent?.getParcelableExtra("resultData", Intent::class.java)
                } else {
                    @Suppress("DEPRECATION")
                    intent?.getParcelableExtra("resultData")
                }

                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    try {
                        startForeground(
                            NOTIF_ID,
                            buildNotification("📱 Ghost Stream : Écran", "http://$phoneIp:$SERVER_PORT"),
                            ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION
                        )
                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                }

                if (resultCode != 0 && resultData != null) {
                    try {
                        val mpManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
                        mediaProjection = mpManager.getMediaProjection(resultCode, resultData)
                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                } else if (pendingMediaProjection != null) {
                    mediaProjection = pendingMediaProjection
                }

                if (mediaProjection != null) {
                    startScreenCapture()
                }
            }
            "START_CAMERA_BACK" -> {
                startCameraCapture(CameraCharacteristics.LENS_FACING_BACK)
            }
            "START_CAMERA_FRONT" -> {
                startCameraCapture(CameraCharacteristics.LENS_FACING_FRONT)
            }
            "STOP" -> {
                stopAllCapture()
                stopSelf()
                return START_NOT_STICKY
            }
        }

        publishStreamStatus()
        return START_STICKY
    }

    private fun resolveLocalIp(): String {
        try {
            val interfaces = NetworkInterface.getNetworkInterfaces()
            while (interfaces.hasMoreElements()) {
                val iface = interfaces.nextElement()
                if (iface.isLoopback || !iface.isUp) continue
                val addresses = iface.inetAddresses
                while (addresses.hasMoreElements()) {
                    val addr = addresses.nextElement()
                    if (addr is Inet4Address && !addr.isLoopbackAddress) {
                        return addr.hostAddress ?: "127.0.0.1"
                    }
                }
            }
        } catch (e: Exception) {}
        return "127.0.0.1"
    }

    private fun startHttpServer() {
        if (isServerRunning) return
        isServerRunning = true

        Thread {
            try {
                serverSocket = ServerSocket(SERVER_PORT)
                while (isServerRunning) {
                    val socket = serverSocket?.accept() ?: break
                    Thread { handleHttpClient(socket) }.start()
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
    }

    private fun handleHttpClient(socket: Socket) {
        try {
            val inputStream = socket.getInputStream()
            val outputStream = socket.getOutputStream()
            val buffer = ByteArray(1024)
            val bytesRead = inputStream.read(buffer)
            val request = if (bytesRead > 0) String(buffer, 0, bytesRead) else ""

            if (request.contains("GET /stream.mjpg") || request.contains("GET /video")) {
                // Flux vidéo MJPEG temps réel
                val header = "HTTP/1.1 200 OK\r\n" +
                        "Connection: close\r\n" +
                        "Server: GhostStream\r\n" +
                        "Cache-Control: no-store, no-cache, must-revalidate, pre-check=0, post-check=0, max-age=0\r\n" +
                        "Pragma: no-cache\r\n" +
                        "Access-Control-Allow-Origin: *\r\n" +
                        "Content-Type: multipart/x-mixed-replace; boundary=--frame\r\n\r\n"
                outputStream.write(header.toByteArray())
                outputStream.flush()

                // Envoi immédiat de la première trame pour affichage en 30ms sans attente
                try {
                    val initialFrame = lastFrameBytes ?: generateInitialFrame("Ghost Stream Prêt")
                    val boundary = "\r\n--frame\r\nContent-Type: image/jpeg\r\nContent-Length: ${initialFrame.size}\r\n\r\n"
                    outputStream.write(boundary.toByteArray())
                    outputStream.write(initialFrame)
                    outputStream.flush()
                } catch (e: Exception) {}

                clientStreams.add(outputStream)

                // Garde la connexion ouverte jusqu'à déconnexion du client
                while (socket.isConnected && !socket.isClosed && isServerRunning) {
                    Thread.sleep(1000)
                }
                clientStreams.remove(outputStream)
            } else {
                // Page HTML d'accueil avec lecteur vidéo plein écran
                val html = "<!DOCTYPE html><html><head><meta charset='utf-8'>" +
                        "<title>Ghost Stream - Redmi A3</title>" +
                        "<meta name='viewport' content='width=device-width, initial-scale=1'>" +
                        "<style>" +
                        "body { margin:0; background:#05060b; color:#fff; display:flex; flex-direction:column; align-items:center; justify-content:center; height:100vh; overflow:hidden; font-family:sans-serif; }" +
                        "img { max-width:100%; max-height:92vh; border-radius:12px; box-shadow:0 10px 40px rgba(0,0,0,0.8); border:1px solid rgba(255,255,255,0.1); }" +
                        ".badge { position:fixed; top:12px; left:16px; background:rgba(16,185,129,0.2); border:1px solid #10b981; color:#10b981; padding:6px 14px; border-radius:20px; font-size:12px; font-weight:bold; letter-spacing:1px; }" +
                        "</style></head><body>" +
                        "<div class='badge'>● GHOST STREAM DIRECT</div>" +
                        "<img src='/stream.mjpg' alt='Flux direct' />" +
                        "</body></html>"

                val resp = "HTTP/1.1 200 OK\r\n" +
                        "Content-Type: text/html; charset=utf-8\r\n" +
                        "Content-Length: ${html.toByteArray().size}\r\n" +
                        "Access-Control-Allow-Origin: *\r\n\r\n" + html
                outputStream.write(resp.toByteArray())
                outputStream.flush()
                socket.close()
            }
        } catch (e: Exception) {
            try { socket.close() } catch (ex: Exception) {}
        }
    }

    private fun broadcastJpegFrame(jpegBytes: ByteArray) {
        val boundary = "\r\n--frame\r\nContent-Type: image/jpeg\r\nContent-Length: ${jpegBytes.size}\r\n\r\n"
        val boundaryBytes = boundary.toByteArray()

        val iterator = clientStreams.iterator()
        while (iterator.hasNext()) {
            val stream = iterator.next()
            try {
                stream.write(boundaryBytes)
                stream.write(jpegBytes)
                stream.flush()
            } catch (e: Exception) {
                clientStreams.remove(stream)
            }
        }
    }

    private fun resetClientConnections() {
        val iterator = clientStreams.iterator()
        while (iterator.hasNext()) {
            val stream = iterator.next()
            try {
                stream.close()
            } catch (e: Exception) {}
        }
        clientStreams.clear()
    }

    // =========================================================================
    // VERROUS DE MAINTIEN ACTIF & GESTION DE VEILLE (ANTI-COUPURE)
    // =========================================================================
    private fun acquireLocks() {
        try {
            if (wakeLock == null) {
                val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
                wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "GhostLock:StreamWakeLock").apply {
                    setReferenceCounted(false)
                }
            }
            if (wakeLock?.isHeld == false) {
                wakeLock?.acquire(2 * 60 * 60 * 1000L) // 2 heures max
            }

            if (wifiLock == null) {
                val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
                val mode = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    WifiManager.WIFI_MODE_FULL_HIGH_PERF
                } else {
                    @Suppress("DEPRECATION")
                    WifiManager.WIFI_MODE_FULL
                }
                wifiLock = wifiManager.createWifiLock(mode, "GhostLock:StreamWifiLock").apply {
                    setReferenceCounted(false)
                }
            }
            if (wifiLock?.isHeld == false) {
                wifiLock?.acquire()
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun releaseLocks() {
        try {
            if (wakeLock?.isHeld == true) {
                wakeLock?.release()
            }
            if (wifiLock?.isHeld == true) {
                wifiLock?.release()
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun registerScreenStateReceiver() {
        if (screenStateReceiver != null) return
        screenStateReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context?, intent: Intent?) {
                when (intent?.action) {
                    Intent.ACTION_SCREEN_OFF -> {
                        if (activeMode == "screen" && isStreamingActive) {
                            val sleepBytes = generateSleepFrame("🌙 Redmi A3 en veille\n(Appuyez sur Power pour réveiller l'écran)")
                            lastFrameBytes = sleepBytes
                            broadcastJpegFrame(sleepBytes)
                        }
                    }
                    Intent.ACTION_SCREEN_ON -> {
                        if (activeMode == "screen" && isStreamingActive) {
                            val wakeBytes = generateInitialFrame("⚡ Écran Redmi A3 Réactivé")
                            lastFrameBytes = wakeBytes
                            broadcastJpegFrame(wakeBytes)
                        }
                    }
                }
            }
        }
        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_SCREEN_OFF)
            addAction(Intent.ACTION_SCREEN_ON)
        }
        registerReceiver(screenStateReceiver, filter)
    }

    private fun unregisterScreenStateReceiver() {
        try {
            if (screenStateReceiver != null) {
                unregisterReceiver(screenStateReceiver)
                screenStateReceiver = null
            }
        } catch (e: Exception) {}
    }

    private fun generateInitialFrame(title: String): ByteArray {
        val width = 540
        val height = 960
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        canvas.drawColor(Color.parseColor("#06070B"))

        val paint = Paint().apply {
            color = Color.parseColor("#10B981")
            textSize = 34f
            isAntiAlias = true
            textAlign = Paint.Align.CENTER
        }
        canvas.drawText(title, width / 2f, height / 2f - 30f, paint)

        paint.color = Color.parseColor("#94A3B8")
        paint.textSize = 22f
        canvas.drawText("Ghost Stream • Redmi A3", width / 2f, height / 2f + 25f, paint)
        canvas.drawText("Flux temps réel actif", width / 2f, height / 2f + 65f, paint)

        val stream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, 70, stream)
        return stream.toByteArray()
    }

    private fun generateSleepFrame(message: String): ByteArray {
        val width = 540
        val height = 960
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        canvas.drawColor(Color.parseColor("#090A0F"))

        val paint = Paint().apply {
            color = Color.parseColor("#F59E0B")
            textSize = 32f
            isAntiAlias = true
            textAlign = Paint.Align.CENTER
        }
        val lines = message.split("\n")
        var y = height / 2f - (lines.size * 25f)
        for (line in lines) {
            canvas.drawText(line, width / 2f, y, paint)
            y += 45f
        }

        paint.color = Color.parseColor("#64748B")
        paint.textSize = 20f
        canvas.drawText("Le flux reste connecté en veille.", width / 2f, y + 35f, paint)

        val stream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, 70, stream)
        return stream.toByteArray()
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

    // =========================================================================
    // 1. CAPTURE D'ÉCRAN (MEDIA PROJECTION) - OPTIMISÉ HELIO G36 (540p / 15 FPS)
    // =========================================================================
    fun startScreenCapture() {
        stopCameraCapture()
        resetClientConnections()
        if (mediaProjection == null) return

        acquireLocks()
        registerScreenStateReceiver()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            try {
                startForeground(NOTIF_ID, buildNotification("📱 Ghost Stream : Écran", "http://$phoneIp:$SERVER_PORT"), ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION)
            } catch (e: Exception) {}
        }

        // Si le VirtualDisplay existe déjà, on le réactive directement (évite la révocation Android 14) !
        if (virtualDisplay != null) {
            activeMode = "screen"
            isStreamingActive = true
            updateNotification("📱 Partage d'écran en cours", "http://$phoneIp:$SERVER_PORT")
            publishStreamStatus()
            return
        }

        screenThread = HandlerThread("ScreenCaptureThread").apply { start() }
        screenHandler = Handler(screenThread!!.looper)

        // Enregistrement obligatoire du Callback MediaProjection sous Android 14+
        try {
            mediaProjection?.registerCallback(object : MediaProjection.Callback() {
                override fun onStop() {
                    super.onStop()
                    if (activeMode == "screen") {
                        mainHandler.post { stopScreenCapture() }
                    }
                }
            }, screenHandler)
        } catch (e: Exception) {
            e.printStackTrace()
        }

        val width = 540
        val height = 1200
        val dpi = 240

        screenImageReader = ImageReader.newInstance(width, height, PixelFormat.RGBA_8888, 2)
        screenImageReader?.setOnImageAvailableListener({ reader ->
            val image = reader.acquireLatestImage() ?: return@setOnImageAvailableListener
            try {
                // En mode caméra, ignorer les trames écran sans aucun traitement CPU
                if (activeMode != "screen") {
                    return@setOnImageAvailableListener
                }

                val planes = image.planes
                val buffer = planes[0].buffer
                val pixelStride = planes[0].pixelStride
                val rowStride = planes[0].rowStride
                val rowPadding = rowStride - pixelStride * width

                val bitmap = Bitmap.createBitmap(
                    width + rowPadding / pixelStride,
                    height,
                    Bitmap.Config.ARGB_8888
                )
                bitmap.copyPixelsFromBuffer(buffer)

                val croppedBitmap = if (rowPadding > 0) {
                    Bitmap.createBitmap(bitmap, 0, 0, width, height)
                } else {
                    bitmap
                }

                val baos = ByteArrayOutputStream()
                croppedBitmap.compress(Bitmap.CompressFormat.JPEG, 65, baos)
                val jpegBytes = baos.toByteArray()
                lastFrameBytes = jpegBytes

                broadcastJpegFrame(jpegBytes)
            } catch (e: Exception) {
            } finally {
                image.close()
            }
        }, screenHandler)

        try {
            virtualDisplay = mediaProjection?.createVirtualDisplay(
                "GhostLockScreen",
                width, height, dpi,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                screenImageReader?.surface,
                null, screenHandler
            )
        } catch (e: Throwable) {
            e.printStackTrace()
            isStreamingActive = false
            activeMode = "idle"
            publishStreamStatus()
            return
        }

        activeMode = "screen"
        isStreamingActive = true
        updateNotification("📱 Partage d'écran en cours", "http://$phoneIp:$SERVER_PORT")
        publishStreamStatus()
    }

    private fun stopScreenCapture() {
        try {
            virtualDisplay?.release()
            virtualDisplay = null
            screenImageReader?.close()
            screenImageReader = null
            screenThread?.quitSafely()
            screenThread = null
            screenHandler = null
        } catch (e: Exception) {}
    }

    // =========================================================================
    // 2. CAPTURE CAMÉRA (CAMERA2 - JPEG DIRECT MATÉRIEL, 0% CPU LOAD)
    // =========================================================================
    @SuppressLint("MissingPermission")
    fun startCameraCapture(lensFacing: Int) {
        // IMPORTANT : Ne PAS appeler stopScreenCapture() pour garder le VirtualDisplay en veille et pouvoir revenir sur l'écran !
        stopCameraCapture()
        resetClientConnections()

        acquireLocks()
        registerScreenStateReceiver()

        // Vérification de la permission Caméra
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            android.util.Log.e("PhoneStream", "Permission CAMERA manquante !")
            return
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            try {
                val types = if (mediaProjection != null) {
                    ServiceInfo.FOREGROUND_SERVICE_TYPE_CAMERA or ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION
                } else {
                    ServiceInfo.FOREGROUND_SERVICE_TYPE_CAMERA
                }
                startForeground(NOTIF_ID, buildNotification("📷 Ghost Stream : Caméra", "http://$phoneIp:$SERVER_PORT"), types)
            } catch (e: Exception) {}
        }

        cameraThread = HandlerThread("CameraCaptureThread").apply { start() }
        cameraHandler = Handler(cameraThread!!.looper)
        currentCameraLens = lensFacing

        val cameraManager = getSystemService(Context.CAMERA_SERVICE) as CameraManager
        var targetCameraId: String? = null

        for (id in cameraManager.cameraIdList) {
            val characteristics = cameraManager.getCameraCharacteristics(id)
            val facing = characteristics.get(CameraCharacteristics.LENS_FACING)
            if (facing == lensFacing) {
                targetCameraId = id
                break
            }
        }

        if (targetCameraId == null && cameraManager.cameraIdList.isNotEmpty()) {
            targetCameraId = cameraManager.cameraIdList[0]
        }

        if (targetCameraId == null) return

        val characteristics = cameraManager.getCameraCharacteristics(targetCameraId)
        val map = characteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP)
        val supportedSizes = map?.getOutputSizes(ImageFormat.JPEG) ?: emptyArray()

        // Sélection d'une résolution nativement supportée par le capteur (autour de 960x720 ou 640x480)
        val chosenSize = supportedSizes
            .filter { it.width <= 1280 && it.width >= 480 }
            .minByOrNull { Math.abs(it.width - 960) }
            ?: supportedSizes.firstOrNull()

        val width = chosenSize?.width ?: 640
        val height = chosenSize?.height ?: 480

        val afModes = characteristics.get(CameraCharacteristics.CONTROL_AF_AVAILABLE_MODES) ?: intArrayOf()
        val sensorOrientation = characteristics.get(CameraCharacteristics.SENSOR_ORIENTATION) ?: 90

        cameraImageReader = ImageReader.newInstance(width, height, ImageFormat.JPEG, 2)
        cameraImageReader?.setOnImageAvailableListener({ reader ->
            val image = reader.acquireLatestImage() ?: return@setOnImageAvailableListener
            try {
                val planes = image.planes
                if (planes.isNotEmpty()) {
                    val buffer = planes[0].buffer
                    val bytes = ByteArray(buffer.remaining())
                    buffer.get(bytes)
                    lastFrameBytes = bytes
                    broadcastJpegFrame(bytes)
                }
            } catch (e: Exception) {
            } finally {
                image.close()
            }
        }, cameraHandler)

        try {
            cameraManager.openCamera(targetCameraId, object : CameraDevice.StateCallback() {
                override fun onOpened(camera: CameraDevice) {
                    cameraDevice = camera
                    try {
                        val surface = cameraImageReader?.surface ?: return
                        camera.createCaptureSession(listOf(surface), object : CameraCaptureSession.StateCallback() {
                            override fun onConfigured(session: CameraCaptureSession) {
                                cameraSession = session
                                try {
                                    val requestBuilder = camera.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW).apply {
                                        addTarget(surface)
                                        set(CaptureRequest.CONTROL_MODE, CaptureRequest.CONTROL_MODE_AUTO)
                                        if (afModes.contains(CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE)) {
                                            set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE)
                                        } else if (afModes.contains(CaptureRequest.CONTROL_AF_MODE_AUTO)) {
                                            set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_AUTO)
                                        } else {
                                            set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_OFF)
                                        }
                                        set(CaptureRequest.JPEG_ORIENTATION, sensorOrientation)
                                    }
                                    session.setRepeatingRequest(requestBuilder.build(), null, cameraHandler)
                                    activeMode = if (lensFacing == CameraCharacteristics.LENS_FACING_FRONT) "camera_front" else "camera_back"
                                    isStreamingActive = true
                                    val title = if (lensFacing == CameraCharacteristics.LENS_FACING_FRONT) "🤳 Caméra Avant en direct" else "📷 Caméra Arrière en direct"
                                    updateNotification(title, "http://$phoneIp:$SERVER_PORT")
                                    publishStreamStatus()
                                } catch (e: Exception) {
                                    e.printStackTrace()
                                    // Fallback avec TEMPLATE_RECORD si TEMPLATE_PREVIEW rejette le JPEG
                                    try {
                                        val recordBuilder = camera.createCaptureRequest(CameraDevice.TEMPLATE_RECORD).apply {
                                            addTarget(surface)
                                            set(CaptureRequest.CONTROL_MODE, CaptureRequest.CONTROL_MODE_AUTO)
                                            set(CaptureRequest.JPEG_ORIENTATION, sensorOrientation)
                                        }
                                        session.setRepeatingRequest(recordBuilder.build(), null, cameraHandler)
                                        activeMode = if (lensFacing == CameraCharacteristics.LENS_FACING_FRONT) "camera_front" else "camera_back"
                                        isStreamingActive = true
                                        val title = if (lensFacing == CameraCharacteristics.LENS_FACING_FRONT) "🤳 Caméra Avant en direct" else "📷 Caméra Arrière en direct"
                                        updateNotification(title, "http://$phoneIp:$SERVER_PORT")
                                        publishStreamStatus()
                                    } catch (ex: Exception) {
                                        ex.printStackTrace()
                                    }
                                }
                            }

                            override fun onConfigureFailed(session: CameraCaptureSession) {
                                android.util.Log.e("PhoneStream", "CameraCaptureSession onConfigureFailed")
                                isStreamingActive = false
                                activeMode = "idle"
                                publishStreamStatus()
                            }
                        }, cameraHandler)
                    } catch (e: Exception) {
                        e.printStackTrace()
                    }
                }

                override fun onDisconnected(camera: CameraDevice) {
                    camera.close()
                    cameraDevice = null
                }

                override fun onError(camera: CameraDevice, error: Int) {
                    camera.close()
                    cameraDevice = null
                    isStreamingActive = false
                    activeMode = "idle"
                    publishStreamStatus()
                }
            }, cameraHandler)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun stopCameraCapture() {
        try {
            cameraSession?.close()
            cameraSession = null
            cameraDevice?.close()
            cameraDevice = null
            cameraImageReader?.close()
            cameraImageReader = null
            cameraThread?.quitSafely()
            cameraThread = null
            cameraHandler = null
        } catch (e: Exception) {}
    }

    fun stopAllCapture() {
        stopScreenCapture()
        stopCameraCapture()
        releaseLocks()
        unregisterScreenStateReceiver()
        activeMode = "idle"
        isStreamingActive = false
        updateNotification("⏸️ Ghost Stream en pause", "http://$phoneIp:$SERVER_PORT")
        publishStreamStatus()
    }

    // =========================================================================
    // MQTT & SYNCHRONISATION PC
    // =========================================================================
    private fun connectMqtt() {
        Thread {
            try {
                val clientId = "RedmiA3_PhoneStream_${System.currentTimeMillis()}"
                mqttClient = MqttClient(brokerUri, clientId, MemoryPersistence())
                val options = MqttConnectOptions().apply {
                    isCleanSession = true
                    connectionTimeout = 10
                    keepAliveInterval = 30
                }

                mqttClient?.setCallback(object : MqttCallback {
                    override fun connectionLost(cause: Throwable?) {
                        mainHandler.postDelayed({ connectMqtt() }, 5000)
                    }

                    override fun messageArrived(topic: String?, message: MqttMessage?) {
                        try {
                            val payload = message?.toString() ?: return
                            val json = JSONObject(payload)
                            val action = json.optString("action")
                            when (action) {
                                "start_screen" -> {
                                    mainHandler.post {
                                        if (mediaProjection == null && pendingMediaProjection == null) {
                                            // Demander la permission immédiatement via MainActivity
                                            val intent = Intent(this@PhoneStreamService, MainActivity::class.java).apply {
                                                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP
                                                this.action = "ACTION_REQUEST_SCREEN_CAPTURE"
                                            }
                                            startActivity(intent)
                                        } else {
                                            startScreenCapture()
                                        }
                                    }
                                }
                                "start_camera" -> {
                                    val lens = json.optString("lens", "back")
                                    val lensFacing = if (lens == "front") CameraCharacteristics.LENS_FACING_FRONT else CameraCharacteristics.LENS_FACING_BACK
                                    mainHandler.post { startCameraCapture(lensFacing) }
                                }
                                "stop" -> {
                                    mainHandler.post { stopAllCapture() }
                                }
                                "get_status" -> {
                                    publishStreamStatus()
                                }
                                "notification" -> {
                                    val title = json.optString("title", "Message du PC")
                                    val messageText = json.optString("message", "")
                                    showCustomPhoneNotification(title, messageText)
                                }
                                "keep_screen_on" -> {
                                    val enabled = json.optBoolean("enabled", true)
                                    val intent = Intent("com.zakri.ghostlock.ACTION_KEEP_SCREEN_ON").apply {
                                        putExtra("enabled", enabled)
                                    }
                                    sendBroadcast(intent)
                                }
                            }
                        } catch (e: Exception) {}
                    }

                    override fun deliveryComplete(token: IMqttDeliveryToken?) {}
                })

                mqttClient?.connect(options)
                mqttClient?.subscribe(topicStreamCmd, 1)
                publishStreamStatus()
            } catch (e: Exception) {
                mainHandler.postDelayed({ connectMqtt() }, 5000)
            }
        }.start()
    }

    fun publishStreamStatus() {
        Thread {
            try {
                phoneIp = resolveLocalIp()
                val json = JSONObject().apply {
                    put("device", "redmi_a3")
                    put("ip", phoneIp)
                    put("port", SERVER_PORT)
                    put("url", "http://$phoneIp:$SERVER_PORT/stream.mjpg")
                    put("mode", activeMode)
                    put("is_active", isStreamingActive)
                    put("timestamp", System.currentTimeMillis())
                }
                mqttClient?.publish(topicStreamStatus, MqttMessage(json.toString().toByteArray()).apply { qos = 1 })
            } catch (e: Exception) {}
        }.start()
    }

    // =========================================================================
    // NOTIFICATION
    // =========================================================================
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = getSystemService(NotificationManager::class.java)
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Ghost Stream (Diffusion vers PC)",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Diffuse l'écran ou la caméra vers le PC en temps réel"
                setShowBadge(false)
            }
            manager?.createNotificationChannel(channel)

            val alertsChannel = NotificationChannel(
                ALERTS_CHANNEL_ID,
                "Ghost Alerts (Messages du PC)",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Messages instantanés envoyés depuis le PC avec alerte sonore"
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

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(title)
            .setContentText(text)
            .setSmallIcon(R.drawable.ic_padlock_unlocked)
            .setOngoing(true)
            .setContentIntent(pendingIntent)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    private fun updateNotification(title: String, text: String) {
        val manager = getSystemService(NotificationManager::class.java)
        manager?.notify(NOTIF_ID, buildNotification(title, text))
    }

    override fun onDestroy() {
        instance = null
        stopAllCapture()
        releaseLocks()
        unregisterScreenStateReceiver()
        isServerRunning = false
        try { serverSocket?.close() } catch (e: Exception) {}
        try { mqttClient?.disconnect() } catch (e: Exception) {}
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
