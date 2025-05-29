import json
import os
from utils import logger

ARQUIVO_CONFIG = "config.json"

CONFIG_PADRAO = {
    "default_path": "C:/downloads",
    "audio_quality": "320",  # Opções: "128", "192", "320"
    "theme": "dark",  # Opções: "dark", "light"
    "video_format": "mp4",  # Opções: "mp4", "mkv"
    "video_quality": "720p",  # Opções: "360p", "480p", "720p", "1080p"
    "apply_metadata": True,
    "save_thumbnails": True
}

APP_VERSION = "1.1.0"  # Versão do aplicativo

# Informações do repositório para o updater
REPO_INFO = {
    "owner": "GuilllasDefas",  # Substitua pelo seu usuário do GitHub
    "name": "YT-Downloader"  # Substitua pelo nome do seu repositório
}

def carregar_config():
    """Carrega configurações do arquivo ou retorna padrões."""
    try:
        if os.path.exists(ARQUIVO_CONFIG):
            with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
                config = json.load(f)
                
                # Garantir que todas as chaves padrão existam
                for key, value in CONFIG_PADRAO.items():
                    if key not in config:
                        config[key] = value
                
                return config
        return CONFIG_PADRAO.copy()
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {str(e)}")
        return CONFIG_PADRAO.copy()

def salvar_config(data):
    """Salva configurações no arquivo."""
    try:
        with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar configurações: {str(e)}")
        return False

def obter_valor_config(key, default=None):
    """Recupera um valor específico das configurações."""
    config = carregar_config()
    return config.get(key, default)

def atualizar_valor_config(key, value):
    """Atualiza um valor específico nas configurações."""
    config = carregar_config()
    config[key] = value
    return salvar_config(config)

def redefinir_para_padrao():
    """Redefine configurações para os valores padrão."""
    return salvar_config(CONFIG_PADRAO.copy())

def get_app_version():
    """Retorna a versão atual do aplicativo."""
    return APP_VERSION

def get_repo_info():
    """Retorna informações do repositório para o updater."""
    return REPO_INFO.copy()
