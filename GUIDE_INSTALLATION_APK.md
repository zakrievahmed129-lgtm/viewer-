# 🛡️ GhostLock — Guide d'utilisation & Compilation APK (Redmi A3)

GhostLock sécurise votre ordinateur en empêchant quiconque d'accéder à votre session (même s'ils ont votre mot de passe Windows), en exigeant une **validation biométrique par empreinte digitale sur votre Redmi A3**.

---

## 🚀 1. Compiler l'APK sur Android Studio

Vous disposez déjà d'**Android Studio** installé sur votre PC. Le projet est entièrement configuré dans le dossier `android_lock_app/`.

### Étape 1 : Ouvrir le projet
- Double-cliquez simplement sur le fichier **[open_android_studio.bat](file:///c:/Users/zakri/Desktop/les%20animations%20doivent%20etres%20incroyables/open_android_studio.bat)** sur votre PC.
- *Ou dans Android Studio :* `File > Open...` et sélectionnez le dossier `android_lock_app`.

### Étape 2 : Générer l'APK
1. Laissez Android Studio synchroniser Gradle (quelques secondes).
2. Dans la barre de menu en haut, cliquez sur :
   **`Build > Build Bundle(s) / APK(s) > Build APK(s)`**
3. Dès que la compilation se termine, une petite notification apparaît en bas à droite :
   Cliquez sur **« locate »** pour ouvrir le dossier contenant le fichier `app-debug.apk`.

### Étape 3 : Installer sur votre Redmi A3
- Transférez `app-debug.apk` sur votre Redmi A3 (par câble USB, Google Drive, Bluetooth ou Telegram).
- Ouvrez le fichier sur votre téléphone et appuyez sur **Installer**.
- Ouvrez l'application **GhostLock**.

---

## 🔒 2. Comment utiliser le Verrouillage sur votre PC

### Démarrer la protection :
- Double-cliquez sur **[start_pc_lock.bat](file:///c:/Users/zakri/Desktop/les%20animations%20doivent%20etres%20incroyables/start_pc_lock.bat)**.
- L'écran devient instantanément noir avec le bouclier cybernétique : **« ACCÈS PC VERROUILLÉ »**.
- La barre des tâches, le clavier (Alt+Tab, Touche Windows) et le Gestionnaire des tâches sont verrouillés.
- **Discrétion totale** : **AUCUN** bouton ni texte de code secret n'est affiché à l'écran. N'importe qui voyant l'écran pensera qu'il est impossible de déverrouiller sans votre empreinte.

### Déverrouiller avec votre Redmi A3 :
1. Dès que votre PC est verrouillé, ouvrez l'application **GhostLock** sur votre téléphone.
2. La boîte de dialogue officielle Google apparaît immédiatement :
   *« Déverrouiller Pc-Zakriev — Posez votre doigt sur le capteur »*.
3. Posez votre doigt sur le **capteur d'empreinte latéral de votre Redmi A3**.
4. Le téléphone vibre et le PC se déverrouille **instantanément** !

---

## 🏃‍♂️ 3. Auto-Verrouillage par Distance Bluetooth RSSI (Tout en gardant le signal !)

- **Comment ça marche sans couper le signal ?**
  1. Votre **Redmi A3** émet une balise Bluetooth Low Energy (BLE) sécurisée.
  2. Le PC mesure en direct la **puissance du signal (RSSI en dBm)** :
     - **Devant le bureau (< 2 mètres)** : Signal fort (> -70 dBm) -> Le PC reste ouvert.
     - **Vous vous éloignez (3-5 mètres ou pièce voisine)** : Le signal faiblit (< -74 dBm) -> **Le PC se VERROUILLE automatiquement !**
  3. **Le signal n'est JAMAIS coupé** : La connexion Cloud MQTT / Internet reste 100% active. Vous recevez la notification sur votre téléphone et pouvez déverrouiller avec votre empreinte même depuis l'autre pièce !

---

## 🤫 4. Raccourci secret & Code PIN discret (En cas de téléphone déchargé)

Si votre Redmi A3 n'a plus de batterie, vous pouvez déverrouiller votre PC discrètement :
1. Sur le clavier de votre PC, faites la combinaison de touches secrète :
   **`Ctrl + Shift + Alt + U`**
2. Une petite boîte de dialogue discrète apparaît au centre.
3. Tapez votre code secret : **`1234`** (modifiable dans [pc_lock_shield.py](file:///c:/Users/zakri/Desktop/les%20animations%20doivent%20etres%20incroyables/pc_lock_shield.py)).
4. Appuyez sur Entrée : le PC est déverrouillé !
