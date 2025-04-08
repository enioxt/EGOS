"""
BIOS-Q: Script de Inicialização do Cursor
Executa automaticamente quando o Cursor é aberto no projeto EVA & GUARANI
Integra o prompt quântico com o sistema BIOS-Q
"""

import json
import os
import subprocess
from pathlib import Path

# Caminhos principais
BIOS_Q_SCRIPT = "core/bios_quantum.py"
QUANTUM_PROMPT = "QUANTUM_PROMPTS/core_principles.md"
SETTINGS_PATH = ".cursor/settings.json"
CONFIG_PATH = "config/ethik_chain_core.yaml"
CHANGELOG_SCRIPT = "core/quantum_changelog.py"
CHANGELOG_FILE = "staging/quantum_changelog.json"


def initialize_cursor_environment():
    """Inicializa o ambiente do Cursor com BIOS-Q e integra o prompt quântico"""
    print("\n✧༺❀༻∞ EVA & GUARANI - Inicializando Ambiente Quântico ∞༺❀༻✧\n")

    # Verificar se o prompt quântico existe
    check_quantum_prompt()

    # Carregar configurações do Cursor
    settings = load_cursor_settings()

    # Verificar se devemos executar o BIOS-Q
    if settings and settings.get("onStartup", {}).get("runScript"):
        script_path = settings["onStartup"]["runScript"]
        print(f"🚀 Executando BIOS-Q: {script_path}")

        # Executar BIOS-Q como processo em background
        try:
            if os.name == "nt":  # Windows
                subprocess.Popen(
                    ["python", script_path], creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:  # Unix/Linux/Mac
                subprocess.Popen(
                    ["python3", script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True,
                )
            print("✅ BIOS-Q inicializado com sucesso")
        except Exception as e:
            print(f"⚠️ Erro ao iniciar BIOS-Q: {str(e)}")

    # Verificar sistema de Changelog Quântico
    check_quantum_changelog()

    print("\n✧༺❀༻∞ EVA & GUARANI - Ambiente Quântico Inicializado ∞༺❀༻✧\n")


def check_quantum_prompt():
    """Verifica se o prompt quântico existe e se está integrado ao BIOS-Q"""
    if os.path.exists(QUANTUM_PROMPT):
        print(f"✅ Prompt Quântico encontrado em {QUANTUM_PROMPT}")

        # Verificar se o BIOS-Q está configurado para usar o prompt quântico
        if os.path.exists(CONFIG_PATH):
            try:
                import yaml

                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)

                if (
                    config
                    and config.get("system", {}).get("core_principles_file") == QUANTUM_PROMPT
                ):
                    print("✅ BIOS-Q configurado para usar o Prompt Quântico")
                else:
                    print("⚠️ BIOS-Q não está configurado para usar o Prompt Quântico correto")
                    # Atualizar o caminho do prompt quântico no config
                    if config and "system" in config:
                        config["system"]["core_principles_file"] = QUANTUM_PROMPT
                        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                            yaml.dump(config, f, sort_keys=False, default_flow_style=False)
                        print("✅ Configuração do BIOS-Q atualizada para usar o Prompt Quântico")
            except Exception as e:
                print(f"⚠️ Erro ao verificar configuração do BIOS-Q: {str(e)}")
    else:
        print(f"⚠️ Prompt Quântico não encontrado em {QUANTUM_PROMPT}")
        # Verificar pastas QUANTUM_PROMPTS para encontrar o prompt
        prompts_dir = Path("QUANTUM_PROMPTS")
        if prompts_dir.exists() and prompts_dir.is_dir():
            md_files = list(prompts_dir.glob("*.md"))
            if md_files:
                print(f"🔍 Encontrados {len(md_files)} arquivos markdown em QUANTUM_PROMPTS:")
                for md_file in md_files:
                    print(f"   - {md_file}")


def check_quantum_changelog():
    """Verifica o sistema de Changelog Quântico e exibe status"""
    if os.path.exists(CHANGELOG_SCRIPT):
        print(f"✅ Sistema de Changelog Quântico encontrado em {CHANGELOG_SCRIPT}")

        # Verificar se há entradas pendentes
        if os.path.exists(CHANGELOG_FILE):
            try:
                with open(CHANGELOG_FILE, "r", encoding="utf-8") as f:
                    changelog_data = json.load(f)

                pending_count = len(changelog_data.get("pending_review", []))
                approved_count = len(changelog_data.get("entries", []))

                if pending_count > 0:
                    print(f"ℹ️ {pending_count} entradas de progresso pendentes de revisão")
                    print(
                        "   Use 'python core/quantum_changelog.py' e selecione a opção 2 para revisar"
                    )

                print(f"ℹ️ {approved_count} progressos aprovados no total")

                # Verificar última atualização
                last_updated = changelog_data.get("last_updated", "")
                if last_updated:
                    print(f"ℹ️ Última atualização: {last_updated}")
            except Exception as e:
                print(f"⚠️ Erro ao verificar changelog: {str(e)}")
    else:
        print("ℹ️ Sistema de Changelog Quântico não encontrado")
        print("   Considere criar 'core/quantum_changelog.py' para registrar progressos")


def load_cursor_settings():
    """Carrega as configurações do Cursor"""
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                settings = json.load(f)
            print(f"✅ Configurações do Cursor carregadas de {SETTINGS_PATH}")
            return settings
        except Exception as e:
            print(f"⚠️ Erro ao carregar configurações do Cursor: {str(e)}")
    else:
        print(f"⚠️ Arquivo de configurações do Cursor não encontrado em {SETTINGS_PATH}")
        # Criar arquivo de configurações padrão
        default_settings = {
            "onStartup": {"runScript": BIOS_Q_SCRIPT, "showBiosQ": True},
            "biosQ": {"autoUpdate": True, "updateInterval": "daily", "showOnStartup": True},
            "ui": {"showStatusInSidebar": True, "roadmapVisualization": "timeline"},
            "project": {
                "name": "EVA & GUARANI - EGOS",
                "description": "Sistema Quântico com Ética Integrada",
            },
            "quantumChangelog": {"autoScan": True, "scanInterval": "daily", "notifyPending": True},
        }

        try:
            os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(default_settings, f, indent=4)
            print(f"✅ Arquivo de configurações do Cursor criado em {SETTINGS_PATH}")
            return default_settings
        except Exception as e:
            print(f"⚠️ Erro ao criar arquivo de configurações do Cursor: {str(e)}")

    return None


# Executar inicialização quando o script é carregado
if __name__ == "__main__":
    initialize_cursor_environment()
