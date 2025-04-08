"""
Translation utilities for the EGOS Dashboard.
Contains the translation dictionary and helper function for internationalization.
"""

import streamlit as st

# Dictionary of translations for multiple languages
TRANSLATIONS = {
    "en": {
        # --- General UI ---
        "title": "☸️ EGOS - Ecosystem Monitoring",
        "last_updated": "Last updated:",
        "language_select": "Select Language:",
        "resources": "**Resources:**",
        "view_source_code": "- [View Source Code (GitHub)]",
        "connect_live_data": "Connect to Live Data",
        "nats_status_label": "NATS Status:",
        "nats_status_disconnected": "Disconnected",
        "nats_status_connecting": "Connecting...",
        "nats_status_connected": "Connected",
        "nats_status_error": "Error",
        "nats_status_closed": "Connection Closed",
        "waiting_live_status": "Waiting for live subsystem status updates via NATS...",
        # --- Overview Section ---
        "overview_header": "📊 System Overview",
        "active_tasks": "⚙️ Active Tasks",
        "active_tasks_help": "Number of processes or tasks actively running in the system.",
        "mycelium_messages": "✉️ Mycelium Messages",
        "mycelium_messages_help": "Total messages exchanged on the Mycelium network since startup.",
        "average_load": "🌡️ Average Load",
        "average_load_help": "Estimated average computational load across the system.",
        "active_ai_models": "🤖 Active AI Models",
        "active_ai_models_help": "Number of AI models loaded and ready for use (CORUJA).",
        "subsystem_status_header": "📡 Subsystem Status",
        "subsystem_col": "Subsystem",
        "status_col": "Status",
        "last_heartbeat_col": "Last Heartbeat",
        "key_metrics": "Key Metrics",
    },
    "pt": {
        # --- General UI ---
        "title": "☸️ EGOS - Monitoramento do Ecossistema",
        "last_updated": "Última atualização:",
        "language_select": "Selecione o Idioma:",
        "resources": "**Recursos:**",
        "view_source_code": "- [Ver Código Fonte (GitHub)]",
        "connect_live_data": "Conectar aos Dados ao Vivo",
        "nats_status_label": "Status NATS:",
        "nats_status_disconnected": "Desconectado",
        "nats_status_connecting": "Conectando...",
        "nats_status_connected": "Conectado",
        "nats_status_error": "Erro",
        "nats_status_closed": "Conexão Fechada",
        "waiting_live_status": "Aguardando atualizações de status dos subsistemas via NATS...",
        # --- Overview Section ---
        "overview_header": "📊 Visão Geral do Sistema",
        "active_tasks": "⚙️ Tarefas Ativas",
        "active_tasks_help": "Número de processos ou tarefas sendo executadas "
        "ativamente no sistema.",
        "mycelium_messages": "✉️ Mensagens (Mycelium)",
        "mycelium_messages_help": "Total de mensagens trocadas na rede Mycelium desde o início.",
        "average_load": "🌡️ Carga Média",
        "average_load_help": "Estimativa da carga computacional média do sistema.",
        "active_ai_models": "🤖 Modelos IA Ativos",
        "active_ai_models_help": "Número de modelos de IA carregados e prontos para uso (CORUJA).",
        "subsystem_status_header": "📡 Status dos Subsistemas",
        "subsystem_col": "Subsistema",
        "status_col": "Status",
        "last_heartbeat_col": "Último Heartbeat",
        "key_metrics": "Métricas Principais",
    },
}


def get_translation(key):
    """
    Get translated text for the given key based on current language in session state.
    Falls back to English if translation not found, then to the key itself.

    Args:
        key: The translation key to look up

    Returns:
        The translated string
    """
    # Fallback logic: Try English if key not found in current language, then show key name
    translation = TRANSLATIONS.get(st.session_state.lang, {}).get(key)
    if translation is None:
        translation = TRANSLATIONS.get("en", {}).get(key)
        if translation is None:
            return f"<Key: {key}>"  # Key not found anywhere
    return translation


# Alias for shorter notation
_ = get_translation
