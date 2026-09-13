# 🛡️ GHOST PROTOCOL • PC LOCK & STREAM VIEWER (VISION PRO HUD)

> **Système complet de contrôle à distance, verrouillage biométrique PC et streaming temps-réel Android (Xiaomi Redmi A3 / Vision Pro)**

![Ghost Protocol](https://img.shields.io/badge/Ghost-Protocol%20v2.0-00f0ff?style=for-the-badge)
![Android](https://img.shields.io/badge/Android-Go%20Edition-34a853?style=for-the-badge&logo=android)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python)
![MQTT](https://img.shields.io/badge/MQTT-HiveMQ%20Cloud-orange?style=for-the-badge)

---

## 🌟 Fonctionnalités Principales

### 1. 👁️ Phone Stream Viewer (`phone_viewer.py` & `phone_viewer.html`)
- **Diffusion Écran & Caméra** : Réception du flux MJPEG haute performance et basse latence depuis le téléphone Android.
- **Bascule Instantanée** : Commutateur fluide entre Écran, Caméra Arrière et Caméra Frontale.
- **Anti-Veille Téléphone (Keep-Awake)** : Maintien de l'écran allumé à distance via MQTT.
- **Capture Photo Instantanée** : Sauvegarde des clichés en pleine résolution dans le dossier `captures/`.
- **Notifications & Alertes HUD PC vers Téléphone** : Envoi de messages personnalisés déclenchant un réveil de l'écran avec une carte holographique futuriste style Apple Vision Pro.

### 2. 📱 Application Android (`android_lock_app` / `GhostLock_VisionPro_RedmiA3.apk`)
- **Optimisée pour Xiaomi Redmi A3** (Android Go Edition).
- **Service en arrière-plan 24/7** (`GhostLockService`) résistant aux optimisations de batterie.
- **Streaming matériel** (`PhoneStreamService`) basé sur MediaProjection et CameraX.
- **Carte HUD Flottante** (`GhostAlertActivity`) : Réveille le téléphone même s'il est verrouillé (`setShowWhenLocked` & `setTurnScreenOn`), fait vibrer l'appareil avec un motif triple haptique et affiche le message avec des boutons d'action rapide.
- **Notification personnalisée RemoteViews** avec bannière Heads-Up néon cyan.

### 3. 🔒 Bouclier de Verrouillage PC (`pc_lock_shield.py` & `lock_ui.html`)
- **Interface Floue Spatial Vision Pro** : Défloutage cinématique ultra-fluide.
- **Déverrouillage Biométrique Proximité Bluetooth (BLE)** : Déverrouille automatiquement le PC à l'approche de votre téléphone.
- **Code PIN de secours discret** : Modal de déverrouillage manuel intégré (`Ctrl + Shift + Alt + U`).
- **Verrouillage total** des entrées (clavier, gestionnaire de tâches, barre des tâches).

### 4. 🌐 Web Viewer Centralisé (`ghost_web_viewer.html` & `ghost_viewer.py`)
- Tableau de bord multi-appareils affichant l'état en direct et le statut des machines connectées.
- Détection automatique de présence et filtres d'appareils actifs.

---

## 📦 Structure du Répertoire

```text
├── GhostLock_VisionPro_RedmiA3.apk    # APK Android prêt à installer
├── app-debug.apk                      # APK Android (version debug)
├── phone_viewer.py                    # Viewer PC pour le stream et les notifs
├── phone_viewer.html                  # Interface futuriste Vision Pro du viewer
├── pc_lock_shield.py                  # Bouclier de verrouillage Windows BLE / MQTT
├── lock_ui.html                       # Interface cinématique de déverrouillage
├── ghost_script.py                    # Moteur d'effets et agent client
├── ghost_script.exe                   # Exécutable compilé du script client
├── ghost_web_viewer.html              # Tableau de bord web des appareils actifs
├── ghost_viewer.py                    # Contrôleur opérateur multi-cibles
├── android_lock_app/                  # Code source complet du projet Android Studio
│   ├── app/src/main/java/             # Code Kotlin (Services, Activities)
│   └── app/src/main/res/              # Layouts XML, Drawables, Styles HUD
├── captures/                          # Dossier de sauvegarde des captures d'écran
└── assets/                            # Spritesheets et ressources graphiques
```

---

## 🚀 Démarrage Rapide

### Sur le Téléphone Android (Redmi A3)
1. Téléchargez et installez `GhostLock_VisionPro_RedmiA3.apk` sur votre smartphone.
2. Ouvrez l'application et accordez les autorisations nécessaires (Affichage par-dessus les autres applis, Notifications, Économiseur de batterie sans restriction).
3. Cliquez sur **« Démarrer le Service »**.

### Sur le PC Windows
1. Installez les dépendances Python :
   ```bash
   pip install pywebview paho-mqtt pillow bleak
   ```
2. Lancer le Viewer du téléphone :
   ```bash
   python phone_viewer.py
   # Ou double-cliquez sur lancer_phone_viewer.bat
   ```
3. Lancer le Bouclier de Verrouillage :
   ```bash
   python pc_lock_shield.py
   # Ou double-cliquez sur start_pc_lock.bat
   ```

---

## ⚡ Licence & Sécurité
Ce projet est conçu pour un usage personnel de contrôle, de productivité et d'automatisation d'appareils personnels.
Développé avec ❤️ par **zakrievahmed129** & Antigravity AI.
