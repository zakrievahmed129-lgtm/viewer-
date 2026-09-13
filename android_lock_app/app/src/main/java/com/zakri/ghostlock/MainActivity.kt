package com.zakri.ghostlock

import android.Manifest
import android.animation.AnimatorSet
import android.animation.ObjectAnimator
import android.animation.ValueAnimator
import android.view.animation.DecelerateInterpolator
import android.view.animation.OvershootInterpolator
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothManager
import android.bluetooth.le.AdvertiseCallback
import android.bluetooth.le.AdvertiseData
import android.bluetooth.le.AdvertiseSettings
import android.bluetooth.le.BluetoothLeAdvertiser
import android.content.Context
import android.content.Intent
import android.content.BroadcastReceiver
import android.content.IntentFilter
import android.view.WindowManager
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.ParcelUuid
import android.os.VibrationEffect
import android.os.Vibrator
import android.provider.Settings
import android.media.projection.MediaProjectionManager
import android.hardware.camera2.CameraCharacteristics
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import android.net.Uri
import android.os.PowerManager
import android.app.Dialog
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.view.View
import android.view.Window
import android.view.ViewGroup
import com.zakri.ghostlock.databinding.ActivityMainBinding
import com.zakri.ghostlock.databinding.DialogSelectPcBinding
import com.zakri.ghostlock.databinding.ItemPcChoiceBinding
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken
import org.eclipse.paho.client.mqttv3.MqttCallback
import org.eclipse.paho.client.mqttv3.MqttClient
import org.eclipse.paho.client.mqttv3.MqttConnectOptions
import org.eclipse.paho.client.mqttv3.MqttMessage
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence
import org.json.JSONObject
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.Executor

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    // Paramètres MQTT & Multi-PC
    private val brokerUri = "tcp://broker.hivemq.com:1883"
    private var targetPc = "pc-zakriev"
    private var topicStatus = "ghost_lock/$targetPc/status"
    private var topicCmd = "ghost_lock/$targetPc/cmd"
    private var topicHeartbeat = "ghost_lock/$targetPc/heartbeat"

    data class DiscoveredPc(
        val name: String,
        var isOnline: Boolean = true,
        var isLocked: Boolean = true,
        var lastSeen: Long = System.currentTimeMillis(),
        var timeStr: String = ""
    )

    private val discoveredPcs = ConcurrentHashMap<String, DiscoveredPc>()
    private var pcSelectorDialog: Dialog? = null

    // Bluetooth BLE (Balise de Proximité RSSI)
    private var bluetoothAdapter: BluetoothAdapter? = null
    private var advertiser: BluetoothLeAdvertiser? = null
    private val serviceUuid = UUID.fromString("0000ffe0-0000-1000-8000-00805f9b34fb")
    private var isAdvertising = false

    private var mqttClient: MqttClient? = null
    private val mainHandler = Handler(Looper.getMainLooper())

    private lateinit var executor: Executor
    private lateinit var biometricPrompt: BiometricPrompt

    private var isPcLocked = true
    private var proximityRunning = true
    private var pendingBiometricAction = "unlock" // "unlock" ou "lock"
    private var lastPcPacketTimestamp = 0L
    private var lastPcTimeStr = ""
    private var isAutoLockArmed = false

    private var keepScreenReceiver: BroadcastReceiver? = null

    // Gestion des permissions Bluetooth Android 12+
    private val requestBluetoothPermissions = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val granted = permissions.entries.all { it.value }
        if (granted) {
            startBleBeacon()
        } else {
            binding.tvLogs.text = "Bluetooth refusé : la proximité passera par Wi-Fi."
        }
    }

    private lateinit var mediaProjectionManager: MediaProjectionManager

    private val screenCaptureLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        try {
            if (result.resultCode == RESULT_OK && result.data != null) {
                val serviceIntent = Intent(this, PhoneStreamService::class.java).apply {
                    action = "START_SCREEN"
                    putExtra("resultCode", result.resultCode)
                    putExtra("resultData", result.data)
                }
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    ContextCompat.startForegroundService(this, serviceIntent)
                } else {
                    startService(serviceIntent)
                }
                updateStreamUi("screen", true)
                binding.tvLogs.text = "📱 Diffusion de l'écran en cours vers le PC"
                Toast.makeText(this, "Diffusion écran lancée !", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, "Autorisation d'enregistrement d'écran refusée", Toast.LENGTH_SHORT).show()
            }
        } catch (e: Exception) {
            e.printStackTrace()
            binding.tvLogs.text = "Erreur démarrage écran : ${e.message}"
            Toast.makeText(this, "Erreur : ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    private val requestCameraPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) {
            startCameraStreaming(CameraCharacteristics.LENS_FACING_BACK)
        } else {
            Toast.makeText(this, "Permission caméra requise pour diffuser", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        targetPc = GhostPrefs.getSelectedPc(this)
        topicStatus = "ghost_lock/$targetPc/status"
        topicCmd = "ghost_lock/$targetPc/cmd"
        topicHeartbeat = "ghost_lock/$targetPc/heartbeat"

        binding.tvPcName.text = "🖥️ $targetPc"
        updateDiscoveredCountUI()

        mediaProjectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager

        setupBiometrics()
        setupListeners()
        setupBluetooth()
        startPersistentBackgroundService()

        // Lancement automatique du sélecteur au démarrage si configuré
        if (GhostPrefs.isAskOnStartup(this)) {
            mainHandler.postDelayed({
                if (!isFinishing && !isDestroyed) {
                    showPcSelectorDialog()
                }
            }, 500)
        }

        // Demande de permission Caméra au démarrage pour autoriser la diffusion distante
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            requestCameraPermission.launch(Manifest.permission.CAMERA)
        }

        connectMqtt()
        startHeartbeatLoop()
        startPcWatchdogLoop()
        startRadarRingAnimations()

        setupKeepScreenReceiver()
        handleIncomingIntent(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleIncomingIntent(intent)
    }

    private fun handleIncomingIntent(intent: Intent?) {
        val action = intent?.action ?: return
        if (action == "ACTION_REQUEST_SCREEN_CAPTURE") {
            try {
                val captureIntent = mediaProjectionManager.createScreenCaptureIntent()
                screenCaptureLauncher.launch(captureIntent)
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    private fun setupKeepScreenReceiver() {
        keepScreenReceiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context?, intent: Intent?) {
                val enabled = intent?.getBooleanExtra("enabled", true) ?: true
                if (enabled) {
                    window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
                    Toast.makeText(this@MainActivity, "💡 Anti-Veille Activé par le PC", Toast.LENGTH_SHORT).show()
                } else {
                    window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
                    Toast.makeText(this@MainActivity, "🌙 Veille normale réactivée", Toast.LENGTH_SHORT).show()
                }
            }
        }
        val filter = IntentFilter("com.zakri.ghostlock.ACTION_KEEP_SCREEN_ON")
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(keepScreenReceiver, filter, Context.RECEIVER_NOT_EXPORTED)
        } else {
            registerReceiver(keepScreenReceiver, filter)
        }
    }

    private fun startPersistentBackgroundService() {
        // 1. Permission de notification Android 13+ (TIRAMISU)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 101)
            }
        }

        // 2. Démarrage immédiat du service permanent 24/7
        try {
            val serviceIntent = Intent(this, GhostLockService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                ContextCompat.startForegroundService(this, serviceIntent)
            } else {
                startService(serviceIntent)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }

        // 3. Demande d'exemption d'optimisation batterie (spécifique Xiaomi / Redmi MIUI / HyperOS)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            try {
                val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
                if (!powerManager.isIgnoringBatteryOptimizations(packageName)) {
                    val intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS).apply {
                        data = Uri.parse("package:$packageName")
                    }
                    startActivity(intent)
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }


    private fun setupBiometrics() {
        executor = ContextCompat.getMainExecutor(this)
        biometricPrompt = BiometricPrompt(this, executor, object : BiometricPrompt.AuthenticationCallback() {
            override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                super.onAuthenticationSucceeded(result)
                vibratePhone()
                when (pendingBiometricAction) {
                    "lock" -> {
                        sendMqttCommand("lock")
                        isPcLocked = true
                        animateLockSequence()
                        binding.tvLogs.text = "🔒 Empreinte validée ! PC verrouillé."
                        Toast.makeText(this@MainActivity, "PC Verrouillé !", Toast.LENGTH_SHORT).show()
                    }
                    "viewer" -> {
                        showGhostScriptLaunchConfirmation()
                    }

                    else -> {
                        sendMqttCommand("unlock")
                        isPcLocked = false
                        animateUnlockSequence()
                        binding.tvLogs.text = "✅ Empreinte validée ! Déverrouillage du PC..."
                        Toast.makeText(this@MainActivity, "Accès PC autorisé !", Toast.LENGTH_SHORT).show()
                    }
                }
            }

            override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                super.onAuthenticationError(errorCode, errString)
                binding.tvLogs.text = "Info : $errString"
            }

            override fun onAuthenticationFailed() {
                super.onAuthenticationFailed()
                binding.tvLogs.text = "❌ Empreinte non reconnue. Réessayez."
            }
        })
    }

    private fun showGhostScriptLaunchConfirmation() {
        MaterialAlertDialogBuilder(this)
            .setTitle("🚀 Lancement de Ghost Script")
            .setMessage("Empreinte biométrique validée avec succès.\n\nSouhaitez-vous lancer ghost_script.exe sur l'ordinateur distant ?")
            .setPositiveButton("Oui, lancer sur le PC") { _, _ ->
                sendMqttCommand("launch_ghost_script")
                binding.tvLogs.text = "👻 Ordre envoyé : Lancement de ghost_script.exe sur le PC..."
                Toast.makeText(this, "Ghost Script lancé sur le PC !", Toast.LENGTH_SHORT).show()
                val intent = Intent(this, ViewerActivity::class.java)
                startActivity(intent)
            }
            .setNegativeButton("Non (Viewer seul)") { _, _ ->
                binding.tvLogs.text = "👁️ Viewer ouvert sans lancer ghost_script.exe."
                Toast.makeText(this, "Ouverture du Viewer seul...", Toast.LENGTH_SHORT).show()
                val intent = Intent(this, ViewerActivity::class.java)
                startActivity(intent)
            }
            .setNeutralButton("Annuler") { dialog, _ ->
                dialog.dismiss()
                binding.tvLogs.text = "Ouverture du Viewer annulée."
            }
            .setCancelable(true)
            .show()
    }


    private fun buildPromptInfo(title: String, subtitle: String): BiometricPrompt.PromptInfo {
        val biometricManager = BiometricManager.from(this)
        val canBio = biometricManager.canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG or BiometricManager.Authenticators.BIOMETRIC_WEAK
        )
        val canCred = biometricManager.canAuthenticate(BiometricManager.Authenticators.DEVICE_CREDENTIAL)

        val builder = BiometricPrompt.PromptInfo.Builder()
            .setTitle(title)
            .setSubtitle(subtitle)
            .setDescription("Vérification requise pour autoriser l'action sur $targetPc")

        // Règle Android : Si on autorise DEVICE_CREDENTIAL, on NE PEUT PAS mettre de NegativeButton
        // Si on utilise uniquement la biométrie, NegativeButton est OBLIGATOIRE.
        if (canBio == BiometricManager.BIOMETRIC_SUCCESS) {
            // Empreinte disponible sur le Redmi A3
            builder.setNegativeButtonText(getString(R.string.bio_prompt_negative))
            builder.setAllowedAuthenticators(
                BiometricManager.Authenticators.BIOMETRIC_STRONG or BiometricManager.Authenticators.BIOMETRIC_WEAK
            )
        } else if (canCred == BiometricManager.BIOMETRIC_SUCCESS) {
            // Pas d'empreinte enregistrée mais code PIN/schéma présent sur le téléphone
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                builder.setAllowedAuthenticators(
                    BiometricManager.Authenticators.BIOMETRIC_STRONG or BiometricManager.Authenticators.DEVICE_CREDENTIAL
                )
            } else {
                @Suppress("DEPRECATION")
                builder.setDeviceCredentialAllowed(true)
            }
        } else {
            builder.setNegativeButtonText(getString(R.string.bio_prompt_negative))
            builder.setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_WEAK)
        }

        return builder.build()
    }

    private fun triggerBiometricAuth(action: String) {
        pendingBiometricAction = action
        val title = when (action) {
            "lock" -> "Verrouillage du PC"
            "viewer" -> "Console Ghost Viewer"
            else -> getString(R.string.bio_prompt_title)
        }
        val subtitle = when (action) {
            "lock" -> "Posez votre doigt pour verrouiller le PC à distance"
            "viewer" -> "Posez votre doigt pour ouvrir le Viewer et lancer Ghost Script"
            else -> getString(R.string.bio_prompt_subtitle)
        }

        val biometricManager = BiometricManager.from(this)
        
        // 1. Test Biométrie (Empreinte digitale)
        val canBio = biometricManager.canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG or BiometricManager.Authenticators.BIOMETRIC_WEAK
        )
        // 2. Test PIN/Schéma du téléphone
        val canCred = biometricManager.canAuthenticate(BiometricManager.Authenticators.DEVICE_CREDENTIAL)

        when {
            canBio == BiometricManager.BIOMETRIC_SUCCESS || canCred == BiometricManager.BIOMETRIC_SUCCESS -> {
                try {
                    val prompt = buildPromptInfo(title, subtitle)
                    biometricPrompt.authenticate(prompt)
                } catch (e: Exception) {
                    Toast.makeText(this, "Erreur biométrie : ${e.message}", Toast.LENGTH_LONG).show()
                    binding.tvLogs.text = "Erreur: ${e.message}"
                }
            }
            canBio == BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> {
                // L'utilisateur n'a pas encore configuré d'empreinte dans les paramètres Android
                Toast.makeText(
                    this,
                    "Veuillez enregistrer une empreinte dans les Paramètres de votre téléphone.",
                    Toast.LENGTH_LONG
                ).show()
                binding.tvLogs.text = "⚠️ Aucune empreinte enregistrée dans Paramètres > Sécurité."
                
                // Ouvre directement les paramètres de sécurité du téléphone pour l'aider
                try {
                    val intent = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                        Intent(Settings.ACTION_BIOMETRIC_ENROLL).apply {
                            putExtra(
                                Settings.EXTRA_BIOMETRIC_AUTHENTICATORS_ALLOWED,
                                BiometricManager.Authenticators.BIOMETRIC_STRONG
                            )
                        }
                    } else {
                        Intent(Settings.ACTION_SECURITY_SETTINGS)
                    }
                    startActivity(intent)
                } catch (e: Exception) {
                    startActivity(Intent(Settings.ACTION_SETTINGS))
                }
            }
            canBio == BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> {
                Toast.makeText(this, "Capteur biométrique non détecté sur cet appareil.", Toast.LENGTH_LONG).show()
                binding.tvLogs.text = "❌ Matériel biométrique absent."
            }
            canBio == BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE -> {
                Toast.makeText(this, "Capteur biométrique occupé ou temporairement indisponible.", Toast.LENGTH_LONG).show()
                binding.tvLogs.text = "Capteur occupé, réessayez."
            }
            else -> {
                // Tentative directe forcée
                try {
                    val prompt = buildPromptInfo(title, subtitle)
                    biometricPrompt.authenticate(prompt)
                } catch (e: Exception) {
                    Toast.makeText(this, "Biométrie non configurée sur le téléphone.", Toast.LENGTH_LONG).show()
                    binding.tvLogs.text = "Code statut biométrique : $canBio"
                }
            }
        }
    }

    private fun setupBluetooth() {
        val bluetoothManager = getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
        bluetoothAdapter = bluetoothManager?.adapter

        if (bluetoothAdapter == null || !bluetoothAdapter!!.isEnabled) {
            binding.tvLogs.text = "Activez le Bluetooth sur votre Redmi A3 pour la mesure de distance."
            return
        }

        checkAndStartBleBeacon()
    }

    private fun checkAndStartBleBeacon() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val permissions = arrayOf(
                Manifest.permission.BLUETOOTH_ADVERTISE,
                Manifest.permission.BLUETOOTH_CONNECT
            )
            val needRequest = permissions.any {
                ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
            }
            if (needRequest) {
                requestBluetoothPermissions.launch(permissions)
                return
            }
        }
        startBleBeacon()
    }

    private fun startBleBeacon() {
        try {
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
            binding.tvLogs.text = "📡 Balise Bluetooth active : le PC mesure votre distance."
        } catch (e: SecurityException) {
            e.printStackTrace()
        } catch (e: Exception) {
            e.printStackTrace()
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

    private fun setupListeners() {
        binding.layoutPcNameClickable.setOnClickListener {
            showPcSelectorDialog()
        }

        binding.tvBtnChangePc.setOnClickListener {
            showPcSelectorDialog()
        }

        binding.layoutPcSelectorHeader.setOnClickListener {
            showPcSelectorDialog()
        }

        binding.btnUnlockBiometric.setOnClickListener {
            triggerBiometricAuth("unlock")
        }

        binding.btnLockPc.setOnClickListener {
            triggerBiometricAuth("lock")
        }

        binding.btnOpenViewer.setOnClickListener {
            triggerBiometricAuth("viewer")
        }

        binding.hubBiometric.setOnClickListener {
            triggerBiometricAuth(if (isPcLocked) "unlock" else "lock")
        }

        binding.switchProximity.setOnCheckedChangeListener { _, isChecked ->
            proximityRunning = isChecked
            sendMqttProximityState(isChecked)
            GhostLockService.instance?.setProximityEnabled(isChecked)
            if (isChecked) {
                checkAndStartBleBeacon()
                binding.tvLogs.text = "🛡️ Proximité 24/7 ACTIVE : Détecté en continu même écran éteint."
            } else {
                stopBleBeacon()
                binding.tvLogs.text = "Proximité désactivée (PC synchronisé)."
            }
        }

        binding.btnStreamScreen.setOnClickListener {
            val intent = mediaProjectionManager.createScreenCaptureIntent()
            screenCaptureLauncher.launch(intent)
        }

        binding.btnStreamCamera.setOnClickListener {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
                startCameraStreaming(CameraCharacteristics.LENS_FACING_BACK)
            } else {
                requestCameraPermission.launch(Manifest.permission.CAMERA)
            }
        }

        binding.btnStopStream.setOnClickListener {
            stopPhoneStream()
        }
    }

    private fun startRadarRingAnimations() {
        // Animation matérielle ultra-fluide des anneaux concentriques visionOS (100% GPU / RenderNode, 90 FPS sur Helio G36)
        val outerScaleX = ObjectAnimator.ofFloat(binding.radarRingOuter, "scaleX", 0.94f, 1.06f).apply {
            duration = 2400
            repeatMode = ValueAnimator.REVERSE
            repeatCount = ValueAnimator.INFINITE
        }
        val outerScaleY = ObjectAnimator.ofFloat(binding.radarRingOuter, "scaleY", 0.94f, 1.06f).apply {
            duration = 2400
            repeatMode = ValueAnimator.REVERSE
            repeatCount = ValueAnimator.INFINITE
        }
        val outerAlpha = ObjectAnimator.ofFloat(binding.radarRingOuter, "alpha", 0.35f, 0.85f).apply {
            duration = 2400
            repeatMode = ValueAnimator.REVERSE
            repeatCount = ValueAnimator.INFINITE
        }

        val midScaleX = ObjectAnimator.ofFloat(binding.radarRingMid, "scaleX", 1.05f, 0.95f).apply {
            duration = 1800
            repeatMode = ValueAnimator.REVERSE
            repeatCount = ValueAnimator.INFINITE
        }
        val midScaleY = ObjectAnimator.ofFloat(binding.radarRingMid, "scaleY", 1.05f, 0.95f).apply {
            duration = 1800
            repeatMode = ValueAnimator.REVERSE
            repeatCount = ValueAnimator.INFINITE
        }
        val midAlpha = ObjectAnimator.ofFloat(binding.radarRingMid, "alpha", 0.45f, 0.95f).apply {
            duration = 1800
            repeatMode = ValueAnimator.REVERSE
            repeatCount = ValueAnimator.INFINITE
        }

        AnimatorSet().apply {
            playTogether(outerScaleX, outerScaleY, outerAlpha, midScaleX, midScaleY, midAlpha)
            start()
        }
    }

    private fun stopBleBeacon() {
        try {
            if (isAdvertising) {
                advertiser?.stopAdvertising(advertiseCallback)
                isAdvertising = false
            }
        } catch (e: Exception) {}
    }

    private fun connectMqtt() {
        Thread {
            try {
                val clientId = "RedmiA3_GhostLock_${System.currentTimeMillis()}"
                mqttClient = MqttClient(brokerUri, clientId, MemoryPersistence())
                val options = MqttConnectOptions().apply {
                    isCleanSession = true
                    connectionTimeout = 10
                    keepAliveInterval = 30
                }

                mqttClient?.setCallback(object : MqttCallback {
                    override fun connectionLost(cause: Throwable?) {
                        mainHandler.post {
                            binding.tvCloudStatus.text = "CLOUD HORS LIGNE"
                            binding.tvCloudStatus.setTextColor(getColor(R.color.rose))
                        }
                        mainHandler.postDelayed({ connectMqtt() }, 5000)
                    }

                    override fun messageArrived(topic: String?, message: MqttMessage?) {
                        val currentTopic = topic ?: return
                        val payloadStr = message?.toString() ?: return
                        try {
                            val json = JSONObject(payloadStr)
                            val parts = currentTopic.split("/")
                            if (parts.size >= 3 && parts[0] == "ghost_lock" && parts[2] == "status") {
                                val pcName = parts[1]
                                val locked = json.optBoolean("locked", false)
                                val online = json.optBoolean("online", true)
                                val armed = json.optBoolean("armed", false)
                                val timeStr = json.optString("time_str", "")
                                val rssi = if (json.has("rssi") && !json.isNull("rssi")) json.optInt("rssi") else null

                                discoveredPcs[pcName] = DiscoveredPc(
                                    name = pcName,
                                    isOnline = online,
                                    isLocked = locked,
                                    lastSeen = System.currentTimeMillis(),
                                    timeStr = timeStr
                                )
                                GhostPrefs.addKnownPc(this@MainActivity, pcName)

                                mainHandler.post {
                                    updateDiscoveredCountUI()
                                    if (pcName.equals(targetPc, ignoreCase = true)) {
                                        if (online) {
                                            lastPcPacketTimestamp = System.currentTimeMillis()
                                            lastPcTimeStr = timeStr
                                        } else {
                                            lastPcPacketTimestamp = 0L
                                        }
                                        updatePcStatusUI(locked, timeStr, online, armed, rssi)
                                    }
                                }
                            }
                        } catch (e: Exception) {}
                    }

                    override fun deliveryComplete(token: IMqttDeliveryToken?) {}
                })

                mqttClient?.connect(options)
                mqttClient?.subscribe("ghost_lock/+/status", 1)
                mqttClient?.subscribe(topicStatus, 1)
                mqttClient?.subscribe(topicCmd, 1)
                mqttClient?.subscribe("ghost_lock/$targetPc/phone_stream/cmd", 1)

                // Demande immédiate d'état du PC
                try {
                    val req = JSONObject().apply {
                        put("action", "get_status")
                        put("device", "redmi_a3")
                        put("timestamp", System.currentTimeMillis())
                    }
                    mqttClient?.publish(topicCmd, MqttMessage(req.toString().toByteArray()).apply { qos = 1 })
                } catch (e: Exception) {}

                mainHandler.post {
                    binding.tvCloudStatus.text = "CLOUD CONNECTÉ"
                    binding.tvCloudStatus.setTextColor(getColor(R.color.emerald))
                    sendMqttProximityState(binding.switchProximity.isChecked)
                }
            } catch (e: Exception) {
                mainHandler.post {
                    binding.tvCloudStatus.text = "ERREUR CLOUD"
                    binding.tvCloudStatus.setTextColor(getColor(R.color.rose))
                }
                mainHandler.postDelayed({ connectMqtt() }, 5000)
            }
        }.start()
    }

    private fun updateDiscoveredCountUI() {
        val totalKnown = GhostPrefs.getKnownPcs(this).size
        val onlineCount = discoveredPcs.values.count { it.isOnline && (System.currentTimeMillis() - it.lastSeen < 60000) }
        binding.tvDiscoveredCount.text = when {
            onlineCount > 1 -> "🟢 $onlineCount PCs en ligne détectés • Toucher pour changer"
            onlineCount == 1 -> "🟢 1 PC en ligne • Toucher pour changer"
            else -> "$totalKnown PC(s) mémorisé(s) • Toucher pour changer"
        }
    }

    fun showPcSelectorDialog() {
        if (isFinishing || isDestroyed) return
        try {
            pcSelectorDialog?.dismiss()
        } catch (e: Exception) {}

        val dialog = Dialog(this)
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE)
        val dialogBinding = DialogSelectPcBinding.inflate(layoutInflater)
        dialog.setContentView(dialogBinding.root)

        dialog.window?.apply {
            setBackgroundDrawable(ColorDrawable(Color.TRANSPARENT))
            setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT)
        }

        var tempSelectedPc = targetPc
        dialogBinding.cbAlwaysAskStartup.isChecked = GhostPrefs.isAskOnStartup(this)

        fun refreshList() {
            dialogBinding.layoutPcContainer.removeAllViews()
            val allPcs = LinkedHashSet<String>()
            allPcs.add(targetPc)
            allPcs.addAll(discoveredPcs.keys)
            allPcs.addAll(GhostPrefs.getKnownPcs(this))

            for (pcName in allPcs) {
                val itemBinding = ItemPcChoiceBinding.inflate(layoutInflater, dialogBinding.layoutPcContainer, false)
                val isSelected = pcName.equals(tempSelectedPc, ignoreCase = true)
                val info = discoveredPcs[pcName]

                itemBinding.tvPcItemName.text = pcName

                val isOnline = info?.isOnline == true && (System.currentTimeMillis() - (info?.lastSeen ?: 0) < 60000)
                if (isOnline) {
                    val lockStateStr = if (info?.isLocked == true) "🔒 Verrouillé" else "🔓 Déverrouillé"
                    itemBinding.tvPcItemStatus.text = "🟢 En ligne • $lockStateStr"
                    itemBinding.tvPcItemStatus.setTextColor(ContextCompat.getColor(this, R.color.emerald))
                } else {
                    itemBinding.tvPcItemStatus.text = "⚪ Hors ligne / En attente"
                    itemBinding.tvPcItemStatus.setTextColor(ContextCompat.getColor(this, R.color.text_muted))
                }

                if (isSelected) {
                    itemBinding.layoutItemRoot.setBackgroundResource(R.drawable.bg_pc_item_selected)
                    itemBinding.tvPcItemCheck.visibility = View.VISIBLE
                    itemBinding.tvPcItemCheck.text = "ACTIF ✓"
                    itemBinding.tvPcItemCheck.setTextColor(Color.parseColor("#00F0FF"))
                } else {
                    itemBinding.layoutItemRoot.setBackgroundResource(R.drawable.bg_pc_item_normal)
                    itemBinding.tvPcItemCheck.visibility = View.VISIBLE
                    itemBinding.tvPcItemCheck.text = "Choisir"
                    itemBinding.tvPcItemCheck.setTextColor(ContextCompat.getColor(this, R.color.text_muted))
                }

                itemBinding.layoutItemRoot.setOnClickListener {
                    tempSelectedPc = pcName
                    refreshList()
                }

                dialogBinding.layoutPcContainer.addView(itemBinding.root)
            }
        }

        refreshList()

        dialogBinding.btnAddCustomPc.setOnClickListener {
            val input = dialogBinding.etCustomPcName.text.toString().trim().lowercase()
            if (input.isNotEmpty()) {
                GhostPrefs.addKnownPc(this, input)
                tempSelectedPc = input
                dialogBinding.etCustomPcName.text.clear()
                refreshList()
                Toast.makeText(this, "PC '$input' ajouté !", Toast.LENGTH_SHORT).show()
            }
        }

        dialogBinding.btnApplyPcSelection.setOnClickListener {
            GhostPrefs.setAskOnStartup(this, dialogBinding.cbAlwaysAskStartup.isChecked)
            if (tempSelectedPc.isNotEmpty() && !tempSelectedPc.equals(targetPc, ignoreCase = true)) {
                switchTargetPc(tempSelectedPc)
            }
            dialog.dismiss()
        }

        dialogBinding.btnClosePcDialog.setOnClickListener {
            GhostPrefs.setAskOnStartup(this, dialogBinding.cbAlwaysAskStartup.isChecked)
            dialog.dismiss()
        }

        pcSelectorDialog = dialog
        dialog.show()
    }

    fun switchTargetPc(newPc: String) {
        val clean = newPc.trim().lowercase()
        if (clean.isEmpty()) return

        val oldPc = targetPc
        targetPc = clean
        GhostPrefs.setSelectedPc(this, clean)

        topicStatus = "ghost_lock/$targetPc/status"
        topicCmd = "ghost_lock/$targetPc/cmd"
        topicHeartbeat = "ghost_lock/$targetPc/heartbeat"

        binding.tvPcName.text = "🖥️ $targetPc"
        binding.tvPcLiveStatus.text = "🟡 EN ATTENTE..."
        binding.tvPcLiveStatus.setTextColor(ContextCompat.getColor(this, R.color.text_muted))

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
                        client.subscribe("ghost_lock/$targetPc/phone_stream/cmd", 1)

                        val req = JSONObject().apply {
                            put("action", "get_status")
                            put("device", "redmi_a3")
                            put("timestamp", System.currentTimeMillis())
                        }
                        client.publish(topicCmd, MqttMessage(req.toString().toByteArray()).apply { qos = 1 })
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()

        try {
            val serviceIntent = Intent(this, GhostLockService::class.java).apply {
                action = "ACTION_CHANGE_TARGET_PC"
                putExtra("target_pc", clean)
            }
            startService(serviceIntent)
        } catch (e: Exception) {}

        try {
            if (PhoneStreamService.instance != null) {
                val streamIntent = Intent(this, PhoneStreamService::class.java).apply {
                    action = "ACTION_CHANGE_TARGET_PC"
                    putExtra("target_pc", clean)
                }
                startService(streamIntent)
            }
        } catch (e: Exception) {}

        updateDiscoveredCountUI()
        Toast.makeText(this, "Connecté à $targetPc", Toast.LENGTH_SHORT).show()
    }

    private fun animateUnlockSequence() {
        // 1. Onde de choc spatiale verte émeraude
        binding.radarShockwave.apply {
            setBackgroundResource(R.drawable.bg_radar_shockwave_emerald)
            scaleX = 0.8f
            scaleY = 0.8f
            alpha = 1.0f
            animate()
                .scaleX(2.3f)
                .scaleY(2.3f)
                .alpha(0.0f)
                .setDuration(650)
                .setInterpolator(DecelerateInterpolator())
                .start()
        }

        // 2. Le cadenas s'ouvre avec rebond dynamique SF Symbols
        binding.ivLockIcon.animate()
            .scaleX(1.32f)
            .scaleY(1.32f)
            .setDuration(160)
            .withEndAction {
                binding.ivLockIcon.setImageResource(R.drawable.ic_padlock_unlocked)
                binding.ivLockIcon.setColorFilter(getColor(R.color.emerald))
                binding.hubBiometric.setBackgroundResource(R.drawable.bg_biometric_hub_unlocked)

                binding.ivLockIcon.animate()
                    .scaleX(1.0f)
                    .scaleY(1.0f)
                    .setDuration(280)
                    .setInterpolator(OvershootInterpolator(2.2f))
                    .start()
            }
            .start()

        // 3. Transition fluide du texte de statut
        binding.tvLockStatus.apply {
            alpha = 0f
            translationY = 12f
            text = "PC ACTUELLEMENT DÉVERROUILLÉ 🔓"
            setTextColor(getColor(R.color.emerald))
            animate()
                .alpha(1f)
                .translationY(0f)
                .setDuration(300)
                .setInterpolator(DecelerateInterpolator())
                .start()
        }
    }

    private fun animateLockSequence() {
        // 1. Onde de choc spatiale rose néon
        binding.radarShockwave.apply {
            setBackgroundResource(R.drawable.bg_radar_shockwave_rose)
            scaleX = 0.8f
            scaleY = 0.8f
            alpha = 1.0f
            animate()
                .scaleX(2.1f)
                .scaleY(2.1f)
                .alpha(0.0f)
                .setDuration(550)
                .setInterpolator(DecelerateInterpolator())
                .start()
        }

        // 2. Le cadenas se comprime et claque fermement (snap mécanique)
        binding.ivLockIcon.animate()
            .scaleX(0.82f)
            .scaleY(0.82f)
            .setDuration(140)
            .withEndAction {
                binding.ivLockIcon.setImageResource(R.drawable.ic_padlock_locked)
                binding.ivLockIcon.setColorFilter(getColor(R.color.rose))
                binding.hubBiometric.setBackgroundResource(R.drawable.bg_biometric_hub_locked)

                binding.ivLockIcon.animate()
                    .scaleX(1.0f)
                    .scaleY(1.0f)
                    .setDuration(240)
                    .setInterpolator(OvershootInterpolator(1.8f))
                    .start()
            }
            .start()

        // 3. Transition fluide du texte de statut
        binding.tvLockStatus.apply {
            alpha = 0f
            translationY = -12f
            text = "PC ACTUELLEMENT VERROUILLÉ 🔒"
            setTextColor(getColor(R.color.rose))
            animate()
                .alpha(1f)
                .translationY(0f)
                .setDuration(300)
                .setInterpolator(DecelerateInterpolator())
                .start()
        }
    }

    private fun updatePcStatusUI(locked: Boolean, timeStr: String, online: Boolean, armed: Boolean = false, rssi: Int? = null) {
        val wasLocked = isPcLocked
        val stateChanged = (wasLocked != locked)
        val armedChanged = (isAutoLockArmed != armed)
        isPcLocked = locked
        isAutoLockArmed = armed

        if (stateChanged) {
            if (locked) {
                animateLockSequence()
                if (online) vibratePhone()
            } else {
                animateUnlockSequence()
                if (online) vibratePhone()
            }
        } else {
            if (locked) {
                binding.ivLockIcon.setImageResource(R.drawable.ic_padlock_locked)
                binding.ivLockIcon.setColorFilter(getColor(R.color.rose))
                binding.hubBiometric.setBackgroundResource(R.drawable.bg_biometric_hub_locked)
                binding.tvLockStatus.text = "PC ACTUELLEMENT VERROUILLÉ 🔒"
                binding.tvLockStatus.setTextColor(getColor(R.color.rose))
            } else {
                binding.ivLockIcon.setImageResource(R.drawable.ic_padlock_unlocked)
                binding.ivLockIcon.setColorFilter(getColor(R.color.emerald))
                binding.hubBiometric.setBackgroundResource(R.drawable.bg_biometric_hub_unlocked)
                binding.tvLockStatus.text = "PC ACTUELLEMENT DÉVERROUILLÉ 🔓"
                binding.tvLockStatus.setTextColor(getColor(R.color.emerald))
            }
        }

        if (online && timeStr.isNotEmpty()) {
            if (locked) {
                binding.tvLastSeen.text = "🔒 PC Verrouillé • $timeStr"
            } else {
                if (armed) {
                    val rssiInfo = if (rssi != null && rssi != 0) " ($rssi dBm)" else ""
                    binding.tvLastSeen.text = "🛡️ Auto-verrouillage : RÉARMÉ • Près du PC$rssiInfo"
                } else {
                    binding.tvLastSeen.text = "📡 Auto-verrouillage en pause • Approchez-vous pour réactiver"
                }
            }
        }

        if (armedChanged && !locked) {
            if (armed) {
                binding.tvLogs.text = "✅ Signal proche détecté : Le système de verrouillage à l'éloignement est RÉARMÉ !"
            }
        }
    }


    private fun startPcWatchdogLoop() {
        mainHandler.post(object : Runnable {
            override fun run() {
                val now = System.currentTimeMillis()
                val isLive = lastPcPacketTimestamp > 0 && (now - lastPcPacketTimestamp) < 7000
                if (!isLive) {
                    binding.tvPcLiveStatus.text = "🔴 PC HORS LIGNE (Inactif)"
                    binding.tvPcLiveStatus.setTextColor(getColor(R.color.rose))
                    if (lastPcPacketTimestamp == 0L) {
                        binding.tvLastSeen.text = "⚠️ En attente du script sur le PC..."
                    } else {
                        val elapsedSec = (now - lastPcPacketTimestamp) / 1000
                        binding.tvLastSeen.text = "⚠️ Inactif depuis ${elapsedSec}s (Dernier: $lastPcTimeStr)"
                    }
                } else {
                    binding.tvPcLiveStatus.text = "🟢 PC EN LIGNE & PRÊT"
                    binding.tvPcLiveStatus.setTextColor(getColor(R.color.emerald))
                }
                mainHandler.postDelayed(this, 1000)
            }
        })
    }

    private fun sendMqttCommand(action: String) {
        Thread {
            try {
                if (mqttClient?.isConnected == true) {
                    val json = JSONObject().apply {
                        put("action", action)
                        put("device", "redmi_a3")
                        put("timestamp", System.currentTimeMillis())
                    }
                    val msg = MqttMessage(json.toString().toByteArray()).apply { qos = 1 }
                    mqttClient?.publish(topicCmd, msg)
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
    }

    private fun sendMqttProximityState(enabled: Boolean) {
        Thread {
            try {
                if (mqttClient?.isConnected == true) {
                    val json = JSONObject().apply {
                        put("action", "set_auto_lock")
                        put("enabled", enabled)
                        put("device", "redmi_a3")
                        put("timestamp", System.currentTimeMillis())
                    }
                    val msg = MqttMessage(json.toString().toByteArray()).apply { qos = 1 }
                    mqttClient?.publish(topicCmd, msg)
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }.start()
    }

    private fun startHeartbeatLoop() {
        mainHandler.post(object : Runnable {
            override fun run() {
                if (proximityRunning && mqttClient?.isConnected == true) {
                    Thread {
                        try {
                            val json = JSONObject().apply {
                                put("action", "heartbeat")
                                put("device", "redmi_a3")
                                put("timestamp", System.currentTimeMillis())
                            }
                            mqttClient?.publish(topicHeartbeat, MqttMessage(json.toString().toByteArray()).apply { qos = 0 })
                        } catch (e: Exception) {}
                    }.start()
                }
                mainHandler.postDelayed(this, 4000)
            }
        })
    }

    private fun vibratePhone() {
        val vibrator = getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(VibrationEffect.createOneShot(80, VibrationEffect.DEFAULT_AMPLITUDE))
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(80)
        }
    }

    private fun startCameraStreaming(lensFacing: Int) {
        val action = if (lensFacing == CameraCharacteristics.LENS_FACING_FRONT) "START_CAMERA_FRONT" else "START_CAMERA_BACK"
        val serviceIntent = Intent(this, PhoneStreamService::class.java).apply {
            this.action = action
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent)
        } else {
            startService(serviceIntent)
        }
        val mode = if (lensFacing == CameraCharacteristics.LENS_FACING_FRONT) "camera_front" else "camera_back"
        updateStreamUi(mode, true)
        binding.tvLogs.text = "📷 Diffusion caméra en cours vers le PC"
        Toast.makeText(this, "Caméra en direct sur le PC !", Toast.LENGTH_SHORT).show()
    }

    private fun stopPhoneStream() {
        val serviceIntent = Intent(this, PhoneStreamService::class.java).apply {
            action = "STOP"
        }
        startService(serviceIntent)
        updateStreamUi("idle", false)
        binding.tvLogs.text = "⏹ Diffusion arrêtée."
        Toast.makeText(this, "Diffusion arrêtée", Toast.LENGTH_SHORT).show()
    }

    private fun updateStreamUi(mode: String, isActive: Boolean) {
        val ip = PhoneStreamService.phoneIp
        val port = PhoneStreamService.SERVER_PORT
        binding.tvStreamIp.text = "$ip:$port"

        if (isActive) {
            window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
            binding.btnStopStream.visibility = android.view.View.VISIBLE
            when (mode) {
                "screen" -> {
                    binding.tvStreamStatus.text = "📱 Écran en direct sur le PC"
                    binding.tvStreamStatus.setTextColor(ContextCompat.getColor(this, R.color.emerald))
                }
                "camera_front" -> {
                    binding.tvStreamStatus.text = "📷 Caméra Avant en direct"
                    binding.tvStreamStatus.setTextColor(ContextCompat.getColor(this, R.color.emerald))
                }
                else -> {
                    binding.tvStreamStatus.text = "📷 Caméra Arrière en direct"
                    binding.tvStreamStatus.setTextColor(ContextCompat.getColor(this, R.color.emerald))
                }
            }
        } else {
            window.clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
            binding.btnStopStream.visibility = android.view.View.GONE
            binding.tvStreamStatus.text = "Inactif • Prêt à diffuser"
            binding.tvStreamStatus.setTextColor(ContextCompat.getColor(this, R.color.text_secondary))
        }
    }

    override fun onResume() {
        super.onResume()
        if (binding.switchProximity.isChecked && !isAdvertising) {
            checkAndStartBleBeacon()
        }
        updateStreamUi(PhoneStreamService.activeMode, PhoneStreamService.isStreamingActive)
    }

    override fun onDestroy() {
        super.onDestroy()
        stopBleBeacon()
        try {
            pcSelectorDialog?.dismiss()
            pcSelectorDialog = null
        } catch (e: Exception) {}
        try {
            if (keepScreenReceiver != null) {
                unregisterReceiver(keepScreenReceiver)
                keepScreenReceiver = null
            }
        } catch (e: Exception) {}
        try {
            mqttClient?.disconnect()
        } catch (e: Exception) {}
    }
}
