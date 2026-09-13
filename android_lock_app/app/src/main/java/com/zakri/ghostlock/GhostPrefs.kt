package com.zakri.ghostlock

import android.content.Context
import android.content.SharedPreferences

/**
 * Gestionnaire de préférences Ghost Protocol.
 * Mémorise le PC cible actif, la liste des machines connues/découvertes,
 * et l'option d'ouverture automatique du sélecteur au démarrage.
 */
object GhostPrefs {
    private const val PREFS_NAME = "ghost_lock_prefs"
    private const val KEY_TARGET_PC = "target_pc"
    private const val KEY_KNOWN_PCS = "known_pcs"
    private const val KEY_ASK_ON_STARTUP = "ask_on_startup"

    const val DEFAULT_PC = "pc-zakriev"

    private fun getPrefs(context: Context): SharedPreferences {
        return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }

    fun getSelectedPc(context: Context): String {
        return getPrefs(context).getString(KEY_TARGET_PC, DEFAULT_PC) ?: DEFAULT_PC
    }

    fun setSelectedPc(context: Context, pc: String) {
        val clean = pc.trim().lowercase()
        if (clean.isNotEmpty()) {
            getPrefs(context).edit().putString(KEY_TARGET_PC, clean).apply()
            addKnownPc(context, clean)
        }
    }

    fun getKnownPcs(context: Context): Set<String> {
        val set = getPrefs(context).getStringSet(KEY_KNOWN_PCS, null)
        val result = LinkedHashSet<String>()
        result.add(DEFAULT_PC)
        if (set != null) {
            result.addAll(set)
        }
        return result
    }

    fun addKnownPc(context: Context, pc: String) {
        val clean = pc.trim().lowercase()
        if (clean.isNotEmpty()) {
            val current = LinkedHashSet(getKnownPcs(context))
            current.add(clean)
            getPrefs(context).edit().putStringSet(KEY_KNOWN_PCS, current).apply()
        }
    }

    fun removeKnownPc(context: Context, pc: String) {
        val clean = pc.trim().lowercase()
        val current = LinkedHashSet(getKnownPcs(context))
        current.remove(clean)
        if (current.isEmpty()) {
            current.add(DEFAULT_PC)
        }
        getPrefs(context).edit().putStringSet(KEY_KNOWN_PCS, current).apply()
        if (getSelectedPc(context) == clean) {
            setSelectedPc(context, current.first())
        }
    }

    fun isAskOnStartup(context: Context): Boolean {
        return getPrefs(context).getBoolean(KEY_ASK_ON_STARTUP, true)
    }

    fun setAskOnStartup(context: Context, ask: Boolean) {
        getPrefs(context).edit().putBoolean(KEY_ASK_ON_STARTUP, ask).apply()
    }
}
